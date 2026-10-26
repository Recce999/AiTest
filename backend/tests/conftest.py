"""测试夹具：临时 SQLite 数据库 + 注册登录辅助函数。

必须在导入 app 之前设置 DATABASE_URL，因为 app/core/db.py 在导入时就创建 engine。
"""
import os
import tempfile

_tmp_dir = tempfile.mkdtemp(prefix="aitest-tests-")
_db_path = os.path.join(_tmp_dir, "test.db").replace("\\", "/")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["JWT_SECRET"] = "pytest-only-secret-key-at-least-32-bytes"
os.environ["ALLOW_PRIVATE_TARGET"] = "True"
os.environ["LLM_API_KEY"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    """每个用例都从干净的表结构开始，避免用例之间互相污染。"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def make_user(client):
    """注册并登录一个用户，返回 (user, 带 token 的请求头)。"""

    def _make(username: str = "alice", password: str = "secret123"):
        registered = client.post(
            "/api/auth/register", json={"username": username, "password": password}
        )
        assert registered.json()["code"] == 0, registered.text

        logged_in = client.post(
            "/api/auth/login", json={"username": username, "password": password}
        )
        body = logged_in.json()
        assert body["code"] == 0, body
        data = body["data"]
        return data["user"], {"Authorization": f"Bearer {data['token']}"}

    return _make


@pytest.fixture()
def project(client, make_user):
    """创建一个属于 alice 的项目，返回 (项目数据, 请求头)。"""
    _, headers = make_user()
    created = client.post(
        "/api/projects",
        json={
            "name": "示例项目",
            "base_url": "http://127.0.0.1:8000",
            "description": "用于测试的项目",
        },
        headers=headers,
    )
    body = created.json()
    assert body["code"] == 0, body
    return body["data"], headers
