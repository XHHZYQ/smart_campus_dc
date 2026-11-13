"""Pydantic 请求/响应模型（前后端接口契约的唯一事实源）。

约定：
- XxxCreate：新增请求体
- XxxUpdate：修改请求体（字段全部可选）
- XxxOut：返回体
- 分页统一返回 PageResult，结构为 { "total": 总数, "items": [...] }
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_serializer

T = TypeVar("T")


def format_datetime(value: datetime | None) -> str | None:
    """把日期时间统一格式化为 YYYY-MM-DD HH:mm:ss 字符串。"""
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


class PageResult(BaseModel, Generic[T]):
    """通用分页返回结构。"""

    total: int = Field(description="总记录数")
    items: list[T] = Field(description="当前页数据")


class MessageOut(BaseModel):
    """通用消息返回结构。"""

    message: str


# ====================================================================
# 一、认证与用户
# ====================================================================


class LoginRequest(BaseModel):
    """登录请求。"""

    username: str = Field(min_length=2, max_length=50, description="登录账号")
    password: str = Field(min_length=4, max_length=64, description="登录密码")


class UserProfile(BaseModel):
    """登录用户信息。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str
    role_id: int
    role_name: str = ""
    role_code: str = ""
    teacher_id: int | None = None
    phone: str | None = None
    email: str | None = None
    status: str
    last_login_at: datetime | None = None


class LoginResponse(BaseModel):
    """登录返回：令牌 + 用户信息 + 可访问菜单。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="有效期（秒）")
    user: UserProfile
    menus: list[str] = Field(default_factory=list, description="允许访问的菜单编码")


class ChangePasswordRequest(BaseModel):
    """修改密码请求。"""

    old_password: str = Field(min_length=4, max_length=64)
    new_password: str = Field(min_length=4, max_length=64)


class RoleCreate(BaseModel):
    """新增角色。"""

    name: str = Field(min_length=2, max_length=50)
    code: str = Field(min_length=2, max_length=50)
    description: str | None = None
    sort_order: int = 0


class RoleUpdate(BaseModel):
    """修改角色。"""

    name: str | None = None
    code: str | None = None
    description: str | None = None
    sort_order: int | None = None


class RoleOut(BaseModel):
    """角色返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    description: str | None = None
    sort_order: int = 0
    created_at: datetime | None = None


class UserCreate(BaseModel):
    """新增系统用户。"""

    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=4, max_length=64)
    real_name: str = Field(min_length=2, max_length=50)
    role_id: int
    teacher_id: int | None = None
    phone: str | None = None
    email: str | None = None
    status: str = "启用"


class UserUpdate(BaseModel):
    """修改系统用户。"""

    real_name: str | None = None
    role_id: int | None = None
    teacher_id: int | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None


class UserOut(BaseModel):
    """系统用户返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str
    role_id: int
    role_name: str = ""
    teacher_id: int | None = None
    phone: str | None = None
    email: str | None = None
    status: str
    last_login_at: datetime | None = None
    created_at: datetime | None = None


class ResetPasswordRequest(BaseModel):
    """重置密码请求。"""

    new_password: str = Field(min_length=4, max_length=64, description="新密码")


class OperationLogOut(BaseModel):
    """操作日志返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None = None
    real_name: str | None = None
    module: str | None = None
    action: str | None = None
    method: str | None = None
    path: str | None = None
    ip: str | None = None
    detail: str | None = None
    success: bool = True
    created_at: datetime | None = None

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime | None) -> str | None:
        return format_datetime(value)


class LoginLogOut(BaseModel):
    """登录日志返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None = None
    ip: str | None = None
    user_agent: str | None = None
    success: bool = True
    message: str | None = None
    created_at: datetime | None = None

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime | None) -> str | None:
        return format_datetime(value)


# ====================================================================
# 二、基础数据
# ====================================================================


class DepartmentCreate(BaseModel):
    """新增部门/教研组。"""

    name: str = Field(min_length=2, max_length=50)
    code: str = Field(min_length=1, max_length=30)
    dept_type: str = "行政科室"
    leader: str | None = None
    phone: str | None = None
    sort_order: int = 0
    remark: str | None = None


class DepartmentUpdate(BaseModel):
    """修改部门/教研组。"""

    name: str | None = None
    code: str | None = None
    dept_type: str | None = None
    leader: str | None = None
    phone: str | None = None
    sort_order: int | None = None
    remark: str | None = None


class DepartmentOut(BaseModel):
    """部门返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    dept_type: str
    leader: str | None = None
    phone: str | None = None
    sort_order: int = 0
    remark: str | None = None
    created_at: datetime | None = None


