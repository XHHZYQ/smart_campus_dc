"""学生学籍路由：含基础信息、学籍信息与家庭信息（父母双方）。

写操作限系统管理员/教务管理员，读操作登录用户即可。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ROLE_ACADEMIC, ROLE_ADMIN, get_current_user, require_roles
from app.models import BaseClass, BaseGrade, BaseStudent, SysUser
from app.schemas import (
    MessageOut,
    PageResult,
    StudentCreate,
    StudentOut,
    StudentUpdate,
)

router = APIRouter(prefix="/students", tags=["学生学籍"])

# 写操作：系统管理员与教务管理员
editor = require_roles(ROLE_ADMIN, ROLE_ACADEMIC)


def _to_student_out(student: BaseStudent, db: Session) -> StudentOut:
    """组装学生返回体，填充班级名称与年级名称。"""
    class_name = ""
    grade_name = ""
    if student.class_id:
        cls = db.get(BaseClass, student.class_id)
        if cls:
            class_name = cls.name
            grade = db.get(BaseGrade, cls.grade_id)
            grade_name = grade.name if grade else ""

    return StudentOut(
        id=student.id,
        student_no=student.student_no,
        name=student.name,
        used_name=student.used_name,
        gender=student.gender,
        nation=student.nation,
        birth_date=student.birth_date,
        id_card=student.id_card,
        political_status=student.political_status,
        phone=student.phone,
        address=student.address,
        class_id=student.class_id,
        class_name=class_name,
        grade_name=grade_name,
        enroll_year=student.enroll_year,
        study_mode=student.study_mode,
        status=student.status,
        father_name=student.father_name,
        father_id_card=student.father_id_card,
        father_work_unit=student.father_work_unit,
        father_position=student.father_position,
        father_phone=student.father_phone,
        mother_name=student.mother_name,
        mother_id_card=student.mother_id_card,
        mother_work_unit=student.mother_work_unit,
        mother_position=student.mother_position,
        mother_phone=student.mother_phone,
        remark=student.remark,
        created_at=student.created_at,
    )


@router.get("", response_model=PageResult[StudentOut], summary="学生分页列表")
def list_students(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按学籍号、姓名或电话模糊查询"),
    class_id: int | None = Query(None, description="按班级筛选"),
    status: str | None = Query(None, description="按学籍状态筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按关键字/班级/学籍状态筛选，分页返回学生列表。"""
    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(
                BaseStudent.student_no.ilike(like),
                BaseStudent.name.ilike(like),
                BaseStudent.phone.ilike(like),
            )
        )
    if class_id:
        conditions.append(BaseStudent.class_id == class_id)
    if status:
        conditions.append(BaseStudent.status == status)

    total = (
        db.scalar(select(func.count()).select_from(BaseStudent).where(*conditions)) or 0
    )
    rows = db.scalars(
        select(BaseStudent)
        .where(*conditions)
        .order_by(BaseStudent.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[StudentOut](
        total=total, items=[_to_student_out(s, db) for s in rows]
    )


@router.get("/options", summary="学生下拉选项")
def list_student_options(
    class_id: int | None = Query(None, description="按班级筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回 id + name 的精简学生列表（name 为“学籍号 姓名”）。"""
    stmt = select(BaseStudent)
    if class_id:
        stmt = stmt.where(BaseStudent.class_id == class_id)
    rows = db.scalars(stmt.order_by(BaseStudent.student_no)).all()
    return [{"id": r.id, "name": f"{r.student_no} {r.name}"} for r in rows]


@router.get("/{student_id}", response_model=StudentOut, summary="学生详情")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按 ID 查询学生完整信息。"""
    student = db.get(BaseStudent, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    return _to_student_out(student, db)


@router.post(
    "",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增学生",
)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """新增学生学籍，学籍号需唯一。"""
    if db.scalar(select(BaseStudent).where(BaseStudent.student_no == payload.student_no)):
        raise HTTPException(status_code=400, detail="学籍号已存在")
    if payload.class_id and db.get(BaseClass, payload.class_id) is None:
        raise HTTPException(status_code=400, detail="所选班级不存在")

    student = BaseStudent(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return _to_student_out(student, db)


@router.put("/{student_id}", response_model=StudentOut, summary="修改学生")
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改学生学籍信息。"""
    student = db.get(BaseStudent, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="学生不存在")

    data = payload.model_dump(exclude_unset=True)
    class_id = data.get("class_id")
    if class_id is not None and db.get(BaseClass, class_id) is None:
        raise HTTPException(status_code=400, detail="所选班级不存在")

    for field, value in data.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return _to_student_out(student, db)


@router.delete("/{student_id}", response_model=MessageOut, summary="删除学生")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除学生学籍。"""
    student = db.get(BaseStudent, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="学生不存在")

    db.delete(student)
    db.commit()
    return MessageOut(message="删除成功")
