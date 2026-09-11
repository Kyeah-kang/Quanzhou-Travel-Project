"""受保护的当前用户接口测试。"""

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User


def test_me_without_token_returns_401(client: TestClient) -> None:
    """缺少 Authorization 头时，OAuth2 依赖应直接返回 401。"""

    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_with_invalid_token_returns_401(client: TestClient) -> None:
    """结构或签名错误的 token 应返回无效令牌提示。"""

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "无效的访问令牌"


def test_me_with_expired_token_returns_401(client: TestClient) -> None:
    """过期 token 应返回重新登录提示。"""

    token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["detail"] == "登录已过期，请重新登录"


def test_me_with_non_numeric_subject_returns_401(client: TestClient) -> None:
    """token subject 不是用户 id 时应返回无效令牌提示。"""

    token = jwt.encode(
        {
            "sub": "abc",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["detail"] == "无效的访问令牌"


def test_me_with_wrong_authorization_scheme_returns_401(client: TestClient) -> None:
    """非 Bearer 认证头应由 OAuth2PasswordBearer 短路返回 401。"""

    response = client.get("/api/auth/me", headers={"Authorization": "Basic xxx"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_with_valid_token_returns_public_user(
    client: TestClient,
    user_factory: Callable[..., object],
) -> None:
    """合法 token 应返回用户资料且不泄露密码哈希。"""

    user = user_factory()
    response = client.get("/api/auth/me", headers=user.headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user.id
    assert body["username"] == user.username
    assert body["email"] == user.email
    assert "hashed_password" not in body


def test_me_for_deleted_user_returns_401(
    client: TestClient,
    user_factory: Callable[..., object],
) -> None:
    """用户删除后，原 token 不能继续物化出用户主体。"""

    user = user_factory()
    with SessionLocal() as db:
        deleted_user = db.get(User, user.id)
        assert deleted_user is not None
        db.delete(deleted_user)
        db.commit()

    response = client.get("/api/auth/me", headers=user.headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "用户不存在或已被删除"
