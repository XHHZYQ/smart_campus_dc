"""排课管理路由：排课记录的增删改查、周课表与下拉选项。

写操作限系统管理员/教务管理员，读操作登录用户即可。
周课表按班级或教师返回，供前端渲染“行=节次、列=星期”的网格。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ACADEMIC, ROLE_ADMIN, get_current_user, require_roles
from app.models import (
    BaseClass,
    BaseSemester,
    BaseTeacher,
    EduCourse,
    EduSchedule,
    SysUser,
)
from app.schemas import (
    MessageOut,
    PageResult,
    ScheduleCreate,
    ScheduleOut,
    ScheduleUpdate,
    TimetableCell,
)

router = APIRouter(prefix="/schedules", tags=["排课管理"])

# 写操作：系统管理员与教务管理员
editor = require_roles(ROLE_ADMIN, ROLE_ACADEMIC)


def _to_schedule_out(schedule: EduSchedule, db: Session) -> ScheduleOut:
    """组装排课返回体，填充学期、班级、课程与教师名称。"""
    out = ScheduleOut.model_validate(schedule)
    semester = db.get(BaseSemester, schedule.semester_id)
    out.semester_name = semester.name if semester else ""
    cls = db.get(BaseClass, schedule.class_id)
    out.class_name = cls.name if cls else ""
    course = db.get(EduCourse, schedule.course_id)
    out.course_name = course.name if course else ""
    if schedule.teacher_id:
        teacher = db.get(BaseTeacher, schedule.teacher_id)
        out.teacher_name = teacher.name if teacher else ""
    return out


def _validate_refs(
    payload: ScheduleCreate | ScheduleUpdate, db: Session, *, require_all: bool
) -> None:
    """校验学期/班级/课程/教师引用是否存在。"""
    data = payload.model_dump(exclude_unset=True)
    if require_all or "semester_id" in data:
        if data.get("semester_id") and db.get(BaseSemester, data["semester_id"]) is None:
            raise HTTPException(status_code=400, detail="所选学期不存在")
    if require_all or "class_id" in data:
        if data.get("class_id") and db.get(BaseClass, data["class_id"]) is None:
            raise HTTPException(status_code=400, detail="所选班级不存在")
    if require_all or "course_id" in data:
        if data.get("course_id") and db.get(EduCourse, data["course_id"]) is None:
            raise HTTPException(status_code=400, detail="所选课程不存在")
    if data.get("teacher_id") and db.get(BaseTeacher, data["teacher_id"]) is None:
        raise HTTPException(status_code=400, detail="所选教师不存在")


@router.get("", response_model=PageResult[ScheduleOut], summary="排课分页列表")
def list_schedules(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    class_id: int | None = Query(None, description="按班级筛选"),
    course_id: int | None = Query(None, description="按课程筛选"),
    semester_id: int | None = Query(None, description="按学期筛选"),
    weekday: int | None = Query(None, description="按星期筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按班级/课程/学期/星期筛选，分页返回排课列表。"""
    conditions = []
    if class_id:
        conditions.append(EduSchedule.class_id == class_id)
    if course_id:
        conditions.append(EduSchedule.course_id == course_id)
    if semester_id:
        conditions.append(EduSchedule.semester_id == semester_id)
    if weekday:
        conditions.append(EduSchedule.weekday == weekday)

    total = (
        db.scalar(select(func.count()).select_from(EduSchedule).where(*conditions)) or 0
    )
    rows = db.scalars(
        select(EduSchedule)
        .where(*conditions)
        .order_by(EduSchedule.weekday, EduSchedule.period, EduSchedule.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[ScheduleOut](
        total=total, items=[_to_schedule_out(s, db) for s in rows]
    )


@router.get("/timetable", response_model=list[TimetableCell], summary="周课表")
def get_timetable(
    class_id: int | None = Query(None, description="按班级查询"),
    teacher_id: int | None = Query(None, description="按教师查询"),
    semester_id: int | None = Query(None, description="按学期筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按班级或教师返回周课表单元格列表（含星期与节次）。"""
    if not class_id and not teacher_id:
        return []

    conditions = []
    if class_id:
        conditions.append(EduSchedule.class_id == class_id)
    if teacher_id:
        conditions.append(EduSchedule.teacher_id == teacher_id)
    if semester_id:
        conditions.append(EduSchedule.semester_id == semester_id)

    rows = db.scalars(
        select(EduSchedule)
        .where(*conditions)
        .order_by(EduSchedule.period, EduSchedule.weekday)
    ).all()

    cells: list[TimetableCell] = []
    for schedule in rows:
        course = db.get(EduCourse, schedule.course_id)
        teacher = db.get(BaseTeacher, schedule.teacher_id) if schedule.teacher_id else None
        cells.append(
            TimetableCell(
                weekday=schedule.weekday,
                period=schedule.period,
                course_name=course.name if course else "",
                teacher_name=teacher.name if teacher else "",
                room=schedule.room or "",
            )
        )
    return cells


@router.post(
    "",
    response_model=ScheduleOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增排课",
)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增排课记录，同一班级同一学期同一节次不可重复。"""
    _validate_refs(payload, db, require_all=True)
    exists = db.scalar(
        select(EduSchedule).where(
            EduSchedule.class_id == payload.class_id,
            EduSchedule.semester_id == payload.semester_id,
            EduSchedule.weekday == payload.weekday,
            EduSchedule.period == payload.period,
        )
    )
    if exists:
        raise HTTPException(status_code=400, detail="该班级在此节次已有排课")

    schedule = EduSchedule(**payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return _to_schedule_out(schedule, db)


@router.put("/{schedule_id}", response_model=ScheduleOut, summary="修改排课")
def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改排课记录。"""
    schedule = db.get(EduSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="排课记录不存在")

    _validate_refs(payload, db, require_all=False)
    data = payload.model_dump(exclude_unset=True)

    new_class_id = data.get("class_id", schedule.class_id)
    new_semester_id = data.get("semester_id", schedule.semester_id)
    new_weekday = data.get("weekday", schedule.weekday)
    new_period = data.get("period", schedule.period)
    conflict = db.scalar(
        select(EduSchedule).where(
            EduSchedule.class_id == new_class_id,
            EduSchedule.semester_id == new_semester_id,
            EduSchedule.weekday == new_weekday,
            EduSchedule.period == new_period,
            EduSchedule.id != schedule_id,
        )
    )
    if conflict:
        raise HTTPException(status_code=400, detail="该班级在此节次已有排课")

    for field, value in data.items():
        setattr(schedule, field, value)
    db.commit()
    db.refresh(schedule)
    return _to_schedule_out(schedule, db)


@router.delete("/{schedule_id}", response_model=MessageOut, summary="删除排课")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除排课记录。"""
    schedule = db.get(EduSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="排课记录不存在")

    db.delete(schedule)
    db.commit()
    return MessageOut(message="删除成功")
