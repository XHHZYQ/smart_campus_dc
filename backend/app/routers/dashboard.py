"""数据看板路由：首页概览、学生构成、成绩分析、资产统计与数据大屏。

全部为只读聚合查询，登录用户即可访问，无需额外写权限。
空数据与除零场景统一返回 0 或空列表，不抛异常。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import ColumnElement, case, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    AfAsset,
    AfDormRoom,
    BaseClass,
    BaseDepartment,
    BaseGrade,
    BaseSemester,
    BaseStudent,
    BaseTeacher,
    EduAttendance,
    EduCourse,
    EduScore,
    SysUser,
)
from app.schemas import (
    AssetStatisticsOut,
    CourseScoreItem,
    NameValue,
    OverviewOut,
    ScoreAnalysisOut,
    ScoreDistributionItem,
    ScreenOut,
    StudentCompositionOut,
)

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


def _name_values(rows) -> list[NameValue]:
    """把 (名称, 数值) 查询结果转换为 NameValue 列表。"""
    result: list[NameValue] = []
    for name, value in rows:
        label = str(name) if name not in (None, "") else "未填写"
        result.append(NameValue(name=label, value=float(value or 0)))
    return result


def _count_value(db: Session, stmt) -> int:
    """执行计数类语句，空值返回 0。"""
    return int(db.scalar(stmt) or 0)


def _sum_value(db: Session, stmt) -> float:
    """执行求和类语句，空值返回 0.0。"""
    return float(db.scalar(stmt) or 0)


def _students_by_stage(db: Session) -> list[NameValue]:
    """按学段（小学/初中/高中）统计学生人数。"""
    rows = db.execute(
        select(BaseGrade.stage, func.count(BaseStudent.id))
        .select_from(BaseStudent)
        .join(BaseClass, BaseStudent.class_id == BaseClass.id)
        .join(BaseGrade, BaseClass.grade_id == BaseGrade.id)
        .group_by(BaseGrade.stage)
        .order_by(BaseGrade.stage)
    ).all()
    return _name_values(rows)


def _students_by_grade(db: Session) -> list[NameValue]:
    """按年级统计学生人数，按年级序号升序排列。"""
    rows = db.execute(
        select(BaseGrade.name, func.count(BaseStudent.id))
        .select_from(BaseStudent)
        .join(BaseClass, BaseStudent.class_id == BaseClass.id)
        .join(BaseGrade, BaseClass.grade_id == BaseGrade.id)
        .group_by(BaseGrade.id, BaseGrade.name, BaseGrade.grade_level)
        .order_by(BaseGrade.grade_level)
    ).all()
    return _name_values(rows)


def _students_by_field(db: Session, column: ColumnElement) -> list[NameValue]:
    """按指定字段（性别/就读方式/学籍状态）统计学生人数。"""
    rows = db.execute(
        select(column, func.count(BaseStudent.id))
        .select_from(BaseStudent)
        .group_by(column)
    ).all()
    return _name_values(rows)


def _score_conditions(
    semester_id: int | None, exam_type: str | None
) -> list[ColumnElement]:
    """构造成绩统计的公共筛选条件（仅统计已录入分数的记录）。"""
    conditions: list[ColumnElement] = [EduScore.score.is_not(None)]
    if semester_id:
        conditions.append(EduScore.semester_id == semester_id)
    if exam_type:
        conditions.append(EduScore.exam_type == exam_type)
    return conditions


@router.get("/overview", response_model=OverviewOut, summary="首页概览指标")
def overview(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """返回首页概览所需的各类总量指标。"""
    student_total = _count_value(db, select(func.count()).select_from(BaseStudent))
    teacher_total = _count_value(db, select(func.count()).select_from(BaseTeacher))
    class_total = _count_value(db, select(func.count()).select_from(BaseClass))
    grade_total = _count_value(db, select(func.count()).select_from(BaseGrade))
    asset_count = _count_value(db, select(func.count()).select_from(AfAsset))
    asset_amount = _sum_value(db, select(func.sum(AfAsset.price)))
    dorm_room_total = _count_value(db, select(func.count()).select_from(AfDormRoom))
    dorm_bed_total = _count_value(db, select(func.sum(AfDormRoom.capacity)))
    dorm_occupied = _count_value(db, select(func.sum(AfDormRoom.occupied)))

    current = db.scalar(
        select(BaseSemester).where(BaseSemester.is_current == True)  # noqa: E712
    )
    return OverviewOut(
        student_total=student_total,
        teacher_total=teacher_total,
        class_total=class_total,
        grade_total=grade_total,
        asset_count=asset_count,
        asset_amount=asset_amount,
        dorm_room_total=dorm_room_total,
        dorm_bed_total=dorm_bed_total,
        dorm_occupied=dorm_occupied,
        current_semester=current.name if current else "",
    )


@router.get(
    "/student-composition",
    response_model=StudentCompositionOut,
    summary="学生构成分析",
)
def student_composition(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按学段、年级、性别、就读方式与学籍状态统计学生构成。"""
    return StudentCompositionOut(
        by_stage=_students_by_stage(db),
        by_grade=_students_by_grade(db),
        by_gender=_students_by_field(db, BaseStudent.gender),
        by_study_mode=_students_by_field(db, BaseStudent.study_mode),
        by_status=_students_by_field(db, BaseStudent.status),
    )


