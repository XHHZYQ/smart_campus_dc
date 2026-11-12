"""数据库连接与会话管理。

使用 SQLAlchemy 2.0 声明式模型，连接 PostgreSQL（psycopg3 驱动）。
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

# 会话工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """所有表模型的基类。"""


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：为每次请求提供独立的数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """根据模型创建所有数据表（已存在的表不会重复创建）。"""
    # 导入模型以完成注册
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
