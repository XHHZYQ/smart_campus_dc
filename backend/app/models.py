"""数据表模型定义（共 17 张表）。

命名规范：
- 表名统一加模块前缀：sys_ 系统管理、base_ 基础数据、edu_ 教学管理、af_ 校务管理
- 主键统一为 id（自增 BIGINT）
- 外键统一为 表名_id，例如 class_id、teacher_id
- 时间字段统一为 created_at / updated_at
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ====================================================================
# 一、系统管理模块（sys_）
# ====================================================================


class SysRole(Base):
    """角色表：定义系统中的角色与权限标识。"""

    __tablename__ = "sys_role"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="角色名称")
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="角色编码"
    )
    description: Mapped[str | None] = mapped_column(String(200), comment="角色说明")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序号")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    users: Mapped[list["SysUser"]] = relationship(back_populates="role")


class SysUser(Base):
    """系统用户表：登录账号，绑定角色，可关联教职工档案。"""

    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="登录账号"
    )
    password_hash: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="密码哈希（bcrypt）"
    )
    real_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="姓名")
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sys_role.id"), nullable=False, comment="所属角色"
    )
    teacher_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_teacher.id"), comment="关联教职工"
    )
    phone: Mapped[str | None] = mapped_column(String(20), comment="联系电话")
    email: Mapped[str | None] = mapped_column(String(100), comment="电子邮箱")
    status: Mapped[str] = mapped_column(
        String(16), default="启用", comment="账号状态：启用/停用"
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, comment="最后登录时间")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), comment="更新时间"
    )

    role: Mapped["SysRole"] = relationship(back_populates="users")


class SysOperationLog(Base):
    """操作日志表：记录用户在系统中的增删改操作。"""

    __tablename__ = "sys_operation_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, comment="操作人ID")
    username: Mapped[str | None] = mapped_column(String(50), comment="操作人账号")
    real_name: Mapped[str | None] = mapped_column(String(50), comment="操作人姓名")
    module: Mapped[str | None] = mapped_column(String(50), comment="功能模块")
    action: Mapped[str | None] = mapped_column(String(50), comment="操作类型")
    method: Mapped[str | None] = mapped_column(String(10), comment="请求方法")
    path: Mapped[str | None] = mapped_column(String(200), comment="请求路径")
    ip: Mapped[str | None] = mapped_column(String(50), comment="客户端IP")
    detail: Mapped[str | None] = mapped_column(Text, comment="操作详情")
    success: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否成功")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="操作时间"
    )


class SysLoginLog(Base):
    """登录日志表：记录登录尝试的结果。"""

    __tablename__ = "sys_login_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(String(50), comment="登录账号")
    ip: Mapped[str | None] = mapped_column(String(50), comment="客户端IP")
    user_agent: Mapped[str | None] = mapped_column(String(300), comment="浏览器标识")
    success: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否成功")
    message: Mapped[str | None] = mapped_column(String(200), comment="提示信息")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="登录时间"
    )


# ====================================================================
# 二、基础数据模块（base_）
# ====================================================================


class BaseDepartment(Base):
    """部门/教研组表：行政科室与学科教研组。"""

    __tablename__ = "base_department"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="部门名称")
    code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, comment="部门编码"
    )
    dept_type: Mapped[str] = mapped_column(
        String(20), default="行政科室", comment="类型：行政科室/教研组"
    )
    leader: Mapped[str | None] = mapped_column(String(50), comment="负责人")
    phone: Mapped[str | None] = mapped_column(String(20), comment="联系电话")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序号")
    remark: Mapped[str | None] = mapped_column(String(200), comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    teachers: Mapped[list["BaseTeacher"]] = relationship(back_populates="department")


class BaseGrade(Base):
    """年级表：一年级至高三，共 12 个年级。"""

    __tablename__ = "base_grade"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="年级名称")
    code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="年级编码"
    )
    stage: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="所属学段：小学/初中/高中"
    )
    grade_level: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="年级序号 1~12"
    )
    head_teacher_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_teacher.id"), comment="年级组长"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    classes: Mapped[list["BaseClass"]] = relationship(back_populates="grade")


class BaseClass(Base):
    """班级表：挂在年级之下。"""

    __tablename__ = "base_class"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="班级名称")
    code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, comment="班级编码"
    )
    grade_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("base_grade.id"), nullable=False, comment="所属年级"
    )
    room: Mapped[str | None] = mapped_column(String(50), comment="教室")
    head_teacher_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_teacher.id"), comment="班主任"
    )
    student_count: Mapped[int] = mapped_column(Integer, default=0, comment="班级人数")
    enroll_year: Mapped[int | None] = mapped_column(Integer, comment="入学年份")
    remark: Mapped[str | None] = mapped_column(String(200), comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    grade: Mapped["BaseGrade"] = relationship(back_populates="classes")
    students: Mapped[list["BaseStudent"]] = relationship(back_populates="class_")


class BaseSemester(Base):
    """学期表：学年学期维护。"""

    __tablename__ = "base_semester"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="学期名称")
    academic_year: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="学年，如 2025-2026"
    )
    term: Mapped[int] = mapped_column(Integer, nullable=False, comment="学期：1 秋季 2 春季")
    start_date: Mapped[date | None] = mapped_column(Date, comment="开始日期")
    end_date: Mapped[date | None] = mapped_column(Date, comment="结束日期")
    is_current: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否当前学期"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )


class BaseStudent(Base):
    """学生学籍表：含基础信息、学籍信息与家庭信息（父母双方）。"""

    __tablename__ = "base_student"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="学籍号"
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="姓名")
    used_name: Mapped[str | None] = mapped_column(String(50), comment="曾用名")
    gender: Mapped[str] = mapped_column(String(4), nullable=False, comment="性别")
    nation: Mapped[str] = mapped_column(String(20), default="汉族", comment="民族")
    birth_date: Mapped[date | None] = mapped_column(Date, comment="出生日期")
    id_card: Mapped[str | None] = mapped_column(String(20), comment="身份证件号")
    political_status: Mapped[str | None] = mapped_column(
        String(16), comment="政治面貌：少先队员/共青团员/群众"
    )
    phone: Mapped[str | None] = mapped_column(String(20), comment="联系电话")
    address: Mapped[str | None] = mapped_column(String(200), comment="现居住地址")
    class_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_class.id"), comment="所属班级"
    )
    enroll_year: Mapped[int | None] = mapped_column(Integer, comment="入学年份")
    study_mode: Mapped[str] = mapped_column(
        String(10), default="走读", comment="就读方式：走读/住校"
    )
    status: Mapped[str] = mapped_column(
        String(16), default="正常", comment="学籍状态：正常/休学/转学/退学/毕业"
    )
    # 家庭信息 —— 父亲
    father_name: Mapped[str | None] = mapped_column(String(50), comment="父亲姓名")
    father_id_card: Mapped[str | None] = mapped_column(String(20), comment="父亲身份证件号")
    father_work_unit: Mapped[str | None] = mapped_column(String(100), comment="父亲工作单位")
    father_position: Mapped[str | None] = mapped_column(String(50), comment="父亲职务")
    father_phone: Mapped[str | None] = mapped_column(String(20), comment="父亲联系电话")
    # 家庭信息 —— 母亲
    mother_name: Mapped[str | None] = mapped_column(String(50), comment="母亲姓名")
    mother_id_card: Mapped[str | None] = mapped_column(String(20), comment="母亲身份证件号")
    mother_work_unit: Mapped[str | None] = mapped_column(String(100), comment="母亲工作单位")
    mother_position: Mapped[str | None] = mapped_column(String(50), comment="母亲职务")
    mother_phone: Mapped[str | None] = mapped_column(String(20), comment="母亲联系电话")
    remark: Mapped[str | None] = mapped_column(String(200), comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), comment="更新时间"
    )

    class_: Mapped["BaseClass | None"] = relationship(back_populates="students")


class BaseTeacher(Base):
    """教职工表：教师与行政人员档案。"""

    __tablename__ = "base_teacher"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    teacher_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="工号"
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="姓名")
    gender: Mapped[str] = mapped_column(String(4), nullable=False, comment="性别")
    department_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_department.id"), comment="所属部门"
    )
    subject: Mapped[str | None] = mapped_column(String(30), comment="任教学科")
    title: Mapped[str | None] = mapped_column(String(30), comment="职称")
    phone: Mapped[str | None] = mapped_column(String(20), comment="联系电话")
    email: Mapped[str | None] = mapped_column(String(100), comment="电子邮箱")
    hire_date: Mapped[date | None] = mapped_column(Date, comment="入职时间")
    status: Mapped[str] = mapped_column(
        String(16), default="在职", comment="在职状态：在职/离职/退休"
    )
    remark: Mapped[str | None] = mapped_column(String(200), comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    department: Mapped["BaseDepartment | None"] = relationship(back_populates="teachers")


# ====================================================================
# 三、教学管理模块（edu_）
# ====================================================================


class EduCourse(Base):
    """学科课程表：学校的课程库。"""

    __tablename__ = "edu_course"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, comment="课程代码"
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="课程名称")
    stage: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="适用学段：小学/初中/高中"
    )
    department_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_department.id"), comment="开课教研组"
    )
    weekly_hours: Mapped[int] = mapped_column(Integer, default=2, comment="周课时")
    course_type: Mapped[str] = mapped_column(
        String(16), default="必修", comment="课程性质：必修/选修/活动"
    )
    teacher_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_teacher.id"), comment="任课教师"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )


class EduSchedule(Base):
    """排课表：课程 + 班级 + 学期 + 星期 + 节次。"""

    __tablename__ = "edu_schedule"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    semester_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("base_semester.id"), nullable=False, comment="学期"
    )
    class_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("base_class.id"), nullable=False, comment="班级"
    )
    course_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("edu_course.id"), nullable=False, comment="课程"
    )
    teacher_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_teacher.id"), comment="任课教师"
    )
    weekday: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="星期：1~5 表示周一至周五"
    )
    period: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="节次：1~8 表示第1节至第8节"
    )
    room: Mapped[str | None] = mapped_column(String(50), comment="上课教室")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )


class EduScore(Base):
    """成绩表：学生 + 课程 + 学期 + 考试类型的成绩记录。"""

    __tablename__ = "edu_score"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("base_student.id"), nullable=False, comment="学生"
    )
    course_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("edu_course.id"), nullable=False, comment="课程"
    )
    semester_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("base_semester.id"), nullable=False, comment="学期"
    )
    exam_type: Mapped[str] = mapped_column(
        String(16), default="期末", comment="考试类型：月考/期中/期末/单元测"
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), comment="成绩（百分制）")
    remark: Mapped[str | None] = mapped_column(String(200), comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )


class EduAttendance(Base):
    """考勤表：学生按课程与日期的考勤状态。"""

    __tablename__ = "edu_attendance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("base_student.id"), nullable=False, comment="学生"
    )
    course_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("edu_course.id"), nullable=False, comment="课程"
    )
    attend_date: Mapped[date] = mapped_column(Date, nullable=False, comment="考勤日期")
    status: Mapped[str] = mapped_column(
        String(16), default="正常", comment="考勤状态：正常/迟到/早退/缺勤/请假"
    )
    remark: Mapped[str | None] = mapped_column(String(200), comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )


# ====================================================================
# 四、校务管理模块（af_）
# ====================================================================


class AfAsset(Base):
    """资产表：学校设备资产台账。"""

    __tablename__ = "af_asset"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="资产编号"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="资产名称")
    category: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="资产分类"
    )
    brand: Mapped[str | None] = mapped_column(String(50), comment="品牌")
    model: Mapped[str | None] = mapped_column(String(50), comment="型号")
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), comment="金额（元）")
    quantity: Mapped[int] = mapped_column(Integer, default=1, comment="数量")
    purchase_date: Mapped[date | None] = mapped_column(Date, comment="购置日期")
    department_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("base_department.id"), comment="所属部门"
    )
    keeper: Mapped[str | None] = mapped_column(String(50), comment="保管人")
    status: Mapped[str] = mapped_column(
        String(16), default="在用", comment="状态：在用/闲置/维修/报废"
    )
    location: Mapped[str | None] = mapped_column(String(100), comment="存放地点")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )


class AfDormRoom(Base):
    """宿舍房间表。"""

    __tablename__ = "af_dorm_room"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    building: Mapped[str] = mapped_column(String(30), nullable=False, comment="宿舍楼")
    room_no: Mapped[str] = mapped_column(String(20), nullable=False, comment="房间号")
    floor: Mapped[int | None] = mapped_column(Integer, comment="楼层")
    capacity: Mapped[int] = mapped_column(Integer, default=6, comment="床位数")
    occupied: Mapped[int] = mapped_column(Integer, default=0, comment="已住人数")
    gender_type: Mapped[str] = mapped_column(
        String(4), default="男", comment="性别类型：男/女"
    )
    remark: Mapped[str | None] = mapped_column(String(200), comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    allocations: Mapped[list["AfDormAllocation"]] = relationship(back_populates="room")


class AfDormAllocation(Base):
    """住宿分配表：学生与宿舍床位的对应关系。"""

    __tablename__ = "af_dorm_allocation"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("base_student.id"), nullable=False, comment="学生"
    )
    room_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("af_dorm_room.id"), nullable=False, comment="宿舍房间"
    )
    bed_no: Mapped[str | None] = mapped_column(String(10), comment="床位号")
    check_in_date: Mapped[date | None] = mapped_column(Date, comment="入住日期")
    status: Mapped[str] = mapped_column(
        String(10), default="在住", comment="状态：在住/已退"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    room: Mapped["AfDormRoom"] = relationship(back_populates="allocations")
