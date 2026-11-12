"""角色管理路由：角色的增删改查与下拉选项。

仅系统管理员可访问。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ADMIN, require_roles
from app.models import SysRole, SysUser
from app.schemas import MessageOut, PageResult, RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["角色管理"])

# 仅系统管理员可管理角色
admin_only = require_roles(ROLE_ADMIN)


@router.get("", response_model=PageResult[RoleOut], summary="角色分页列表")
def list_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按名称或编码模糊查询"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """按角色名称/编码模糊查询，分页返回。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(or_(SysRole.name.ilike(like), SysRole.code.ilike(like)))

    total = db.scalar(select(func.count()).select_from(SysRole).where(*conditions)) or 0
    rows = db.scalars(
        select(SysRole)
        .where(*conditions)
        .order_by(SysRole.sort_order, SysRole.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[RoleOut](total=total, items=[RoleOut.model_validate(r) for r in rows])


@router.get("/options", summary="角色下拉选项")
def list_role_options(
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """返回 id + name 的精简角色列表。"""
    rows = db.scalars(select(SysRole).order_by(SysRole.sort_order, SysRole.id)).all()
    return [{"id": r.id, "name": r.name} for r in rows]


@router.post(
    "",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增角色",
)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """新增角色，角色编码需唯一。"""
    if db.scalar(select(SysRole).where(SysRole.code == payload.code)):
        raise HTTPException(status_code=400, detail="角色编码已存在")

    role = SysRole(**payload.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleOut.model_validate(role)


@router.put("/{role_id}", response_model=RoleOut, summary="修改角色")
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """修改角色，若修改编码需校验唯一性。"""
    role = db.get(SysRole, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="角色不存在")

    data = payload.model_dump(exclude_unset=True)
    code = data.get("code")
    if code and code != role.code and db.scalar(
        select(SysRole).where(SysRole.code == code)
    ):
        raise HTTPException(status_code=400, detail="角色编码已存在")

    for field, value in data.items():
        setattr(role, field, value)
    db.commit()
    db.refresh(role)
    return RoleOut.model_validate(role)


@router.delete("/{role_id}", response_model=MessageOut, summary="删除角色")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """删除角色，若仍有用户使用则不允许删除。"""
    role = db.get(SysRole, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="角色不存在")

    used = db.scalar(
        select(func.count()).select_from(SysUser).where(SysUser.role_id == role_id)
    )
    if used:
        raise HTTPException(status_code=400, detail="该角色下仍有用户，无法删除")

    db.delete(role)
    db.commit()
    return MessageOut(message="删除成功")
