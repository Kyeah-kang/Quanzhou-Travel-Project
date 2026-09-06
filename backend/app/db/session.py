"""提供 SQLAlchemy 会话工厂和 FastAPI 可复用的数据库依赖。"""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.db.engine import engine

SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """生成一个工作单元会话，并确保请求结束后释放连接。"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
