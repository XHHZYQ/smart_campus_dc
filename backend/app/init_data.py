"""初始化数据脚本。

用途：
1. 创建角色（五种角色）
2. 创建演示账号（每种角色一个，密码统一为 admin123）
3. 创建基础参考数据（部门、年级、班级、学期）

执行方式（在 backend 目录下）：
    python -m app.init_data

脚本可重复执行：已存在的数据会跳过，不会重复插入。
完整的演示业务数据（学生、教职工、课程、成绩、考勤、资产、宿舍）在后续阶段补充。
"""

from app.database import SessionLocal, init_db
from app.models import (
    BaseClass,
    BaseDepartment,
    BaseGrade,
    BaseSemester,
    SysRole,
    SysUser,
)
from app.security import hash_password

# 统一演示密码
DEMO_PASSWORD = "admin123"

# 五种角色
ROLES = [
    {"name": "系统管理员", "code": "admin", "description": "拥有系统全部功能权限", "sort_order": 1},
    {"name": "教务管理员", "code": "academic", "description": "负责基础数据与教学管理", "sort_order": 2},
    {"name": "班主任", "code": "head_teacher", "description": "管理所带班级的学生、成绩与考勤", "sort_order": 3},
    {"name": "任课教师", "code": "subject_teacher", "description": "录入所任课程的成绩与考勤", "sort_order": 4},
    {"name": "总务管理员", "code": "general_affairs", "description": "负责资产台账与宿舍管理", "sort_order": 5},
]

# 演示账号（每个角色一个）
USERS = [
    {"username": "admin", "real_name": "张建国", "role_code": "admin", "phone": "13800000001", "email": "admin@school.edu.cn"},
    {"username": "jiaowu", "real_name": "李文娟", "role_code": "academic", "phone": "13800000002", "email": "jiaowu@school.edu.cn"},
    {"username": "banzhuren", "real_name": "王海燕", "role_code": "head_teacher", "phone": "13800000003", "email": "banzhuren@school.edu.cn"},
    {"username": "laoshi", "real_name": "陈志强", "role_code": "subject_teacher", "phone": "13800000004", "email": "laoshi@school.edu.cn"},
    {"username": "zongwu", "real_name": "刘明辉", "role_code": "general_affairs", "phone": "13800000005", "email": "zongwu@school.edu.cn"},
]

# 部门与教研组
DEPARTMENTS = [
    {"name": "教务处", "code": "D001", "dept_type": "行政科室", "leader": "李文娟", "phone": "010-88880001", "sort_order": 1},
    {"name": "德育处", "code": "D002", "dept_type": "行政科室", "leader": "赵德明", "phone": "010-88880002", "sort_order": 2},
    {"name": "总务处", "code": "D003", "dept_type": "行政科室", "leader": "刘明辉", "phone": "010-88880003", "sort_order": 3},
    {"name": "校长办公室", "code": "D004", "dept_type": "行政科室", "leader": "孙国华", "phone": "010-88880004", "sort_order": 4},
    {"name": "语文教研组", "code": "D101", "dept_type": "教研组", "leader": "周雅琴", "phone": "010-88880101", "sort_order": 11},
    {"name": "数学教研组", "code": "D102", "dept_type": "教研组", "leader": "吴建华", "phone": "010-88880102", "sort_order": 12},
    {"name": "英语教研组", "code": "D103", "dept_type": "教研组", "leader": "郑晓梅", "phone": "010-88880103", "sort_order": 13},
    {"name": "物理教研组", "code": "D104", "dept_type": "教研组", "leader": "冯立军", "phone": "010-88880104", "sort_order": 14},
    {"name": "化学教研组", "code": "D105", "dept_type": "教研组", "leader": "许文斌", "phone": "010-88880105", "sort_order": 15},
    {"name": "生物教研组", "code": "D106", "dept_type": "教研组", "leader": "何丽丽", "phone": "010-88880106", "sort_order": 16},
    {"name": "政治教研组", "code": "D107", "dept_type": "教研组", "leader": "杨志刚", "phone": "010-88880107", "sort_order": 17},
    {"name": "历史教研组", "code": "D108", "dept_type": "教研组", "leader": "罗建平", "phone": "010-88880108", "sort_order": 18},
    {"name": "地理教研组", "code": "D109", "dept_type": "教研组", "leader": "唐国栋", "phone": "010-88880109", "sort_order": 19},
    {"name": "体育教研组", "code": "D110", "dept_type": "教研组", "leader": "马晓东", "phone": "010-88880110", "sort_order": 20},
]

# 十二个年级：小学 6 个、初中 3 个、高中 3 个
GRADE_DEFS = [
    ("一年级", "小学", 1), ("二年级", "小学", 2), ("三年级", "小学", 3),
    ("四年级", "小学", 4), ("五年级", "小学", 5), ("六年级", "小学", 6),
    ("七年级", "初中", 7), ("八年级", "初中", 8), ("九年级", "初中", 9),
    ("高一", "高中", 10), ("高二", "高中", 11), ("高三", "高中", 12),
]

