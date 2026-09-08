"""集中管理 FastAPI 应用配置，并从仓库根目录的 .env 读取环境变量。"""

from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """应用运行配置。"""

    project_name: str = "刺桐智游"
    version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3307
    mysql_user: str = "citong"
    mysql_password: str = ""
    mysql_database: str = "citong"
    jwt_secret: str = Field(min_length=32, validation_alias="SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)

    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def mysql_dsn(self) -> str:
        """根据分散的 MySQL 配置生成 SQLAlchemy 连接地址。"""

        username = quote_plus(self.mysql_user)
        password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{username}:{password}@"
            f"{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )


settings = Settings()
