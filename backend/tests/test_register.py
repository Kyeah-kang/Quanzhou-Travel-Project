"""注册接口的成功、冲突和输入校验测试。"""

from collections.abc import Callable

import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User


def test_register_success_persists_bcrypt_hash(
    client: TestClient,
    user_factory: Callable[..., object],
) -> None:
    """注册成功应返回公开字段，并在数据库保存可验证的 bcrypt 哈希。"""

    user = user_factory(register=False)
    assert hasattr(user, "username")
    assert hasattr(user, "email")
    assert hasattr(user, "password")
    username = user.username
    email = user.email
    password = user.password
    response = client.post(
        "/api/auth/register",
        json={"username": username, "email": email.upper(), "password": password},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == username
    assert body["email"] == email
    assert "hashed_password" not in body
    assert "password" not in body

    with SessionLocal() as db:
        saved_user = db.scalar(select(User).where(User.username == username))
        assert saved_user is not None
        assert saved_user.hashed_password.startswith("$2b$")
        assert bcrypt.checkpw(
            password.encode("utf-8"),
            saved_user.hashed_password.encode("utf-8"),
        )


def test_register_without_email_returns_null_email(
    client: TestClient,
    user_factory: Callable[..., object],
) -> None:
    """email 是可选字段，省略时接口应返回 null。"""

    user = user_factory(register=False, include_email=False)
    assert hasattr(user, "username")
    assert hasattr(user, "password")
    response = client.post(
        "/api/auth/register",
        json={"username": user.username, "password": user.password},
    )

    assert response.status_code == 201
    assert response.json()["email"] is None


def test_duplicate_username_returns_conflict(
    client: TestClient,
    user_factory: Callable[..., object],
) -> None:
    """重复用户名应返回 409，而不是暴露数据库异常。"""

    first_user = user_factory()
    second_user = user_factory(register=False)
    second = client.post(
        "/api/auth/register",
        json={
            "username": first_user.username,
            "email": second_user.email,
            "password": second_user.password,
        },
    )

    assert second.status_code == 409
    assert "用户名" in second.json()["detail"]


def test_duplicate_email_returns_conflict(
    client: TestClient,
    user_factory: Callable[..., object],
) -> None:
    """重复邮箱应返回 409。"""

    first_user = user_factory()
    second_user = user_factory(register=False)
    second = client.post(
        "/api/auth/register",
        json={
            "username": second_user.username,
            "email": first_user.email.upper(),
            "password": second_user.password,
        },
    )

    assert second.status_code == 409
    assert "邮箱" in second.json()["detail"]


def test_invalid_register_payload_returns_unprocessable_entity(client: TestClient) -> None:
    """短密码、非法用户名和坏邮箱都应由 Pydantic 返回 422。"""

    invalid_payloads = (
        {"username": "valid_user", "password": "short"},
        {"username": "bad-user", "password": "secret123"},
        {"username": "valid_user", "email": "not-an-email", "password": "secret123"},
    )

    for payload in invalid_payloads:
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
