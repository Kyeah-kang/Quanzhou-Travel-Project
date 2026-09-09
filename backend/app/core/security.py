"""提供密码哈希与校验功能。"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


class TokenError(Exception):
    """JWT 校验失败的基础异常。"""


class TokenExpiredError(TokenError):
    """JWT 已超过 exp 指定的有效期。"""


class TokenInvalidError(TokenError):
    """JWT 签名、结构、算法或必要声明不合法。"""


def hash_password(plain: str) -> str:
    """使用 bcrypt 随机加盐生成密码哈希。"""

    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证明文密码是否匹配已保存的 bcrypt 哈希。"""

    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """为用户签发只包含身份和过期时间的 JWT。"""

    expires_at = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(subject), "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """验签并校验 JWT，返回其中的用户 subject。"""

    try:
        # 算法必须由服务端配置决定，不能相信 token header，避免算法混淆攻击。
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError from exc
    except jwt.InvalidTokenError as exc:
        raise TokenInvalidError from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise TokenInvalidError
    return subject
