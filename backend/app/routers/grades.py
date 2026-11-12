"""年级管理路由：年级的增删改查与下拉选项。

写操作限系统管理员/教务管理员，读操作登录用户即可。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ACADEMIC, ROLE_ADMIN, get_current_user, require_roles
from app.models import BaseClass, BaseGrade, BaseTeacher, SysUser
from app.schemas import GradeCreate, GradeOut, GradeUpdate, MessageOut, PageResult

router = APIRouter(prefix="/grades", tags=["年级管理"])

# 写操作：系统管理员与教务管理员
editor = require_roles(ROLE_ADMIN, ROLE_ACADEMIC)


def _to_grade_out(grade: BaseGrade, db: Session) -> GradeOut:
    """组装年级返回体，填充年级组长姓名与班级数量。"""
    head_teacher_name = ""
    if grade.head_teacher_id:
        teacher = db.get(BaseTeacher, grade.head_teacher_id)
        head_teacher_name = teacher.name if teacher else ""
    class_count = (
        db.scalar(
            select(func.count())
            .select_from(BaseClass)
            .where(BaseClass.grade_id == grade.id)
        )
        or 0
    )
    return GradeOut(
        id=grade.id,
        name=grade.name,
        code=grade.code,
        stage=grade.stage,
        grade_level=grade.grade_level,
        head_teacher_id=grade.head_teacher_id,
        head_teacher_name=head_teacher_name,
        class_count=class_count,
        created_at=grade.created_at,
    )


@router.get("", response_model=PageResult[GradeOut], summary="年级分页列表")
def list_grades(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按名称或编码模糊查询"),
    stage: str | None = Query(None, description="按学段筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字/学段筛选，分页返回年级列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(or_(BaseGrade.name.ilike(like), BaseGrade.code.ilike(like)))
    if stage:
        conditions.append(BaseGrade.stage == stage)

    total = db.scalar(select(func.count()).select_from(BaseGrade).where(*conditions)) or 0
    rows = db.scalars(
        select(BaseGrade)
        .where(*conditions)
        .order_by(BaseGrade.grade_level, BaseGrade.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[GradeOut](
        total=total, items=[_to_grade_out(g, db) for g in rows]
    )


@router.get("/options", summary="年级下拉选项")
def list_grade_options(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简年级列表。"""
    rows = db.scalars(select(BaseGrade).order_by(BaseGrade.grade_level, BaseGrade.id)).all()
    return [{"id": r.id, "name": r.name} for r in rows]


@router.post(
    "",
    response_model=GradeOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增年级",
)
def create_grade(
    payload: GradeCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增年级，编码需唯一。"""
    if db.scalar(select(BaseGrade).where(BaseGrade.code == payload.code)):
        raise HTTPException(status_code=400, detail="年级编码已存在")

    grade = BaseGrade(**payload.model_dump())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return _to_grade_out(grade, db)


@router.put("/{grade_id}", response_model=GradeOut, summary="修改年级")
def update_grade(
    grade_id: int,
    payload: GradeUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改年级信息。"""
    grade = db.get(BaseGrade, grade_id)
    if grade is None:
        raise HTTPException(status_code=404, detail="年级不存在")

    data = payload.model_dump(exclude_unset=True)
    code = data.get("code")
    if code and code != grade.code and db.scalar(
        select(BaseGrade).where(BaseGrade.code == code)
    ):
        raise HTTPException(status_code=400, detail="年级编码已存在")

    for field, value in data.items():
        setattr(grade, field, value)
    db.commit()
    db.refresh(grade)
    return _to_grade_out(grade, db)


@router.delete("/{grade_id}", response_model=MessageOut, summary="删除年级")
def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除年级，若仍有班级归属则不允许删除。"""
    grade = db.get(BaseGrade, grade_id)
    if grade is None:
        raise HTTPException(status_code=404, detail="年级不存在")

    used = db.scalar(
        select(func.count()).select_from(BaseClass).where(BaseClass.grade_id == grade_id)
    )
    if used:
        raise HTTPException(status_code=400, detail="该年级下仍有班级，无法删除")

    db.delete(grade)
    db.commit()
    return MessageOut(message="删除成功")
