"""学期管理路由：学年的学期维护与下拉选项。

写操作限系统管理员/教务管理员，读操作登录用户即可。
当前学期在同一时间只能有一个。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ACADEMIC, ROLE_ADMIN, get_current_user, require_roles
from app.models import BaseSemester, SysUser
from app.schemas import (
    MessageOut,
    PageResult,
    SemesterCreate,
    SemesterOut,
    SemesterUpdate,
)

router = APIRouter(prefix="/semesters", tags=["学期管理"])

# 写操作：系统管理员与教务管理员
editor = require_roles(ROLE_ADMIN, ROLE_ACADEMIC)


def _clear_other_current(db: Session, keep_id: int | None = None) -> None:
    """把除 keep_id 以外的学期全部置为非当前学期。"""
    stmt = update(BaseSemester).where(BaseSemester.is_current == True)  # noqa: E712
    if keep_id is not None:
        stmt = stmt.where(BaseSemester.id != keep_id)
    db.execute(stmt.values(is_current=False))


@router.get("", response_model=PageResult[SemesterOut], summary="学期分页列表")
def list_semesters(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按学期名称或学年模糊查询"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字筛选，分页返回学期列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(
                BaseSemester.name.ilike(like),
                BaseSemester.academic_year.ilike(like),
            )
        )

    total = (
        db.scalar(select(func.count()).select_from(BaseSemester).where(*conditions)) or 0
    )
    rows = db.scalars(
        select(BaseSemester)
        .where(*conditions)
        .order_by(BaseSemester.academic_year.desc(), BaseSemester.term.desc(), BaseSemester.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[SemesterOut](
        total=total, items=[SemesterOut.model_validate(r) for r in rows]
    )


@router.get("/options", summary="学期下拉选项")
def list_semester_options(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简学期列表。"""
    rows = db.scalars(
        select(BaseSemester).order_by(
            BaseSemester.academic_year.desc(), BaseSemester.term.desc()
        )
    ).all()
    return [{"id": r.id, "name": r.name} for r in rows]


@router.post(
    "",
    response_model=SemesterOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增学期",
)
def create_semester(
    payload: SemesterCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增学期，若设为当前学期则自动取消其他学期。"""
    if payload.is_current:
        _clear_other_current(db)

    semester = BaseSemester(**payload.model_dump())
    db.add(semester)
    db.commit()
    db.refresh(semester)
    return SemesterOut.model_validate(semester)


@router.put("/{semester_id}", response_model=SemesterOut, summary="修改学期")
def update_semester(
    semester_id: int,
    payload: SemesterUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改学期，若设为当前学期则自动取消其他学期。"""
    semester = db.get(BaseSemester, semester_id)
    if semester is None:
        raise HTTPException(status_code=404, detail="学期不存在")

    data = payload.model_dump(exclude_unset=True)
    if data.get("is_current") is True:
        _clear_other_current(db, keep_id=semester_id)

    for field, value in data.items():
        setattr(semester, field, value)
    db.commit()
    db.refresh(semester)
    return SemesterOut.model_validate(semester)


@router.delete("/{semester_id}", response_model=MessageOut, summary="删除学期")
def delete_semester(
    semester_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除学期。"""
    semester = db.get(BaseSemester, semester_id)
    if semester is None:
        raise HTTPException(status_code=404, detail="学期不存在")

    db.delete(semester)
    db.commit()
    return MessageOut(message="删除成功")
