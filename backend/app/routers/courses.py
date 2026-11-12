"""学科课程路由：课程库的增删改查与下拉选项。

写操作限系统管理员/教务管理员，读操作登录用户即可。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ACADEMIC, ROLE_ADMIN, get_current_user, require_roles
from app.models import (
    BaseDepartment,
    BaseTeacher,
    EduAttendance,
    EduCourse,
    EduSchedule,
    EduScore,
    SysUser,
)
from app.schemas import CourseCreate, CourseOut, CourseUpdate, MessageOut, PageResult

router = APIRouter(prefix="/courses", tags=["学科课程"])

# 写操作：系统管理员与教务管理员
editor = require_roles(ROLE_ADMIN, ROLE_ACADEMIC)


def _to_course_out(course: EduCourse, db: Session) -> CourseOut:
    """组装课程返回体，填充开课教研组名称与任课教师姓名。"""
    out = CourseOut.model_validate(course)
    if course.department_id:
        dept = db.get(BaseDepartment, course.department_id)
        out.department_name = dept.name if dept else ""
    if course.teacher_id:
        teacher = db.get(BaseTeacher, course.teacher_id)
        out.teacher_name = teacher.name if teacher else ""
    return out


@router.get("", response_model=PageResult[CourseOut], summary="课程分页列表")
def list_courses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按课程名称或代码模糊查询"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字筛选，分页返回课程列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(or_(EduCourse.name.ilike(like), EduCourse.code.ilike(like)))

    total = db.scalar(select(func.count()).select_from(EduCourse).where(*conditions)) or 0
    rows = db.scalars(
        select(EduCourse)
        .where(*conditions)
        .order_by(EduCourse.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[CourseOut](total=total, items=[_to_course_out(c, db) for c in rows])


@router.get("/options", summary="课程下拉选项")
def list_course_options(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简课程列表。"""
    rows = db.scalars(select(EduCourse).order_by(EduCourse.id)).all()
    return [{"id": r.id, "name": r.name} for r in rows]


@router.post(
    "",
    response_model=CourseOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增课程",
)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增课程，课程代码需唯一。"""
    if db.scalar(select(EduCourse).where(EduCourse.code == payload.code)):
        raise HTTPException(status_code=400, detail="课程代码已存在")
    if payload.department_id and db.get(BaseDepartment, payload.department_id) is None:
        raise HTTPException(status_code=400, detail="所选教研组不存在")
    if payload.teacher_id and db.get(BaseTeacher, payload.teacher_id) is None:
        raise HTTPException(status_code=400, detail="所选任课教师不存在")

    course = EduCourse(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return _to_course_out(course, db)


@router.put("/{course_id}", response_model=CourseOut, summary="修改课程")
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改课程信息。"""
    course = db.get(EduCourse, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    data = payload.model_dump(exclude_unset=True)
    department_id = data.get("department_id")
    if department_id is not None and db.get(BaseDepartment, department_id) is None:
        raise HTTPException(status_code=400, detail="所选教研组不存在")
    teacher_id = data.get("teacher_id")
    if teacher_id is not None and db.get(BaseTeacher, teacher_id) is None:
        raise HTTPException(status_code=400, detail="所选任课教师不存在")

    for field, value in data.items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return _to_course_out(course, db)


@router.delete("/{course_id}", response_model=MessageOut, summary="删除课程")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除课程，若已被排课、成绩或考勤引用则不允许删除。"""
    course = db.get(EduCourse, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    for model in (EduSchedule, EduScore, EduAttendance):
        used = db.scalar(
            select(func.count()).select_from(model).where(model.course_id == course_id)
        )
        if used:
            raise HTTPException(status_code=400, detail="该课程已被教学业务引用，无法删除")

    db.delete(course)
    db.commit()
    return MessageOut(message="删除成功")
