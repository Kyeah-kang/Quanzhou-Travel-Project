"""承载登录业务和统一的凭据失败处理。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginIn


class InvalidCredentialsError(Exception):
    """表示登录凭据无效。"""


def login(db: Session, data: LoginIn) -> str:
    """验证用户名密码并返回访问令牌。"""

    user = db.scalar(select(User).where(User.username == data.username))
    if user is None or not verify_password(data.password, user.hashed_password):
        # 用户不存在和密码错误共用异常，避免通过响应枚举有效用户名。
        raise InvalidCredentialsError

    return create_access_token(user.id)