# 六个学期
SEMESTERS = [
    {"name": "2023-2024学年第一学期", "academic_year": "2023-2024", "term": 1, "start_date": "2023-09-01", "end_date": "2024-01-20", "is_current": False},
    {"name": "2023-2024学年第二学期", "academic_year": "2023-2024", "term": 2, "start_date": "2024-02-26", "end_date": "2024-07-05", "is_current": False},
    {"name": "2024-2025学年第一学期", "academic_year": "2024-2025", "term": 1, "start_date": "2024-09-02", "end_date": "2025-01-17", "is_current": False},
    {"name": "2024-2025学年第二学期", "academic_year": "2024-2025", "term": 2, "start_date": "2025-02-24", "end_date": "2025-07-04", "is_current": False},
    {"name": "2025-2026学年第一学期", "academic_year": "2025-2026", "term": 1, "start_date": "2025-09-01", "end_date": "2026-01-16", "is_current": True},
    {"name": "2025-2026学年第二学期", "academic_year": "2025-2026", "term": 2, "start_date": "2026-02-23", "end_date": "2026-07-03", "is_current": False},
]


def init_roles(db) -> dict[str, SysRole]:
    """初始化角色，返回 角色编码 → 角色对象 的映射。"""
    mapping: dict[str, SysRole] = {}
    for item in ROLES:
        role = db.query(SysRole).filter(SysRole.code == item["code"]).first()
        if role is None:
            role = SysRole(**item)
            db.add(role)
            db.flush()
            print(f"  新增角色：{item['name']}")
        mapping[item["code"]] = role
    db.commit()
    return mapping


def init_users(db, role_map: dict[str, SysRole]) -> None:
    """初始化演示账号。"""
    password_hash = hash_password(DEMO_PASSWORD)
    for item in USERS:
        exists = db.query(SysUser).filter(SysUser.username == item["username"]).first()
        if exists:
            continue
        role = role_map[item["role_code"]]
        db.add(
            SysUser(
                username=item["username"],
                password_hash=password_hash,
                real_name=item["real_name"],
                role_id=role.id,
                phone=item["phone"],
                email=item["email"],
                status="启用",
            )
        )
        print(f"  新增账号：{item['username']}（{item['real_name']}）")
    db.commit()


def init_departments(db) -> None:
    """初始化部门与教研组。"""
    for item in DEPARTMENTS:
        exists = (
            db.query(BaseDepartment).filter(BaseDepartment.code == item["code"]).first()
        )
        if exists:
            continue
        db.add(BaseDepartment(**item))
    db.commit()


def init_grades(db) -> None:
    """初始化十二个年级。"""
    for name, stage, level in GRADE_DEFS:
        code = f"G{level:02d}"
        exists = db.query(BaseGrade).filter(BaseGrade.code == code).first()
        if exists:
            continue
        db.add(BaseGrade(name=name, code=code, stage=stage, grade_level=level))
    db.commit()


def init_semesters(db) -> None:
    """初始化学期。"""
    from datetime import date

    for item in SEMESTERS:
        exists = (
            db.query(BaseSemester).filter(BaseSemester.name == item["name"]).first()
        )
        if exists:
            continue
        data = dict(item)
        data["start_date"] = date.fromisoformat(data["start_date"])
        data["end_date"] = date.fromisoformat(data["end_date"])
        db.add(BaseSemester(**data))
    db.commit()


def init_classes(db) -> None:
    """初始化班级：每个年级 4 个班。"""
    grades = db.query(BaseGrade).order_by(BaseGrade.grade_level).all()
    for grade in grades:
        for index in range(1, 5):
            class_code = f"{grade.code}-{index:02d}"
            exists = (
                db.query(BaseClass).filter(BaseClass.code == class_code).first()
            )
            if exists:
                continue
            db.add(
                BaseClass(
                    name=f"{grade.name}({index})班",
                    code=class_code,
                    grade_id=grade.id,
                    room=f"{grade.name}教学楼{index}02",
                    enroll_year=2026 - grade.grade_level,
                )
            )
    db.commit()


def main() -> None:
    """执行初始化。"""
    print("=" * 56)
    print("智慧校园数据中心管理软件 —— 初始化基础数据")
    print("=" * 56)

    print("[1/2] 创建数据表 ...")
    init_db()

    db = SessionLocal()
    try:
        print("[2/2] 写入初始数据 ...")
        role_map = init_roles(db)
        init_users(db, role_map)
        init_departments(db)
        init_grades(db)
        init_semesters(db)
        init_classes(db)
        print("-" * 56)
        print("初始化完成！演示账号（密码统一为 {}）：".format(DEMO_PASSWORD))
        for item in USERS:
            print(f"  {item['username']:<12} {item['real_name']}  ({item['role_code']})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
