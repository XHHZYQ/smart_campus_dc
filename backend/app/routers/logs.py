"""日志管理路由：操作日志与登录日志的分页查询（只读）。

仅系统管理员可访问。
"""

from datetime import date, datetime, time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ADMIN, require_roles
from app.models import SysLoginLog, SysOperationLog, SysUser
from app.schemas import LoginLogOut, OperationLogOut, PageResult

router = APIRouter(prefix="/logs", tags=["日志管理"])

# 仅系统管理员可查看日志
admin_only = require_roles(ROLE_ADMIN)


def _day_bounds(start: date | None, end: date | None) -> list:
    """把起止日期转换为时间范围查询条件。"""
    conditions = []
    if start:
        conditions.append(SysOperationLog.created_at >= datetime.combine(start, time.min))
    if end:
        conditions.append(SysOperationLog.created_at <= datetime.combine(end, time.max))
    return conditions


@router.get(
    "/operation",
    response_model=PageResult[OperationLogOut],
    summary="操作日志分页列表",
)
def list_operation_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按操作人或模块模糊查询"),
    start_date: date | None = Query(None, description="开始日期"),
    end_date: date | None = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """查询操作日志，按时间倒序分页返回。"""
    conditions = _day_bounds(start_date, end_date)
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(
                SysOperationLog.username.ilike(like),
                SysOperationLog.real_name.ilike(like),
                SysOperationLog.module.ilike(like),
                SysOperationLog.action.ilike(like),
            )
        )

    total = (
        db.scalar(select(func.count()).select_from(SysOperationLog).where(*conditions))
        or 0
    )
    rows = db.scalars(
        select(SysOperationLog)
        .where(*conditions)
        .order_by(SysOperationLog.created_at.desc(), SysOperationLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[OperationLogOut](
        total=total, items=[OperationLogOut.model_validate(r) for r in rows]
    )


@router.get(
    "/login",
    response_model=PageResult[LoginLogOut],
    summary="登录日志分页列表",
)
def list_login_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按登录账号或IP模糊查询"),
    start_date: date | None = Query(None, description="开始日期"),
    end_date: date | None = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(admin_only),
):
    """查询登录日志，按时间倒序分页返回。"""
    conditions = []
    if start_date:
        conditions.append(SysLoginLog.created_at >= datetime.combine(start_date, time.min))
    if end_date:
        conditions.append(SysLoginLog.created_at <= datetime.combine(end_date, time.max))
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(SysLoginLog.username.ilike(like), SysLoginLog.ip.ilike(like))
        )

    total = (
        db.scalar(select(func.count()).select_from(SysLoginLog).where(*conditions)) or 0
    )
    rows = db.scalars(
        select(SysLoginLog)
        .where(*conditions)
        .order_by(SysLoginLog.created_at.desc(), SysLoginLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[LoginLogOut](
        total=total, items=[LoginLogOut.model_validate(r) for r in rows]
    )
