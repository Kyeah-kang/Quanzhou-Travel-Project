"""集中管理 FastAPI 应用配置，并从仓库根目录的 .env 读取环境变量。"""

from pathlib import Path

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

    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
