"""资产台账路由：学校设备资产的增删改查与下拉选项。

写操作限系统管理员/总务管理员，读操作登录用户即可。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ADMIN, ROLE_GENERAL_AFFAIRS, get_current_user, require_roles
from app.models import AfAsset, BaseDepartment, SysUser
from app.schemas import AssetCreate, AssetOut, AssetUpdate, MessageOut, PageResult

router = APIRouter(prefix="/assets", tags=["资产台账"])

# 写操作：系统管理员与总务管理员
editor = require_roles(ROLE_ADMIN, ROLE_GENERAL_AFFAIRS)


def _to_asset_out(asset: AfAsset, db: Session) -> AssetOut:
    """组装资产返回体，填充所属部门名称。"""
    out = AssetOut.model_validate(asset)
    if asset.department_id:
        dept = db.get(BaseDepartment, asset.department_id)
        out.department_name = dept.name if dept else ""
    return out


@router.get("", response_model=PageResult[AssetOut], summary="资产分页列表")
def list_assets(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按资产编号、名称、品牌或保管人模糊查询"),
    category: str | None = Query(None, description="按分类筛选"),
    status: str | None = Query(None, description="按状态筛选"),
    department_id: int | None = Query(None, description="按所属部门筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字/分类/状态/部门筛选，分页返回资产列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(
                AfAsset.asset_no.ilike(like),
                AfAsset.name.ilike(like),
                AfAsset.brand.ilike(like),
                AfAsset.keeper.ilike(like),
            )
        )
    if category:
        conditions.append(AfAsset.category == category)
    if status:
        conditions.append(AfAsset.status == status)
    if department_id:
        conditions.append(AfAsset.department_id == department_id)

    total = db.scalar(select(func.count()).select_from(AfAsset).where(*conditions)) or 0
    rows = db.scalars(
        select(AfAsset)
        .where(*conditions)
        .order_by(AfAsset.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[AssetOut](total=total, items=[_to_asset_out(a, db) for a in rows])


@router.get("/options", summary="资产下拉选项")
def list_asset_options(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简资产列表（name 为“资产编号 名称”）。"""
    rows = db.scalars(select(AfAsset).order_by(AfAsset.asset_no)).all()
    return [{"id": r.id, "name": f"{r.asset_no} {r.name}"} for r in rows]


@router.post(
    "",
    response_model=AssetOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增资产",
)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增资产，资产编号需唯一。"""
    if db.scalar(select(AfAsset).where(AfAsset.asset_no == payload.asset_no)):
        raise HTTPException(status_code=400, detail="资产编号已存在")
    if payload.department_id and db.get(BaseDepartment, payload.department_id) is None:
        raise HTTPException(status_code=400, detail="所选部门不存在")

    asset = AfAsset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return _to_asset_out(asset, db)


@router.put("/{asset_id}", response_model=AssetOut, summary="修改资产")
def update_asset(
    asset_id: int,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改资产信息。"""
    asset = db.get(AfAsset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="资产不存在")

    data = payload.model_dump(exclude_unset=True)
    department_id = data.get("department_id")
    if department_id is not None and db.get(BaseDepartment, department_id) is None:
        raise HTTPException(status_code=400, detail="所选部门不存在")

    for field, value in data.items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return _to_asset_out(asset, db)


@router.delete("/{asset_id}", response_model=MessageOut, summary="删除资产")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除资产。"""
    asset = db.get(AfAsset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="资产不存在")

    db.delete(asset)
    db.commit()
    return MessageOut(message="删除成功")