class GradeCreate(BaseModel):
    """新增年级。"""

    name: str = Field(min_length=1, max_length=20)
    code: str = Field(min_length=1, max_length=20)
    stage: str
    grade_level: int = Field(ge=1, le=12)
    head_teacher_id: int | None = None


class GradeUpdate(BaseModel):
    """修改年级。"""

    name: str | None = None
    code: str | None = None
    stage: str | None = None
    grade_level: int | None = None
    head_teacher_id: int | None = None


class GradeOut(BaseModel):
    """年级返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    stage: str
    grade_level: int
    head_teacher_id: int | None = None
    head_teacher_name: str = ""
    class_count: int = 0
    created_at: datetime | None = None


class ClassCreate(BaseModel):
    """新增班级。"""

    name: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1, max_length=30)
    grade_id: int
    room: str | None = None
    head_teacher_id: int | None = None
    enroll_year: int | None = None
    remark: str | None = None


class ClassUpdate(BaseModel):
    """修改班级。"""

    name: str | None = None
    code: str | None = None
    grade_id: int | None = None
    room: str | None = None
    head_teacher_id: int | None = None
    enroll_year: int | None = None
    remark: str | None = None


class ClassOut(BaseModel):
    """班级返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    grade_id: int
    grade_name: str = ""
    stage: str = ""
    room: str | None = None
    head_teacher_id: int | None = None
    head_teacher_name: str = ""
    student_count: int = 0
    enroll_year: int | None = None
    remark: str | None = None
    created_at: datetime | None = None


class SemesterCreate(BaseModel):
    """新增学期。"""

    name: str = Field(min_length=2, max_length=50)
    academic_year: str = Field(min_length=4, max_length=20)
    term: int = Field(ge=1, le=2)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False


class SemesterUpdate(BaseModel):
    """修改学期。"""

    name: str | None = None
    academic_year: str | None = None
    term: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None


class SemesterOut(BaseModel):
    """学期返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    academic_year: str
    term: int
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    created_at: datetime | None = None


class StudentCreate(BaseModel):
    """新增学生学籍。"""

    student_no: str = Field(min_length=4, max_length=32)
    name: str = Field(min_length=1, max_length=50)
    used_name: str | None = None
    gender: str = "男"
    nation: str = "汉族"
    birth_date: date | None = None
    id_card: str | None = None
    political_status: str | None = None
    phone: str | None = None
    address: str | None = None
    class_id: int | None = None
    enroll_year: int | None = None
    study_mode: str = "走读"
    status: str = "正常"
    father_name: str | None = None
    father_id_card: str | None = None
    father_work_unit: str | None = None
    father_position: str | None = None
    father_phone: str | None = None
    mother_name: str | None = None
    mother_id_card: str | None = None
    mother_work_unit: str | None = None
    mother_position: str | None = None
    mother_phone: str | None = None
    remark: str | None = None


class StudentUpdate(BaseModel):
    """修改学生学籍（字段全部可选）。"""

    name: str | None = None
    used_name: str | None = None
    gender: str | None = None
    nation: str | None = None
    birth_date: date | None = None
    id_card: str | None = None
    political_status: str | None = None
    phone: str | None = None
    address: str | None = None
    class_id: int | None = None
    enroll_year: int | None = None
    study_mode: str | None = None
    status: str | None = None
    father_name: str | None = None
    father_id_card: str | None = None
    father_work_unit: str | None = None
    father_position: str | None = None
    father_phone: str | None = None
    mother_name: str | None = None
    mother_id_card: str | None = None
    mother_work_unit: str | None = None
    mother_position: str | None = None
    mother_phone: str | None = None
    remark: str | None = None


class StudentOut(BaseModel):
    """学生学籍返回体（含班级与年级名称）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    student_no: str
    name: str
    used_name: str | None = None
    gender: str
    nation: str
    birth_date: date | None = None
    id_card: str | None = None
    political_status: str | None = None
    phone: str | None = None
    address: str | None = None
    class_id: int | None = None
    class_name: str = ""
    grade_name: str = ""
    enroll_year: int | None = None
    study_mode: str
    status: str
    father_name: str | None = None
    father_id_card: str | None = None
    father_work_unit: str | None = None
    father_position: str | None = None
    father_phone: str | None = None
    mother_name: str | None = None
    mother_id_card: str | None = None
    mother_work_unit: str | None = None
    mother_position: str | None = None
    mother_phone: str | None = None
    remark: str | None = None
    created_at: datetime | None = None


