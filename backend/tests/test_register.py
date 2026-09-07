"""注册接口的成功、冲突和输入校验测试。"""

from uuid import uuid4

import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def unique_identity() -> tuple[str, str]:
    """生成可重复执行测试所需的唯一用户名和邮箱。"""

    suffix = uuid4().hex[:12]
    return f"test_{suffix}", f"test_{suffix}@example.com"


def remove_user(username: str) -> None:
    """删除测试用户，避免测试数据持续污染开发库。"""

    with SessionLocal() as db:
        db.execute(delete(User).where(User.username == username))
        db.commit()


def test_register_success_persists_bcrypt_hash() -> None:
    """注册成功应返回公开字段，并在数据库保存可验证的 bcrypt 哈希。"""

    username, email = unique_identity()
    try:
        response = client.post(
            "/api/auth/register",
            json={"username": username, "email": email.upper(), "password": "secret123"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["username"] == username
        assert body["email"] == email
        assert "hashed_password" not in body
        assert "password" not in body

        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.username == username))
            assert user is not None
            assert user.hashed_password.startswith("$2b$")
            assert bcrypt.checkpw(b"secret123", user.hashed_password.encode("utf-8"))
    finally:
        remove_user(username)


def test_duplicate_username_returns_conflict() -> None:
    """重复用户名应返回 409，而不是暴露数据库异常。"""

    username, email = unique_identity()
    _, other_email = unique_identity()
    try:
        first = client.post(
            "/api/auth/register",
            json={"username": username, "email": email, "password": "secret123"},
        )
        second = client.post(
            "/api/auth/register",
            json={"username": username, "email": other_email, "password": "secret123"},
        )

        assert first.status_code == 201
        assert second.status_code == 409
        assert "用户名" in second.json()["detail"]
    finally:
        remove_user(username)


def test_duplicate_email_returns_conflict() -> None:
    """重复邮箱应返回 409。"""

    username, email = unique_identity()
    other_username, _ = unique_identity()
    try:
        first = client.post(
            "/api/auth/register",
            json={"username": username, "email": email, "password": "secret123"},
        )
        second = client.post(
            "/api/auth/register",
            json={"username": other_username, "email": email.upper(), "password": "secret123"},
        )

        assert first.status_code == 201
        assert second.status_code == 409
        assert "邮箱" in second.json()["detail"]
    finally:
        remove_user(username)


def test_invalid_register_payload_returns_unprocessable_entity() -> None:
    """短密码、非法用户名和坏邮箱都应由 Pydantic 返回 422。"""

    invalid_payloads = (
        {"username": "valid_user", "password": "short"},
        {"username": "bad-user", "password": "secret123"},
        {"username": "valid_user", "email": "not-an-email", "password": "secret123"},
    )

    for payload in invalid_payloads:
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