@router.get("/score-analysis", response_model=ScoreAnalysisOut, summary="成绩分析")
def score_analysis(
    semester_id: int | None = Query(None, description="按学期筛选"),
    exam_type: str | None = Query(None, description="按考试类型筛选"),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按学科统计平均分/及格率/优秀率，并给出分数段分布与学期趋势。"""
    conditions = _score_conditions(semester_id, exam_type)

    # 按学科统计平均分、及格率（>=60）、优秀率（>=85）
    course_rows = db.execute(
        select(
            EduCourse.name,
            func.avg(EduScore.score),
            func.count(EduScore.score),
            func.sum(case((EduScore.score >= 60, 1), else_=0)),
            func.sum(case((EduScore.score >= 85, 1), else_=0)),
        )
        .select_from(EduScore)
        .join(EduCourse, EduScore.course_id == EduCourse.id)
        .where(*conditions)
        .group_by(EduCourse.id, EduCourse.name)
        .order_by(EduCourse.name)
    ).all()
    by_course: list[CourseScoreItem] = []
    for course_name, avg_val, cnt, pass_cnt, excellent_cnt in course_rows:
        total = int(cnt or 0)
        by_course.append(
            CourseScoreItem(
                course_name=course_name,
                average=round(float(avg_val or 0), 2),
                pass_rate=round(int(pass_cnt or 0) / total * 100, 2) if total else 0.0,
                excellent_rate=(
                    round(int(excellent_cnt or 0) / total * 100, 2) if total else 0.0
                ),
                count=total,
            )
        )

    # 分数段分布
    ranges: list[tuple[str, ColumnElement]] = [
        ("60 分以下", EduScore.score < 60),
        ("60-69 分", (EduScore.score >= 60) & (EduScore.score < 70)),
        ("70-79 分", (EduScore.score >= 70) & (EduScore.score < 80)),
        ("80-89 分", (EduScore.score >= 80) & (EduScore.score < 90)),
        ("90-100 分", EduScore.score >= 90),
    ]
    distribution: list[ScoreDistributionItem] = []
    for label, cond in ranges:
        count = _count_value(
            db, select(func.count()).select_from(EduScore).where(*conditions, cond)
        )
        distribution.append(ScoreDistributionItem(range_name=label, count=count))

    # 各学期平均分趋势（按学年、学期升序）
    trend_rows = db.execute(
        select(BaseSemester.name, func.avg(EduScore.score))
        .select_from(EduScore)
        .join(BaseSemester, EduScore.semester_id == BaseSemester.id)
        .where(*conditions)
        .group_by(
            BaseSemester.id,
            BaseSemester.name,
            BaseSemester.academic_year,
            BaseSemester.term,
        )
        .order_by(BaseSemester.academic_year, BaseSemester.term)
    ).all()

    return ScoreAnalysisOut(
        by_course=by_course,
        distribution=distribution,
        semester_trend=_name_values(trend_rows),
    )


@router.get(
    "/asset-statistics", response_model=AssetStatisticsOut, summary="资产统计"
)
def asset_statistics(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """按分类、部门、状态统计资产数量与金额。"""
    by_category = _name_values(
        db.execute(
            select(AfAsset.category, func.count(AfAsset.id))
            .select_from(AfAsset)
            .group_by(AfAsset.category)
            .order_by(AfAsset.category)
        ).all()
    )
    amount_by_category = _name_values(
        db.execute(
            select(AfAsset.category, func.sum(AfAsset.price))
            .select_from(AfAsset)
            .group_by(AfAsset.category)
            .order_by(AfAsset.category)
        ).all()
    )
    by_department = _name_values(
        db.execute(
            select(BaseDepartment.name, func.count(AfAsset.id))
            .select_from(AfAsset)
            .join(BaseDepartment, AfAsset.department_id == BaseDepartment.id)
            .group_by(BaseDepartment.id, BaseDepartment.name)
            .order_by(BaseDepartment.name)
        ).all()
    )
    by_status = _name_values(
        db.execute(
            select(AfAsset.status, func.count(AfAsset.id))
            .select_from(AfAsset)
            .group_by(AfAsset.status)
        ).all()
    )
    return AssetStatisticsOut(
        by_category=by_category,
        by_department=by_department,
        by_status=by_status,
        amount_by_category=amount_by_category,
    )


@router.get("/screen", response_model=ScreenOut, summary="数据大屏聚合数据")
def screen(
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    """一次性返回数据大屏所需的合并指标。"""
    student_total = _count_value(db, select(func.count()).select_from(BaseStudent))
    teacher_total = _count_value(db, select(func.count()).select_from(BaseTeacher))
    class_total = _count_value(db, select(func.count()).select_from(BaseClass))
    asset_amount = _sum_value(db, select(func.sum(AfAsset.price)))

    asset_by_category = _name_values(
        db.execute(
            select(AfAsset.category, func.sum(AfAsset.price))
            .select_from(AfAsset)
            .group_by(AfAsset.category)
            .order_by(func.sum(AfAsset.price).desc())
        ).all()
    )

    avg_score_rows = db.execute(
        select(EduCourse.name, func.avg(EduScore.score))
        .select_from(EduScore)
        .join(EduCourse, EduScore.course_id == EduCourse.id)
        .where(EduScore.score.is_not(None))
        .group_by(EduCourse.id, EduCourse.name)
        .order_by(EduCourse.name)
    ).all()

    attendance_by_status = _name_values(
        db.execute(
            select(EduAttendance.status, func.count(EduAttendance.id))
            .select_from(EduAttendance)
            .group_by(EduAttendance.status)
        ).all()
    )

    return ScreenOut(
        student_total=student_total,
        teacher_total=teacher_total,
        class_total=class_total,
        asset_amount=asset_amount,
        by_stage=_students_by_stage(db),
        by_grade=_students_by_grade(db),
        by_gender=_students_by_field(db, BaseStudent.gender),
        asset_by_category=asset_by_category,
        avg_score_by_course=_name_values(avg_score_rows),
        attendance_by_status=attendance_by_status,
    )
