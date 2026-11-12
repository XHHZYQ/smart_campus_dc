"""考勤记录路由：学生考勤的查询与增删改。

写操作允许系统管理员/教务管理员/班主任/任课教师，读操作登录用户即可。
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import (
    ROLE_ACADEMIC,
    ROLE_ADMIN,
    ROLE_HEAD_TEACHER,
    ROLE_SUBJECT_TEACHER,
    get_current_user,
    require_roles,
)
from app.models import BaseClass, BaseStudent, EduAttendance, EduCourse, SysUser
from app.schemas import (
    AttendanceCreate,
    AttendanceOut,
    AttendanceUpdate,
    MessageOut,
    PageResult,
)

router = APIRouter(prefix="/attendances", tags=["考勤记录"])

# 写操作：系统管理员、教务管理员、班主任、任课教师
editor = require_roles(
    ROLE_ADMIN, ROLE_ACADEMIC, ROLE_HEAD_TEACHER, ROLE_SUBJECT_TEACHER
)


def _to_attendance_out(attendance: EduAttendance, db: Session) -> AttendanceOut:
    """组装考勤返回体，填充学籍号、学生姓名、班级与课程名称。"""
    out = AttendanceOut.model_validate(attendance)
    student = db.get(BaseStudent, attendance.student_id)
    if student:
        out.student_no = student.student_no
        out.student_name = student.name
        if student.class_id:
            cls = db.get(BaseClass, student.class_id)
            out.class_name = cls.name if cls else ""
    course = db.get(EduCourse, attendance.course_id)
    out.course_name = course.name if course else ""
    return out


@router.get("", response_model=PageResult[AttendanceOut], summary="考勤分页列表")
def list_attendances(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    student_id: int | None = Query(None, description="按学生筛选"),
    class_id: int | None = Query(None, description="按班级筛选"),
    course_id: int | None = Query(None, description="按课程筛选"),
    date_from: date | None = Query(None, description="考勤起始日期"),
    date_to: date | None = Query(None, description="考勤结束日期"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按学生/班级/课程/日期范围筛选，分页返回考勤列表。"""
    conditions = []
    if student_id:
        conditions.append(EduAttendance.student_id == student_id)
    if class_id:
        student_ids = select(BaseStudent.id).where(BaseStudent.class_id == class_id)
        conditions.append(EduAttendance.student_id.in_(student_ids))
    if course_id:
        conditions.append(EduAttendance.course_id == course_id)
    if date_from:
        conditions.append(EduAttendance.attend_date >= date_from)
    if date_to:
        conditions.append(EduAttendance.attend_date <= date_to)

    total = (
        db.scalar(select(func.count()).select_from(EduAttendance).where(*conditions)) or 0
    )
    rows = db.scalars(
        select(EduAttendance)
        .where(*conditions)
        .order_by(EduAttendance.attend_date.desc(), EduAttendance.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[AttendanceOut](
        total=total, items=[_to_attendance_out(a, db) for a in rows]
    )


@router.post(
    "",
    response_model=AttendanceOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增考勤",
)
def create_attendance(
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增考勤记录。"""
    if db.get(BaseStudent, payload.student_id) is None:
        raise HTTPException(status_code=400, detail="所选学生不存在")
    if db.get(EduCourse, payload.course_id) is None:
        raise HTTPException(status_code=400, detail="所选课程不存在")

    attendance = EduAttendance(**payload.model_dump())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return _to_attendance_out(attendance, db)


@router.put("/{attendance_id}", response_model=AttendanceOut, summary="修改考勤")
def update_attendance(
    attendance_id: int,
    payload: AttendanceUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改考勤记录。"""
    attendance = db.get(EduAttendance, attendance_id)
    if attendance is None:
        raise HTTPException(status_code=404, detail="考勤记录不存在")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(attendance, field, value)
    db.commit()
    db.refresh(attendance)
    return _to_attendance_out(attendance, db)


@router.delete("/{attendance_id}", response_model=MessageOut, summary="删除考勤")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除考勤记录。"""
    attendance = db.get(EduAttendance, attendance_id)
    if attendance is None:
        raise HTTPException(status_code=404, detail="考勤记录不存在")

    db.delete(attendance)
    db.commit()
    return MessageOut(message="删除成功")
