"""认证路由：登录、获取当前用户、修改密码。"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models import SysLoginLog, SysUser
from app.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    MessageOut,
    UserProfile,
)
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["认证管理"])

# 各角色可访问的菜单编码
MENU_BY_ROLE: dict[str, list[str]] = {
    "admin": [
        "dashboard", "dashboard:screen", "dashboard:student", "dashboard:score",
        "dashboard:asset", "system:user", "system:role", "system:operation-log",
        "system:login-log", "base:department", "base:grade", "base:class",
        "base:semester", "base:student", "base:teacher", "edu:course",
        "edu:schedule", "edu:score", "edu:attendance", "af:asset", "af:dorm",
    ],
    "academic": [
        "dashboard", "dashboard:screen", "dashboard:student", "dashboard:score",
        "dashboard:asset", "base:department", "base:grade", "base:class",
        "base:semester", "base:student", "base:teacher", "edu:course",
        "edu:schedule", "edu:score", "edu:attendance",
    ],
    "head_teacher": [
        "dashboard", "dashboard:student", "dashboard:score", "base:grade",
        "base:class", "base:student", "base:semester", "edu:course",
        "edu:schedule", "edu:score", "edu:attendance",
    ],
    "subject_teacher": [
        "dashboard", "dashboard:score", "base:class", "base:student",
        "base:semester", "edu:course", "edu:schedule", "edu:score",
        "edu:attendance",
    ],
    "general_affairs": [
        "dashboard", "dashboard:asset", "base:department", "base:grade",
        "base:class", "base:teacher", "af:asset", "af:dorm",
    ],
}


def write_login_log(
    db: Session,
    username: str,
    request: Request,
    success: bool,
    message: str,
) -> None:
    """写入登录日志。"""
    log = SysLoginLog(
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=(request.headers.get("user-agent") or "")[:300],
        success=success,
        message=message,
    )
    db.add(log)
    db.commit()


def build_profile(user: SysUser) -> UserProfile:
    """把用户对象转换为返回用的用户信息。"""
    return UserProfile(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        role_id=user.role_id,
        role_name=user.role.name if user.role else "",
        role_code=user.role.code if user.role else "",
        teacher_id=user.teacher_id,
        phone=user.phone,
        email=user.email,
        status=user.status,
        last_login_at=user.last_login_at,
    )


@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """账号密码登录，成功返回 JWT 令牌与用户信息。"""
    user = db.scalar(select(SysUser).where(SysUser.username == payload.username))

    if user is None or not verify_password(payload.password, user.password_hash):
        write_login_log(db, payload.username, request, False, "账号或密码错误")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误"
        )

    if user.status != "启用":
        write_login_log(db, payload.username, request, False, "账号已停用")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已停用，请联系管理员"
        )

    # 校验通过，记录登录时间与日志
    user.last_login_at = datetime.now()
    db.commit()
    db.refresh(user)
    write_login_log(db, payload.username, request, True, "登录成功")

    role_code = user.role.code if user.role else ""
    token = create_access_token(user.id, user.username, role_code)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=build_profile(user),
        menus=MENU_BY_ROLE.get(role_code, []),
    )


@router.get("/profile", response_model=UserProfile, summary="获取当前登录用户信息")
def get_profile(current_user: SysUser = Depends(get_current_user)):
    """返回当前令牌对应的用户信息。"""
    return build_profile(current_user)


@router.post("/change-password", response_model=MessageOut, summary="修改密码")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """校验原密码后设置新密码。"""
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码不正确")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return MessageOut(message="密码修改成功，请使用新密码重新登录")
