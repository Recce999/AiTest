"""项目 CRUD 与越权校验。"""


def _payload(name="新项目"):
    return {
        "name": name,
        "base_url": "http://127.0.0.1:8000",
        "description": "描述",
    }


def test_create_and_list(client, make_user):
    _, headers = make_user()

    created = client.post("/api/projects", json=_payload(), headers=headers).json()
    assert created["code"] == 0
    assert created["data"]["name"] == "新项目"

    listing = client.get("/api/projects", headers=headers).json()
    assert listing["code"] == 0
    assert [item["id"] for item in listing["data"]] == [created["data"]["id"]]


def test_update_and_delete(client, make_user):
    _, headers = make_user()
    pid = client.post("/api/projects", json=_payload(), headers=headers).json()["data"]["id"]

    updated = client.put(
        f"/api/projects/{pid}", json=_payload("改名后"), headers=headers
    ).json()
    assert updated["code"] == 0
    assert updated["data"]["name"] == "改名后"

    deleted = client.delete(f"/api/projects/{pid}", headers=headers).json()
    assert deleted["code"] == 0
    assert client.get("/api/projects", headers=headers).json()["data"] == []


def test_delete_project_purges_run_history(client, make_user, monkeypatch):
    """删项目时要连执行记录和执行结果一起清掉，不能留下孤儿数据。"""
    _, headers = make_user()
    pid = client.post("/api/projects", json=_payload(), headers=headers).json()["data"]["id"]
    api_id = (
        client.post(
            "/api/apis",
            json={"project_id": pid, "name": "健康检查", "method": "GET", "path": "/health"},
            headers=headers,
        )
        .json()["data"]["id"]
    )
    client.post(
        "/api/cases",
        json={"api_id": api_id, "name": "正常返回", "assertions": [{"type": "status_code", "expected": 200}]},
        headers=headers,
    )

    def fake_request(*args, **kwargs):
        class Resp:
            status_code = 200

            def json(self):
                return {"status": "up"}

        return Resp()

    monkeypatch.setattr("app.services.executor.requests.request", fake_request)
    run_id = client.post("/api/runs", json={"project_id": pid}, headers=headers).json()["data"]["id"]

    assert client.delete(f"/api/projects/{pid}", headers=headers).json()["code"] == 0

    from app.core.db import SessionLocal
    from app.models.models import Run, RunResult

    db = SessionLocal()
    try:
        assert db.get(Run, run_id) is None
        assert db.query(RunResult).filter(RunResult.run_id == run_id).count() == 0
    finally:
        db.close()


def test_other_users_project_is_forbidden(client, make_user):
    _, alice_headers = make_user("alice")
    _, bob_headers = make_user("bob")

    pid = (
        client.post("/api/projects", json=_payload(), headers=alice_headers)
        .json()["data"]["id"]
    )

    assert (
        client.put(
            f"/api/projects/{pid}", json=_payload("bob 想改名"), headers=bob_headers
        ).json()["code"]
        == 403
    )
    assert client.delete(f"/api/projects/{pid}", headers=bob_headers).json()["code"] == 403
    assert client.get("/api/projects", headers=bob_headers).json()["data"] == []


def test_empty_name_rejected(client, make_user):
    _, headers = make_user()
    response = client.post(
        "/api/projects",
        json={"name": "", "base_url": "http://127.0.0.1:8000", "description": ""},
        headers=headers,
    )
    assert response.status_code == 422
