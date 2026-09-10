"""定义认证相关的 FastAPI 依赖。"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import TokenExpiredError, TokenInvalidError, decode_access_token
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def authentication_error(detail: str) -> HTTPException:
    """构造统一的 Bearer 认证失败响应。"""

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """验 token、查询用户并返回当前主体；所有认证失败都返回 401。"""

    try:
        subject = decode_access_token(token)
    except TokenExpiredError as exc:
        raise authentication_error("登录已过期，请重新登录") from exc
    except TokenInvalidError as exc:
        raise authentication_error("无效的访问令牌") from exc

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise authentication_error("无效的访问令牌") from exc

    # 验签本身不查库，保持 JWT 的无状态特性；/me 查库是为了物化用户资料并拦截已删除用户。
    user = db.get(User, user_id)
    if user is None:
        raise authentication_error("用户不存在或已被删除")
    return user
