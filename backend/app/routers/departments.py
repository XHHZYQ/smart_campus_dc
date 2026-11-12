"""部门管理路由：行政科室与教研组的增删改查与下拉选项。

写操作限系统管理员/教务管理员，读操作登录用户即可。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ACADEMIC, ROLE_ADMIN, get_current_user, require_roles
from app.models import BaseDepartment, BaseTeacher, SysUser
from app.schemas import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
    MessageOut,
    PageResult,
)

router = APIRouter(prefix="/departments", tags=["部门管理"])

# 写操作：系统管理员与教务管理员
editor = require_roles(ROLE_ADMIN, ROLE_ACADEMIC)


@router.get("", response_model=PageResult[DepartmentOut], summary="部门分页列表")
def list_departments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按名称、编码或负责人模糊查询"),
    dept_type: str | None = Query(None, description="按类型筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字/类型筛选，分页返回部门列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(
                BaseDepartment.name.ilike(like),
                BaseDepartment.code.ilike(like),
                BaseDepartment.leader.ilike(like),
            )
        )
    if dept_type:
        conditions.append(BaseDepartment.dept_type == dept_type)

    total = (
        db.scalar(select(func.count()).select_from(BaseDepartment).where(*conditions))
        or 0
    )
    rows = db.scalars(
        select(BaseDepartment)
        .where(*conditions)
        .order_by(BaseDepartment.sort_order, BaseDepartment.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[DepartmentOut](
        total=total, items=[DepartmentOut.model_validate(r) for r in rows]
    )


@router.get("/options", summary="部门下拉选项")
def list_department_options(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简部门列表。"""
    rows = db.scalars(
        select(BaseDepartment).order_by(BaseDepartment.sort_order, BaseDepartment.id)
    ).all()
    return [{"id": r.id, "name": r.name} for r in rows]


@router.post(
    "",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增部门",
)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增部门，编码需唯一。"""
    if db.scalar(select(BaseDepartment).where(BaseDepartment.code == payload.code)):
        raise HTTPException(status_code=400, detail="部门编码已存在")

    department = BaseDepartment(**payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return DepartmentOut.model_validate(department)


@router.put("/{department_id}", response_model=DepartmentOut, summary="修改部门")
def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改部门信息。"""
    department = db.get(BaseDepartment, department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="部门不存在")

    data = payload.model_dump(exclude_unset=True)
    code = data.get("code")
    if code and code != department.code and db.scalar(
        select(BaseDepartment).where(BaseDepartment.code == code)
    ):
        raise HTTPException(status_code=400, detail="部门编码已存在")

    for field, value in data.items():
        setattr(department, field, value)
    db.commit()
    db.refresh(department)
    return DepartmentOut.model_validate(department)


@router.delete("/{department_id}", response_model=MessageOut, summary="删除部门")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除部门，若仍有教职工归属则不允许删除。"""
    department = db.get(BaseDepartment, department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="部门不存在")

    used = db.scalar(
        select(func.count())
        .select_from(BaseTeacher)
        .where(BaseTeacher.department_id == department_id)
    )
    if used:
        raise HTTPException(status_code=400, detail="该部门下仍有教职工，无法删除")

    db.delete(department)
    db.commit()
    return MessageOut(message="删除成功")
