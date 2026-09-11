"""登录接口的成功、失败和令牌声明测试。"""

from collections.abc import Callable
from time import time

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings


def test_login_success_returns_minimal_jwt(
    client: TestClient,
    user_factory: Callable[..., object],
) -> None:
    """正确凭据应返回 bearer token，且 token 只有 sub 和 exp 声明。"""

    user = user_factory()
    response = client.post(
        "/api/auth/login",
        json={"username": user.username, "password": user.password},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == settings.access_token_expire_minutes * 60
    assert len(body["access_token"].split(".")) == 3

    claims = jwt.decode(
        body["access_token"],
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    assert set(claims) == {"sub", "exp"}
    assert claims["sub"] == str(user.id)
    assert claims["exp"] > int(time())


def test_wrong_password_and_unknown_user_return_same_401(
    client: TestClient,
    user_factory: Callable[..., object],
) -> None:
    """错误密码和不存在用户必须返回同一错误，避免用户名枚举。"""

    user = user_factory()
    unknown_user = user_factory(register=False)
    wrong_password = client.post(
        "/api/auth/login",
        json={"username": user.username, "password": "wrong123"},
    )
    unknown = client.post(
        "/api/auth/login",
        json={"username": unknown_user.username, "password": user.password},
    )

    assert wrong_password.status_code == 401
    assert unknown.status_code == 401
    assert wrong_password.json()["detail"] == "用户名或密码错误"
    assert unknown.json()["detail"] == wrong_password.json()["detail"]


def test_login_missing_field_returns_unprocessable_entity(client: TestClient) -> None:
    """缺少登录字段应由 FastAPI 返回 422。"""

    response = client.post("/api/auth/login", json={"username": "missing_password"})

    assert response.status_code == 422
