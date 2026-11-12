"""宿舍管理路由：宿舍房间与住宿分配的增删改查。

写操作限系统管理员/总务管理员，读操作登录用户即可。
住宿分配会同步维护房间的已住人数（occupied）字段。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ADMIN, ROLE_GENERAL_AFFAIRS, get_current_user, require_roles
from app.models import AfDormAllocation, AfDormRoom, BaseClass, BaseStudent, SysUser
from app.schemas import (
    DormAllocationCreate,
    DormAllocationOut,
    DormAllocationUpdate,
    DormRoomCreate,
    DormRoomOut,
    DormRoomUpdate,
    MessageOut,
    PageResult,
)

router = APIRouter(prefix="/dorms", tags=["宿舍管理"])

# 写操作：系统管理员与总务管理员
editor = require_roles(ROLE_ADMIN, ROLE_GENERAL_AFFAIRS)


def _sync_room_occupied(db: Session, room_id: int) -> None:
    """按在住分配记录重算并写回房间的已住人数。"""
    room = db.get(AfDormRoom, room_id)
    if room is None:
        return
    room.occupied = (
        db.scalar(
            select(func.count())
            .select_from(AfDormAllocation)
            .where(
                AfDormAllocation.room_id == room_id,
                AfDormAllocation.status == "在住",
            )
        )
        or 0
    )
    db.commit()


def _to_allocation_out(allocation: AfDormAllocation, db: Session) -> DormAllocationOut:
    """组装住宿分配返回体，填充学生信息与房间信息。"""
    out = DormAllocationOut.model_validate(allocation)
    student = db.get(BaseStudent, allocation.student_id)
    if student:
        out.student_no = student.student_no
        out.student_name = student.name
        if student.class_id:
            cls = db.get(BaseClass, student.class_id)
            out.class_name = cls.name if cls else ""
    room = db.get(AfDormRoom, allocation.room_id)
    if room:
        out.building = room.building
        out.room_no = room.room_no
    return out


# ==================== 宿舍房间 ====================


@router.get("/rooms", response_model=PageResult[DormRoomOut], summary="宿舍房间分页列表")
def list_rooms(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按宿舍楼或房间号模糊查询"),
    building: str | None = Query(None, description="按宿舍楼筛选"),
    gender_type: str | None = Query(None, description="按性别类型筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字/宿舍楼/性别类型筛选，分页返回宿舍房间列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(AfDormRoom.building.ilike(like), AfDormRoom.room_no.ilike(like))
        )
    if building:
        conditions.append(AfDormRoom.building == building)
    if gender_type:
        conditions.append(AfDormRoom.gender_type == gender_type)

    total = db.scalar(select(func.count()).select_from(AfDormRoom).where(*conditions)) or 0
    rows = db.scalars(
        select(AfDormRoom)
        .where(*conditions)
        .order_by(AfDormRoom.building, AfDormRoom.room_no)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[DormRoomOut](
        total=total, items=[DormRoomOut.model_validate(r) for r in rows]
    )


@router.get("/rooms/options", summary="宿舍房间下拉选项")
def list_room_options(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简宿舍房间列表（name 为“宿舍楼 房间号”）。"""
    rows = db.scalars(
        select(AfDormRoom).order_by(AfDormRoom.building, AfDormRoom.room_no)
    ).all()
    return [{"id": r.id, "name": f"{r.building} {r.room_no}"} for r in rows]


