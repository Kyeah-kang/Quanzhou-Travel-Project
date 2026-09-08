"""登录接口的成功、失败和令牌声明测试。"""

from time import time
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def unique_identity() -> tuple[str, str]:
    """生成可重复执行测试所需的唯一用户名和邮箱。"""

    suffix = uuid4().hex[:12]
    return f"login_{suffix}", f"login_{suffix}@example.com"


def remove_user(username: str) -> None:
    """删除测试用户，避免测试数据持续污染开发库。"""

    with SessionLocal() as db:
        db.execute(delete(User).where(User.username == username))
        db.commit()


def create_test_user(username: str, email: str) -> None:
    """通过公开注册接口准备登录测试数据。"""

    response = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": "secret123"},
    )
    assert response.status_code == 201


def test_login_success_returns_minimal_jwt() -> None:
    """正确凭据应返回 bearer token，且 token 只有 sub 和 exp 声明。"""

    username, email = unique_identity()
    try:
        create_test_user(username, email)
        with SessionLocal() as db:
            user_id = db.scalar(select(User.id).where(User.username == username))

        response = client.post(
            "/api/auth/login",
            json={"username": username, "password": "secret123"},
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
        assert claims["sub"] == str(user_id)
        assert claims["exp"] > int(time())
    finally:
        remove_user(username)


def test_wrong_password_and_unknown_user_return_same_401() -> None:
    """错误密码和不存在用户必须返回同一错误，避免用户名枚举。"""

    username, email = unique_identity()
    unknown_username, _ = unique_identity()
    try:
        create_test_user(username, email)
        wrong_password = client.post(
            "/api/auth/login",
            json={"username": username, "password": "wrong123"},
        )
        unknown_user = client.post(
            "/api/auth/login",
            json={"username": unknown_username, "password": "secret123"},
        )

        assert wrong_password.status_code == 401
        assert unknown_user.status_code == 401
        assert wrong_password.json()["detail"] == "用户名或密码错误"
        assert unknown_user.json()["detail"] == wrong_password.json()["detail"]
    finally:
        remove_user(username)


def test_login_missing_field_returns_unprocessable_entity() -> None:
    """缺少登录字段应由 FastAPI 返回 422。"""

    response = client.post("/api/auth/login", json={"username": "missing_password"})

    assert response.status_code == 422
