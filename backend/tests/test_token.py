"""JWT 解码校验工具的安全边界测试。"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    TokenExpiredError,
    TokenInvalidError,
    create_access_token,
    decode_access_token,
)


def encode_payload(payload: dict[str, object], secret: str = settings.jwt_secret) -> str:
    """用当前配置算法构造测试 token，不经过生产签发函数。"""

    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def test_decode_valid_access_token_returns_subject() -> None:
    """D07 签发的合法 token 应返回字符串 subject。"""

    token = create_access_token(42)

    assert decode_access_token(token) == "42"


def test_decode_expired_token_raises_expired_error() -> None:
    """签名正确但已过期的 token 应单独归类。"""

    token = encode_payload(
        {
            "sub": "42",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        }
    )

    with pytest.raises(TokenExpiredError):
        decode_access_token(token)


def test_decode_tampered_token_raises_invalid_error() -> None:
    """修改签名后，验签必须失败。"""

    token = create_access_token(42)
    header, payload, signature = token.split(".")
    tampered_signature = f"{signature[:-1]}{'A' if signature[-1] != 'A' else 'B'}"

    with pytest.raises(TokenInvalidError):
        decode_access_token(f"{header}.{payload}.{tampered_signature}")


def test_decode_wrong_secret_token_raises_invalid_error() -> None:
    """使用其他密钥签发的 token 不应被当前服务接受。"""

    token = encode_payload(
        {"sub": "42", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "x" * 32,
    )

    with pytest.raises(TokenInvalidError):
        decode_access_token(token)


def test_decode_token_without_subject_raises_invalid_error() -> None:
    """缺少 sub 的 token 即使签名正确也不能作为身份凭据。"""

    token = encode_payload(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
    )

    with pytest.raises(TokenInvalidError):
        decode_access_token(token)
