"""为后端测试提供共享客户端、用户工厂和自动清理。"""

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

TEST_PASSWORD = "secret123"


@dataclass(frozen=True)
class TestUser:
    """测试用户及其登录凭据。"""

    username: str
    email: str
    password: str
    id: int
    token: str

    @property
    def headers(self) -> dict[str, str]:
        """返回可直接用于受保护请求的认证请求头。"""

        return {"Authorization": f"Bearer {self.token}"}


def _unique_identity() -> tuple[str, str]:
    """生成不会与其他测试冲突的用户名和邮箱。"""

    suffix = uuid4().hex[:12]
    username = f"test_{suffix}"
    return username, f"{username}@example.com"


def _delete_users(usernames: Iterable[str]) -> None:
    """按用户名批量清理测试用户。"""

    names = list(usernames)
    if not names:
        return

    with SessionLocal() as db:
        db.execute(delete(User).where(User.username.in_(names)))
        db.commit()


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """创建全测试共享的 TestClient，并管理应用生命周期。"""

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_factory(client: TestClient) -> Iterator[Callable[..., TestUser]]:
    """注册并登录测试用户，测试结束后用 yield teardown 批量清理。"""

    created_usernames: list[str] = []

    def create_user(
        *,
        username: str | None = None,
        email: str | None = None,
        password: str = TEST_PASSWORD,
        register: bool = True,
        include_email: bool = True,
    ) -> TestUser:
        """创建一个测试用户；register=False 只生成待请求的唯一身份。"""

        generated_username, _ = _unique_identity()
        actual_username = username or generated_username
        actual_email = email or f"{actual_username}@example.com"
        created_usernames.append(actual_username)

        if not register:
            return TestUser(
                username=actual_username,
                email=actual_email,
                password=password,
                id=0,
                token="",
            )

        payload: dict[str, str] = {
            "username": actual_username,
            "password": password,
        }
        if include_email:
            payload["email"] = actual_email

        register_response = client.post("/api/auth/register", json=payload)
        assert register_response.status_code == 201
        user_body = register_response.json()

        login_response = client.post(
            "/api/auth/login",
            json={"username": actual_username, "password": password},
        )
        assert login_response.status_code == 200

        return TestUser(
            username=actual_username,
            email=actual_email,
            password=password,
            id=user_body["id"],
            token=login_response.json()["access_token"],
        )

    yield create_user
    _delete_users(created_usernames)
