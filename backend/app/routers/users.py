"""用户管理路由：系统用户的增删改查与密码重置。

仅系统管理员可访问。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ADMIN, require_roles
from app.models import SysRole, SysUser
from app.schemas import (
    MessageOut,
    PageResult,
    ResetPasswordRequest,
    UserCreate,
    UserOut,
    UserUpdate,
)
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["用户管理"])

# 仅系统管理员可管理用户
admin_only = require_roles(ROLE_ADMIN)


def _to_user_out(user: SysUser) -> UserOut:
    """把用户对象转换为返回体，并填充角色名称。"""
    return UserOut(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        role_id=user.role_id,
        role_name=user.role.name if user.role else "",
        teacher_id=user.teacher_id,
        phone=user.phone,
        email=user.email,
        status=user.status,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.get("", response_model=PageResult[UserOut], summary="用户分页列表")
def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按账号或姓名模糊查询"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """按账号/姓名模糊查询，分页返回。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(or_(SysUser.username.ilike(like), SysUser.real_name.ilike(like)))

    total = db.scalar(select(func.count()).select_from(SysUser).where(*conditions)) or 0
    rows = db.scalars(
        select(SysUser)
        .where(*conditions)
        .order_by(SysUser.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[UserOut](total=total, items=[_to_user_out(u) for u in rows])


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增用户",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """新增系统用户，账号需唯一。"""
    if db.scalar(select(SysUser).where(SysUser.username == payload.username)):
        raise HTTPException(status_code=400, detail="登录账号已存在")
    if db.get(SysRole, payload.role_id) is None:
        raise HTTPException(status_code=400, detail="所选角色不存在")

    data = payload.model_dump()
    password = data.pop("password")
    user = SysUser(**data, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_user_out(user)


@router.put("/{user_id}", response_model=UserOut, summary="修改用户")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """修改用户信息（不含账号与密码）。"""
    user = db.get(SysUser, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    data = payload.model_dump(exclude_unset=True)
    role_id = data.get("role_id")
    if role_id is not None and db.get(SysRole, role_id) is None:
        raise HTTPException(status_code=400, detail="所选角色不存在")

    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return _to_user_out(user)


@router.put("/{user_id}/reset-password", response_model=MessageOut, summary="重置密码")
def reset_password(
    user_id: int,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """管理员重置指定用户密码。"""
    user = db.get(SysUser, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return MessageOut(message="密码重置成功")


@router.delete("/{user_id}", response_model=MessageOut, summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(admin_only),
):
    """删除用户，不允许删除当前登录账号。"""
    user = db.get(SysUser, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录账号")

    db.delete(user)
    db.commit()
    return MessageOut(message="删除成功")
