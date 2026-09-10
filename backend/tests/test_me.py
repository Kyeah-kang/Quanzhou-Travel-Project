"""受保护的当前用户接口测试。"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def unique_identity() -> tuple[str, str]:
    """生成可重复执行测试所需的唯一用户名和邮箱。"""

    suffix = uuid4().hex[:12]
    return f"me_{suffix}", f"me_{suffix}@example.com"


def remove_user(username: str) -> None:
    """删除测试用户，避免测试数据持续污染开发库。"""

    with SessionLocal() as db:
        db.execute(delete(User).where(User.username == username))
        db.commit()


def create_and_login() -> tuple[str, str, dict[str, object]]:
    """通过注册和登录接口准备当前用户测试数据。"""

    username, email = unique_identity()
    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": "secret123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "secret123"},
    )
    assert login_response.status_code == 200
    return username, email, login_response.json()


def test_me_without_token_returns_401() -> None:
    """缺少 Authorization 头时，OAuth2 依赖应直接返回 401。"""

    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_with_invalid_token_returns_401() -> None:
    """结构或签名错误的 token 应返回无效令牌提示。"""

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "无效的访问令牌"


def test_me_with_expired_token_returns_401() -> None:
    """过期 token 应返回重新登录提示。"""

    token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "登录已过期，请重新登录"


def test_me_with_valid_token_returns_public_user() -> None:
    """合法 token 应返回用户资料且不泄露密码哈希。"""

    username, email, login_body = create_and_login()
    try:
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {login_body['access_token']}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["username"] == username
        assert body["email"] == email
        assert "hashed_password" not in body
    finally:
        remove_user(username)


def test_me_for_deleted_user_returns_401() -> None:
    """用户删除后，原 token 不能继续物化出用户主体。"""

    username, _, login_body = create_and_login()
    remove_user(username)

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login_body['access_token']}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "用户不存在或已被删除"
