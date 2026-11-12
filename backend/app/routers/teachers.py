"""教职工档案路由：教师与行政人员档案的增删改查与下拉选项。

写操作限系统管理员/教务管理员，读操作登录用户即可。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ACADEMIC, ROLE_ADMIN, get_current_user, require_roles
from app.models import BaseDepartment, BaseTeacher, SysUser
from app.schemas import MessageOut, PageResult, TeacherCreate, TeacherOut, TeacherUpdate

router = APIRouter(prefix="/teachers", tags=["教职工档案"])

# 写操作：系统管理员与教务管理员
editor = require_roles(ROLE_ADMIN, ROLE_ACADEMIC)


def _to_teacher_out(teacher: BaseTeacher) -> TeacherOut:
    """组装教职工返回体，填充所属部门名称。"""
    return TeacherOut(
        id=teacher.id,
        teacher_no=teacher.teacher_no,
        name=teacher.name,
        gender=teacher.gender,
        department_id=teacher.department_id,
        department_name=teacher.department.name if teacher.department else "",
        subject=teacher.subject,
        title=teacher.title,
        phone=teacher.phone,
        email=teacher.email,
        hire_date=teacher.hire_date,
        status=teacher.status,
        remark=teacher.remark,
        created_at=teacher.created_at,
    )


@router.get("", response_model=PageResult[TeacherOut], summary="教职工分页列表")
def list_teachers(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按工号、姓名或电话模糊查询"),
    department_id: int | None = Query(None, description="按部门筛选"),
    status: str | None = Query(None, description="按在职状态筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字/部门/状态筛选，分页返回教职工列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(
                BaseTeacher.teacher_no.ilike(like),
                BaseTeacher.name.ilike(like),
                BaseTeacher.phone.ilike(like),
            )
        )
    if department_id:
        conditions.append(BaseTeacher.department_id == department_id)
    if status:
        conditions.append(BaseTeacher.status == status)

    total = (
        db.scalar(select(func.count()).select_from(BaseTeacher).where(*conditions)) or 0
    )
    rows = db.scalars(
        select(BaseTeacher)
        .where(*conditions)
        .order_by(BaseTeacher.teacher_no)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[TeacherOut](
        total=total, items=[_to_teacher_out(t) for t in rows]
    )


@router.get("/options", summary="教职工下拉选项")
def list_teacher_options(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简教职工列表。"""
    rows = db.scalars(select(BaseTeacher).order_by(BaseTeacher.teacher_no)).all()
    return [{"id": r.id, "name": r.name} for r in rows]


@router.post(
    "",
    response_model=TeacherOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增教职工",
)
def create_teacher(
    payload: TeacherCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增教职工，工号需唯一。"""
    if db.scalar(select(BaseTeacher).where(BaseTeacher.teacher_no == payload.teacher_no)):
        raise HTTPException(status_code=400, detail="工号已存在")
    if payload.department_id and db.get(BaseDepartment, payload.department_id) is None:
        raise HTTPException(status_code=400, detail="所选部门不存在")

    teacher = BaseTeacher(**payload.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return _to_teacher_out(teacher)


@router.put("/{teacher_id}", response_model=TeacherOut, summary="修改教职工")
def update_teacher(
    teacher_id: int,
    payload: TeacherUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改教职工档案。"""
    teacher = db.get(BaseTeacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="教职工不存在")

    data = payload.model_dump(exclude_unset=True)
    department_id = data.get("department_id")
    if department_id is not None and db.get(BaseDepartment, department_id) is None:
        raise HTTPException(status_code=400, detail="所选部门不存在")

    for field, value in data.items():
        setattr(teacher, field, value)
    db.commit()
    db.refresh(teacher)
    return _to_teacher_out(teacher)


@router.delete("/{teacher_id}", response_model=MessageOut, summary="删除教职工")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除教职工档案。"""
    teacher = db.get(BaseTeacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="教职工不存在")

    db.delete(teacher)
    db.commit()
    return MessageOut(message="删除成功")