class TeacherCreate(BaseModel):
    """新增教职工。"""

    teacher_no: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=1, max_length=50)
    gender: str = "男"
    department_id: int | None = None
    subject: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    hire_date: date | None = None
    status: str = "在职"
    remark: str | None = None


class TeacherUpdate(BaseModel):
    """修改教职工。"""

    name: str | None = None
    gender: str | None = None
    department_id: int | None = None
    subject: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    hire_date: date | None = None
    status: str | None = None
    remark: str | None = None


class TeacherOut(BaseModel):
    """教职工返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_no: str
    name: str
    gender: str
    department_id: int | None = None
    department_name: str = ""
    subject: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    hire_date: date | None = None
    status: str
    remark: str | None = None
    created_at: datetime | None = None


# ====================================================================
# 三、教学管理
# ====================================================================


class CourseCreate(BaseModel):
    """新增学科课程。"""

    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=50)
    stage: str
    department_id: int | None = None
    weekly_hours: int = 2
    course_type: str = "必修"
    teacher_id: int | None = None


class CourseUpdate(BaseModel):
    """修改学科课程。"""

    name: str | None = None
    stage: str | None = None
    department_id: int | None = None
    weekly_hours: int | None = None
    course_type: str | None = None
    teacher_id: int | None = None


class CourseOut(BaseModel):
    """学科课程返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    stage: str
    department_id: int | None = None
    department_name: str = ""
    weekly_hours: int
    course_type: str
    teacher_id: int | None = None
    teacher_name: str = ""
    created_at: datetime | None = None


class ScheduleCreate(BaseModel):
    """新增排课记录。"""

    semester_id: int
    class_id: int
    course_id: int
    teacher_id: int | None = None
    weekday: int = Field(ge=1, le=5, description="星期 1~5")
    period: int = Field(ge=1, le=8, description="节次 1~8")
    room: str | None = None


class ScheduleUpdate(BaseModel):
    """修改排课记录。"""

    semester_id: int | None = None
    class_id: int | None = None
    course_id: int | None = None
    teacher_id: int | None = None
    weekday: int | None = None
    period: int | None = None
    room: str | None = None


class ScheduleOut(BaseModel):
    """排课返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    semester_id: int
    semester_name: str = ""
    class_id: int
    class_name: str = ""
    course_id: int
    course_name: str = ""
    teacher_id: int | None = None
    teacher_name: str = ""
    weekday: int
    period: int
    room: str | None = None
    created_at: datetime | None = None


class TimetableCell(BaseModel):
    """周课表中的一格。"""

    weekday: int = 1
    period: int
    course_name: str = ""
    teacher_name: str = ""
    room: str = ""


class TimetableRow(BaseModel):
    """周课表中的一行（一个节次）。"""

    period: int
    weekday_cells: list[TimetableCell] = Field(default_factory=list)


class ScoreCreate(BaseModel):
    """新增成绩。"""

    student_id: int
    course_id: int
    semester_id: int
    exam_type: str = "期末"
    score: Decimal | None = None
    remark: str | None = None


class ScoreUpdate(BaseModel):
    """修改成绩。"""

    exam_type: str | None = None
    score: Decimal | None = None
    remark: str | None = None


class ScoreOut(BaseModel):
    """成绩返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    student_no: str = ""
    student_name: str = ""
    class_name: str = ""
    course_id: int
    course_name: str = ""
    semester_id: int
    semester_name: str = ""
    exam_type: str
    score: Decimal | None = None
    remark: str | None = None
    created_at: datetime | None = None


class BatchScoreItem(BaseModel):
    """批量录入中的一条成绩。"""

    student_id: int
    score: Decimal | None = None
    remark: str | None = None


class BatchScoreRequest(BaseModel):
    """批量录入成绩请求：同一班级、同一课程、同一学期。"""

    class_id: int
    course_id: int
    semester_id: int
    exam_type: str = "期末"
    items: list[BatchScoreItem]


class AttendanceCreate(BaseModel):
    """新增考勤记录。"""

    student_id: int
    course_id: int
    attend_date: date
    status: str = "正常"
    remark: str | None = None


class AttendanceUpdate(BaseModel):
    """修改考勤记录。"""

    status: str | None = None
    remark: str | None = None


