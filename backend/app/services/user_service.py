"""承载用户注册业务和唯一性冲突处理。"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import RegisterIn


class UserAlreadyExistsError(Exception):
    """表示用户名或邮箱已被注册。"""


def register(db: Session, data: RegisterIn) -> User:
    """校验唯一性并创建用户，返回已持久化的用户对象。"""

    email = str(data.email).lower() if data.email is not None else None

    if db.scalar(select(User.id).where(User.username == data.username)) is not None:
        raise UserAlreadyExistsError("用户名已存在")
    if email is not None and db.scalar(select(User.id).where(User.email == email)) is not None:
        raise UserAlreadyExistsError("邮箱已存在")

    user = User(
        username=data.username,
        email=email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        # 前置查询与提交不是原子操作，并发注册仍需依赖数据库唯一约束兜底。
        db.rollback()
        raise UserAlreadyExistsError("用户名或邮箱已存在") from None

    return user
