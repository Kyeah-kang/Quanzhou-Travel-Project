"""健康检查接口冒烟测试。"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    """健康检查应返回 200 和 ok 状态。"""

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