class AttendanceOut(BaseModel):
    """考勤返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    student_no: str = ""
    student_name: str = ""
    class_name: str = ""
    course_id: int
    course_name: str = ""
    attend_date: date
    status: str
    remark: str | None = None
    created_at: datetime | None = None


# ====================================================================
# 四、校务管理
# ====================================================================


class AssetCreate(BaseModel):
    """新增资产。"""

    asset_no: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=1, max_length=100)
    category: str
    brand: str | None = None
    model: str | None = None
    price: Decimal | None = None
    quantity: int = 1
    purchase_date: date | None = None
    department_id: int | None = None
    keeper: str | None = None
    status: str = "在用"
    location: str | None = None


class AssetUpdate(BaseModel):
    """修改资产。"""

    name: str | None = None
    category: str | None = None
    brand: str | None = None
    model: str | None = None
    price: Decimal | None = None
    quantity: int | None = None
    purchase_date: date | None = None
    department_id: int | None = None
    keeper: str | None = None
    status: str | None = None
    location: str | None = None


class AssetOut(BaseModel):
    """资产返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_no: str
    name: str
    category: str
    brand: str | None = None
    model: str | None = None
    price: Decimal | None = None
    quantity: int = 1
    purchase_date: date | None = None
    department_id: int | None = None
    department_name: str = ""
    keeper: str | None = None
    status: str
    location: str | None = None
    created_at: datetime | None = None


class DormRoomCreate(BaseModel):
    """新增宿舍房间。"""

    building: str = Field(min_length=1, max_length=30)
    room_no: str = Field(min_length=1, max_length=20)
    floor: int | None = None
    capacity: int = 6
    gender_type: str = "男"
    remark: str | None = None


class DormRoomUpdate(BaseModel):
    """修改宿舍房间。"""

    building: str | None = None
    room_no: str | None = None
    floor: int | None = None
    capacity: int | None = None
    gender_type: str | None = None
    remark: str | None = None


class DormRoomOut(BaseModel):
    """宿舍房间返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    building: str
    room_no: str
    floor: int | None = None
    capacity: int
    occupied: int = 0
    gender_type: str
    remark: str | None = None
    created_at: datetime | None = None


class DormAllocationCreate(BaseModel):
    """新增住宿分配。"""

    student_id: int
    room_id: int
    bed_no: str | None = None
    check_in_date: date | None = None
    status: str = "在住"


class DormAllocationUpdate(BaseModel):
    """修改住宿分配。"""

    room_id: int | None = None
    bed_no: str | None = None
    check_in_date: date | None = None
    status: str | None = None


class DormAllocationOut(BaseModel):
    """住宿分配返回体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    student_no: str = ""
    student_name: str = ""
    class_name: str = ""
    room_id: int
    building: str = ""
    room_no: str = ""
    bed_no: str | None = None
    check_in_date: date | None = None
    status: str
    created_at: datetime | None = None


# ====================================================================
# 五、数据看板
# ====================================================================


class NameValue(BaseModel):
    """名称-数值对，用于饼图/柱状图。"""

    name: str
    value: float


class OverviewOut(BaseModel):
    """首页概览指标。"""

    student_total: int
    teacher_total: int
    class_total: int
    grade_total: int
    asset_count: int
    asset_amount: float
    dorm_room_total: int
    dorm_bed_total: int
    dorm_occupied: int
    current_semester: str


class StudentCompositionOut(BaseModel):
    """学生构成分析。"""

    by_stage: list[NameValue]
    by_grade: list[NameValue]
    by_gender: list[NameValue]
    by_study_mode: list[NameValue]
    by_status: list[NameValue]


class ScoreDistributionItem(BaseModel):
    """分数段分布项。"""

    range_name: str
    count: int


class CourseScoreItem(BaseModel):
    """按课程统计的成绩指标。"""

    course_name: str
    average: float
    pass_rate: float
    excellent_rate: float
    count: int


class ScoreAnalysisOut(BaseModel):
    """成绩分析。"""

    by_course: list[CourseScoreItem]
    distribution: list[ScoreDistributionItem]
    semester_trend: list[NameValue]


class AssetStatisticsOut(BaseModel):
    """资产统计。"""

    by_category: list[NameValue]
    by_department: list[NameValue]
    by_status: list[NameValue]
    amount_by_category: list[NameValue]


class ScreenOut(BaseModel):
    """数据大屏聚合数据。"""

    student_total: int
    teacher_total: int
    class_total: int
    asset_amount: float
    by_stage: list[NameValue]
    by_grade: list[NameValue]
    by_gender: list[NameValue]
    asset_by_category: list[NameValue]
    avg_score_by_course: list[NameValue]
    attendance_by_status: list[NameValue]
