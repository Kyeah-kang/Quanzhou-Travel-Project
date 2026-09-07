"""创建全局 SQLAlchemy 同步 engine。"""

from sqlalchemy import create_engine

from app.core.config import settings

engine = create_engine(
    settings.mysql_dsn,
    pool_pre_ping=True,
    echo=settings.debug,
    hide_parameters=True,
)
