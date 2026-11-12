"""成绩管理路由：成绩的查询、单条录入、批量录入与增删改。

写操作允许系统管理员/教务管理员/班主任/任课教师，读操作登录用户即可。
批量录入按“学生 + 课程 + 学期 + 考试类型”已存在则更新、否则新增。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import (
    ROLE_ACADEMIC,
    ROLE_ADMIN,
    ROLE_HEAD_TEACHER,
    ROLE_SUBJECT_TEACHER,
    get_current_user,
    require_roles,
)
from app.models import (
    BaseClass,
    BaseSemester,
    BaseStudent,
    EduCourse,
    EduScore,
    SysUser,
)
from app.schemas import (
    BatchScoreRequest,
    MessageOut,
    PageResult,
    ScoreCreate,
    ScoreOut,
    ScoreUpdate,
)

router = APIRouter(prefix="/scores", tags=["成绩管理"])

# 写操作：系统管理员、教务管理员、班主任、任课教师
editor = require_roles(
    ROLE_ADMIN, ROLE_ACADEMIC, ROLE_HEAD_TEACHER, ROLE_SUBJECT_TEACHER
)


def _to_score_out(score: EduScore, db: Session) -> ScoreOut:
    """组装成绩返回体，填充学籍号、学生姓名、班级、课程与学期名称。"""
    out = ScoreOut.model_validate(score)
    student = db.get(BaseStudent, score.student_id)
    if student:
        out.student_no = student.student_no
        out.student_name = student.name
        if student.class_id:
            cls = db.get(BaseClass, student.class_id)
            out.class_name = cls.name if cls else ""
    course = db.get(EduCourse, score.course_id)
    out.course_name = course.name if course else ""
    semester = db.get(BaseSemester, score.semester_id)
    out.semester_name = semester.name if semester else ""
    return out


@router.get("", response_model=PageResult[ScoreOut], summary="成绩分页列表")
def list_scores(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    student_id: int | None = Query(None, description="按学生筛选"),
    class_id: int | None = Query(None, description="按班级筛选"),
    course_id: int | None = Query(None, description="按课程筛选"),
    semester_id: int | None = Query(None, description="按学期筛选"),
    exam_type: str | None = Query(None, description="按考试类型筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按学生/班级/课程/学期/考试类型筛选，分页返回成绩列表。"""
    conditions = []
    if student_id:
        conditions.append(EduScore.student_id == student_id)
    if class_id:
        student_ids = select(BaseStudent.id).where(BaseStudent.class_id == class_id)
        conditions.append(EduScore.student_id.in_(student_ids))
    if course_id:
        conditions.append(EduScore.course_id == course_id)
    if semester_id:
        conditions.append(EduScore.semester_id == semester_id)
    if exam_type:
        conditions.append(EduScore.exam_type == exam_type)

    total = db.scalar(select(func.count()).select_from(EduScore).where(*conditions)) or 0
    rows = db.scalars(
        select(EduScore)
        .where(*conditions)
        .order_by(EduScore.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PageResult[ScoreOut](total=total, items=[_to_score_out(s, db) for s in rows])


@router.post(
    "",
    response_model=ScoreOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增成绩",
)
def create_score(
    payload: ScoreCreate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """单条录入成绩。"""
    if db.get(BaseStudent, payload.student_id) is None:
        raise HTTPException(status_code=400, detail="所选学生不存在")
    if db.get(EduCourse, payload.course_id) is None:
        raise HTTPException(status_code=400, detail="所选课程不存在")
    if db.get(BaseSemester, payload.semester_id) is None:
        raise HTTPException(status_code=400, detail="所选学期不存在")

    score = EduScore(**payload.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return _to_score_out(score, db)


@router.post("/batch", response_model=MessageOut, summary="批量录入成绩")
def batch_create_scores(
    payload: BatchScoreRequest,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """批量录入成绩：已存在则更新，否则新增。"""
    if db.get(EduCourse, payload.course_id) is None:
        raise HTTPException(status_code=400, detail="所选课程不存在")
    if db.get(BaseSemester, payload.semester_id) is None:
        raise HTTPException(status_code=400, detail="所选学期不存在")

    created = 0
    updated = 0
    for item in payload.items:
        if db.get(BaseStudent, item.student_id) is None:
            continue
        existing = db.scalar(
            select(EduScore).where(
                EduScore.student_id == item.student_id,
                EduScore.course_id == payload.course_id,
                EduScore.semester_id == payload.semester_id,
                EduScore.exam_type == payload.exam_type,
            )
        )
        if existing:
            existing.score = item.score
            existing.remark = item.remark
            updated += 1
        else:
            db.add(
                EduScore(
                    student_id=item.student_id,
                    course_id=payload.course_id,
                    semester_id=payload.semester_id,
                    exam_type=payload.exam_type,
                    score=item.score,
                    remark=item.remark,
                )
            )
            created += 1

    db.commit()
    return MessageOut(message=f"批量录入完成：新增 {created} 条，更新 {updated} 条")


@router.put("/{score_id}", response_model=ScoreOut, summary="修改成绩")
def update_score(
    score_id: int,
    payload: ScoreUpdate,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """修改成绩。"""
    score = db.get(EduScore, score_id)
    if score is None:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(score, field, value)
    db.commit()
    db.refresh(score)
    return _to_score_out(score, db)


@router.delete("/{score_id}", response_model=MessageOut, summary="删除成绩")
def delete_score(
    score_id: int,
    db: Session = Depends(get_db),
    _: SysUser = Depends(editor),
):
    """删除成绩。"""
    score = db.get(EduScore, score_id)
    if score is None:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    db.delete(score)
    db.commit()
    return MessageOut(message="删除成功")