@router.post(
    "/rooms",
    response_model=DormRoomOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增宿舍房间",
)
def create_room(
    payload: DormRoomCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增宿舍房间。"""
    room = AfDormRoom(**payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return DormRoomOut.model_validate(room)


@router.put("/rooms/{room_id}", response_model=DormRoomOut, summary="修改宿舍房间")
def update_room(
    room_id: int,
    payload: DormRoomUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改宿舍房间。"""
    room = db.get(AfDormRoom, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="宿舍房间不存在")

    data = payload.model_dump(exclude_unset=True)
    capacity = data.get("capacity")
    if capacity is not None and capacity < room.occupied:
        raise HTTPException(status_code=400, detail="床位数不能小于当前已住人数")

    for field, value in data.items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return DormRoomOut.model_validate(room)


@router.delete("/rooms/{room_id}", response_model=MessageOut, summary="删除宿舍房间")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除宿舍房间，若已有住宿分配记录则不允许删除。"""
    room = db.get(AfDormRoom, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="宿舍房间不存在")

    used = db.scalar(
        select(func.count())
        .select_from(AfDormAllocation)
        .where(AfDormAllocation.room_id == room_id)
    )
    if used:
        raise HTTPException(status_code=400, detail="该宿舍已有住宿分配记录，无法删除")

    db.delete(room)
    db.commit()
    return MessageOut(message="删除成功")


# ==================== 住宿分配 ====================


@router.get(
    "/allocations", response_model=PageResult[DormAllocationOut], summary="住宿分配分页列表"
)
def list_allocations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按学生学籍号或姓名模糊查询"),
    room_id: int | None = Query(None, description="按宿舍房间筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字/房间筛选，分页返回住宿分配列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        student_ids = select(BaseStudent.id).where(
            or_(BaseStudent.student_no.ilike(like), BaseStudent.name.ilike(like))
        )
        conditions.append(AfDormAllocation.student_id.in_(student_ids))
    if room_id:
        conditions.append(AfDormAllocation.room_id == room_id)

    total = (
        db.scalar(select(func.count()).select_from(AfDormAllocation).where(*conditions))
        or 0
    )
    rows = db.scalars(
        select(AfDormAllocation)
        .where(*conditions)
        .order_by(AfDormAllocation.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[DormAllocationOut](
        total=total, items=[_to_allocation_out(a, db) for a in rows]
    )


@router.post(
    "/allocations",
    response_model=DormAllocationOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增住宿分配",
)
def create_allocation(
    payload: DormAllocationCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增住宿分配，房间床位已满时不允许分配。"""
    if db.get(BaseStudent, payload.student_id) is None:
        raise HTTPException(status_code=400, detail="所选学生不存在")
    room = db.get(AfDormRoom, payload.room_id)
    if room is None:
        raise HTTPException(status_code=400, detail="所选宿舍房间不存在")
    if payload.status == "在住" and room.occupied >= room.capacity:
        raise HTTPException(status_code=400, detail="该宿舍剩余床位不足，无法分配")

    allocation = AfDormAllocation(**payload.model_dump())
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    _sync_room_occupied(db, allocation.room_id)
    return _to_allocation_out(allocation, db)


@router.put(
    "/allocations/{allocation_id}",
    response_model=DormAllocationOut,
    summary="修改住宿分配",
)
def update_allocation(
    allocation_id: int,
    payload: DormAllocationUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改住宿分配，调整房间或状态时同步维护床位占用。"""
    allocation = db.get(AfDormAllocation, allocation_id)
    if allocation is None:
        raise HTTPException(status_code=404, detail="住宿分配记录不存在")

    data = payload.model_dump(exclude_unset=True)
    old_room_id = allocation.room_id
    new_room_id = data.get("room_id", allocation.room_id)
    new_status = data.get("status", allocation.status)

    if new_status == "在住":
        room = db.get(AfDormRoom, new_room_id)
        if room is None:
            raise HTTPException(status_code=400, detail="所选宿舍房间不存在")
        in_house = (
            db.scalar(
                select(func.count())
                .select_from(AfDormAllocation)
                .where(
                    AfDormAllocation.room_id == new_room_id,
                    AfDormAllocation.status == "在住",
                    AfDormAllocation.id != allocation_id,
                )
            )
            or 0
        )
        if in_house >= room.capacity:
            raise HTTPException(status_code=400, detail="该宿舍剩余床位不足，无法分配")

    for field, value in data.items():
        setattr(allocation, field, value)
    db.commit()
    db.refresh(allocation)

    _sync_room_occupied(db, old_room_id)
    if new_room_id != old_room_id:
        _sync_room_occupied(db, new_room_id)
    return _to_allocation_out(allocation, db)


@router.delete(
    "/allocations/{allocation_id}",
    response_model=MessageOut,
    summary="删除住宿分配",
)
def delete_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除住宿分配记录，并释放对应床位。"""
    allocation = db.get(AfDormAllocation, allocation_id)
    if allocation is None:
        raise HTTPException(status_code=404, detail="住宿分配记录不存在")

    room_id = allocation.room_id
    db.delete(allocation)
    db.commit()
    _sync_room_occupied(db, room_id)
    return MessageOut(message="删除成功")
