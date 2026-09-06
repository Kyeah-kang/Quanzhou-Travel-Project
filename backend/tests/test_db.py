"""SQLAlchemy 数据层的配置、连通性和模型注册测试。"""

from sqlalchemy import text

import app.models  # noqa: F401
from app.core.config import settings
from app.db.base import Base
from app.db.engine import engine


def test_mysql_dsn_uses_pymysql() -> None:
    """DSN 使用同步 PyMySQL 方言，且不在断言输出中暴露完整连接信息。"""

    assert settings.mysql_dsn.startswith("mysql+pymysql://")


def test_mysql_connection() -> None:
    """数据层应能通过容器中的 MySQL 执行最小查询。"""

    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1


def test_user_model_is_registered() -> None:
    """导入模型汇总包后，users 应出现在共享元数据中。"""

    assert "users" in Base.metadata.tables
