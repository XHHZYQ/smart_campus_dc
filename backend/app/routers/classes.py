"""班级管理路由：班级的增删改查与下拉选项。

写操作限系统管理员/教务管理员，读操作登录用户即可。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ACADEMIC, ROLE_ADMIN, get_current_user, require_roles
from app.models import BaseClass, BaseGrade, BaseStudent, BaseTeacher, SysUser
from app.schemas import ClassCreate, ClassOut, ClassUpdate, MessageOut, PageResult

router = APIRouter(prefix="/classes", tags=["班级管理"])

# 写操作：系统管理员与教务管理员
editor = require_roles(ROLE_ADMIN, ROLE_ACADEMIC)


def _to_class_out(cls: BaseClass, db: Session) -> ClassOut:
    """组装班级返回体，填充年级名称、学段、班主任姓名与人数。"""
    grade = db.get(BaseGrade, cls.grade_id) if cls.grade_id else None
    head_teacher_name = ""
    if cls.head_teacher_id:
        teacher = db.get(BaseTeacher, cls.head_teacher_id)
        head_teacher_name = teacher.name if teacher else ""
    student_count = (
        db.scalar(
            select(func.count())
            .select_from(BaseStudent)
            .where(BaseStudent.class_id == cls.id)
        )
        or 0
    )
    return ClassOut(
        id=cls.id,
        name=cls.name,
        code=cls.code,
        grade_id=cls.grade_id,
        grade_name=grade.name if grade else "",
        stage=grade.stage if grade else "",
        room=cls.room,
        head_teacher_id=cls.head_teacher_id,
        head_teacher_name=head_teacher_name,
        student_count=student_count,
        enroll_year=cls.enroll_year,
        remark=cls.remark,
        created_at=cls.created_at,
    )


@router.get("", response_model=PageResult[ClassOut], summary="班级分页列表")
def list_classes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按名称或编码模糊查询"),
    grade_id: int | None = Query(None, description="按年级筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字/年级筛选，分页返回班级列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(or_(BaseClass.name.ilike(like), BaseClass.code.ilike(like)))
    if grade_id:
        conditions.append(BaseClass.grade_id == grade_id)

    total = db.scalar(select(func.count()).select_from(BaseClass).where(*conditions)) or 0
    rows = db.scalars(
        select(BaseClass)
        .where(*conditions)
        .order_by(BaseClass.grade_id, BaseClass.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[ClassOut](total=total, items=[_to_class_out(c, db) for c in rows])


@router.get("/options", summary="班级下拉选项")
def list_class_options(
    grade_id: int | None = Query(None, description="按年级筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简班级列表，可按年级过滤。"""
    stmt = select(BaseClass)
    if grade_id:
        stmt = stmt.where(BaseClass.grade_id == grade_id)
    rows = db.scalars(stmt.order_by(BaseClass.grade_id, BaseClass.id)).all()
    return [{"id": r.id, "name": r.name} for r in rows]


@router.post(
    "",
    response_model=ClassOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增班级",
)
def create_class(
    payload: ClassCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增班级，编码需唯一且所属年级必须存在。"""
    if db.scalar(select(BaseClass).where(BaseClass.code == payload.code)):
        raise HTTPException(status_code=400, detail="班级编码已存在")
    if db.get(BaseGrade, payload.grade_id) is None:
        raise HTTPException(status_code=400, detail="所选年级不存在")

    cls = BaseClass(**payload.model_dump())
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return _to_class_out(cls, db)


@router.put("/{class_id}", response_model=ClassOut, summary="修改班级")
def update_class(
    class_id: int,
    payload: ClassUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改班级信息。"""
    cls = db.get(BaseClass, class_id)
    if cls is None:
        raise HTTPException(status_code=404, detail="班级不存在")

    data = payload.model_dump(exclude_unset=True)
    code = data.get("code")
    if code and code != cls.code and db.scalar(
        select(BaseClass).where(BaseClass.code == code)
    ):
        raise HTTPException(status_code=400, detail="班级编码已存在")
    grade_id = data.get("grade_id")
    if grade_id is not None and db.get(BaseGrade, grade_id) is None:
        raise HTTPException(status_code=400, detail="所选年级不存在")

    for field, value in data.items():
        setattr(cls, field, value)
    db.commit()
    db.refresh(cls)
    return _to_class_out(cls, db)


@router.delete("/{class_id}", response_model=MessageOut, summary="删除班级")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除班级，若仍有学生归属则不允许删除。"""
    cls = db.get(BaseClass, class_id)
    if cls is None:
        raise HTTPException(status_code=404, detail="班级不存在")

    used = db.scalar(
        select(func.count())
        .select_from(BaseStudent)
        .where(BaseStudent.class_id == class_id)
    )
    if used:
        raise HTTPException(status_code=400, detail="该班级下仍有学生，无法删除")

    db.delete(cls)
    db.commit()
    return MessageOut(message="删除成功")
