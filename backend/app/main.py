"""应用入口：创建 FastAPI 应用、注册中间件与路由。

启动命令：
    uvicorn app.main:app --reload --port 8000
接口文档：
    http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import SessionLocal, init_db
from app.models import SysOperationLog, SysUser
from app.routers import (
    assets,
    attendances,
    auth,
    classes,
    courses,
    dashboard,
    departments,
    dorms,
    grades,
    logs,
    roles,
    schedules,
    scores,
    semesters,
    students,
    teachers,
    users,
)
from app.security import decode_access_token

# 请求路径前缀 → 功能模块名称，用于生成操作日志
MODULE_MAP: dict[str, str] = {
    "users": "用户管理",
    "roles": "角色管理",
    "logs": "日志管理",
    "departments": "部门管理",
    "grades": "年级管理",
    "classes": "班级管理",
    "semesters": "学期管理",
    "students": "学生学籍",
    "teachers": "教职工档案",
    "courses": "学科课程",
    "schedules": "排课管理",
    "scores": "成绩管理",
    "attendances": "考勤管理",
    "assets": "资产台账",
    "dorms": "宿舍管理",
    "dorm-rooms": "宿舍管理",
    "dorm-allocations": "住宿分配",
}

# 请求方法 → 操作类型
ACTION_MAP: dict[str, str] = {
    "POST": "新增",
    "PUT": "修改",
    "PATCH": "修改",
    "DELETE": "删除",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时自动建表。"""
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="面向小学、初中、高中学校的校园数据中心管理软件后端服务",
    lifespan=lifespan,
)

# 跨域配置：允许本地前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def record_operation_log(request: Request, call_next):
    """记录增删改操作到操作日志表。"""
    response = await call_next(request)

    method = request.method.upper()
    path = request.url.path
    action = ACTION_MAP.get(method)

    # 只记录接口路径下的写操作
    if action and path.startswith(settings.API_PREFIX) and response.status_code < 400:
        try:
            segments = [seg for seg in path.split("/") if seg]
            # 形如 /api/v1/students/12 → 取 "students"
            module_key = segments[2] if len(segments) > 2 else ""
            module = MODULE_MAP.get(module_key, module_key or "其他")

            user_id = None
            username = None
            real_name = None
            auth_header = request.headers.get("authorization", "")
            if auth_header.lower().startswith("bearer "):
                payload = decode_access_token(auth_header[7:])
                if payload:
                    user_id = int(payload.get("sub") or 0) or None
                    username = payload.get("username")

            db = SessionLocal()
            try:
                if user_id and username:
                    user_obj = db.get(SysUser, user_id)
                    real_name = user_obj.real_name if user_obj else None
                db.add(
                    SysOperationLog(
                        user_id=user_id,
                        username=username,
                        real_name=real_name,
                        module=module,
                        action=action,
                        method=method,
                        path=path,
                        ip=request.client.host if request.client else None,
                        detail=f"{action}{module}",
                        success=True,
                    )
                )
                db.commit()
            finally:
                db.close()
        except Exception:  # noqa: BLE001 日志记录失败不影响业务
            pass

    return response


@app.get("/", tags=["系统"], summary="服务状态")
def root():
    """服务根路径，用于确认服务已启动。"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
    }


@app.get(f"{settings.API_PREFIX}/health", tags=["系统"], summary="健康检查")
def health():
    """健康检查接口。"""
    return {"status": "ok"}


# 注册各业务模块路由
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(roles.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(logs.router, prefix=settings.API_PREFIX)
app.include_router(departments.router, prefix=settings.API_PREFIX)
app.include_router(grades.router, prefix=settings.API_PREFIX)
app.include_router(classes.router, prefix=settings.API_PREFIX)
app.include_router(semesters.router, prefix=settings.API_PREFIX)
app.include_router(students.router, prefix=settings.API_PREFIX)
app.include_router(teachers.router, prefix=settings.API_PREFIX)
app.include_router(courses.router, prefix=settings.API_PREFIX)
app.include_router(schedules.router, prefix=settings.API_PREFIX)
app.include_router(scores.router, prefix=settings.API_PREFIX)
app.include_router(attendances.router, prefix=settings.API_PREFIX)
app.include_router(assets.router, prefix=settings.API_PREFIX)
app.include_router(dorms.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
