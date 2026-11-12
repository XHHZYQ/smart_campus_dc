"""应用配置模块。

统一管理数据库连接、JWT 参数、跨域白名单等配置项。
配置来源优先级：环境变量 > .env 文件 > 代码内默认值。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置对象。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用基础信息
    APP_NAME: str = "智慧校园数据中心管理软件"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # 数据库
    DATABASE_URL: str = (
        "postgresql+psycopg://smart_campus_dc:smart_campus_dc@localhost:5433/smart_campus_dc_db"
    )

    # 认证
    SECRET_KEY: str = "smart-campus-dc-secret-key-please-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    # 跨域
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        """把逗号分隔的跨域配置解析为列表。"""
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]


settings = Settings()
