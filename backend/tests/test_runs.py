"""执行引擎与报告：用假响应替代真实 HTTP，覆盖通过、失败、异常与 SSRF。"""
import json

from app.core.config import settings


class FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body
        self.text = json.dumps(body, ensure_ascii=False) if body is not None else ""

    def json(self):
        if self._body is None:
            raise json.JSONDecodeError("Expecting value", "", 0)
        return self._body


def _setup(
    client,
    headers,
    *,
    assertions=None,
    expected_status=200,
    enabled=True,
    base_url="http://127.0.0.1:8000",
):
    project_id = client.post(
        "/api/projects",
        json={"name": "执行项目", "base_url": base_url, "description": ""},
        headers=headers,
    ).json()["data"]["id"]

    api_id = client.post(
        "/api/apis",
        json={
            "project_id": project_id,
            "name": "健康检查",
            "method": "GET",
            "path": "/health",
            "headers": {},
            "body": {},
            "expected_status": expected_status,
        },
        headers=headers,
    ).json()["data"]["id"]

    case = client.post(
        "/api/cases",
        json={
            "api_id": api_id,
            "name": "用例",
            "payload": {},
            "assertions": assertions or [{"type": "status_code", "expected": expected_status}],
            "enabled": enabled,
        },
        headers=headers,
    ).json()["data"]

    return project_id, api_id, case


def _fake_request(status_code=200, body=None):
    def _request(*args, **kwargs):
        return FakeResponse(status_code, body)

    return _request


def test_run_passed(client, make_user, monkeypatch):
    _, headers = make_user()
    project_id, _, _ = _setup(
        client,
        headers,
        assertions=[
            {"type": "status_code", "expected": 200},
            {"type": "json_field", "path": "data.status", "expected": "up"},
            {"type": "max_duration", "expected": 5000},
        ],
    )
    monkeypatch.setattr(
        "app.services.executor.requests.request", _fake_request(200, {"data": {"status": "up"}})
    )

    body = client.post("/api/runs", json={"project_id": project_id}, headers=headers).json()
    assert body["code"] == 0

    run = body["data"]
    assert (run["total"], run["passed"], run["failed"]) == (1, 1, 0)
    assert run["results"][0]["status"] == "passed"
    assert run["results"][0]["status_code"] == 200


def test_run_failed_on_status_code(client, make_user, monkeypatch):
    _, headers = make_user()
    project_id, _, _ = _setup(client, headers)
    monkeypatch.setattr("app.services.executor.requests.request", _fake_request(500, {"msg": "boom"}))

    run = client.post("/api/runs", json={"project_id": project_id}, headers=headers).json()["data"]

    assert (run["total"], run["passed"], run["failed"]) == (1, 0, 1)
    assert run["results"][0]["status"] == "failed"
    assert "状态码期望 200" in run["results"][0]["error_msg"]


def test_run_failed_on_missing_json_field(client, make_user, monkeypatch):
    _, headers = make_user()
    project_id, _, _ = _setup(
        client,
        headers,
        assertions=[{"type": "json_field", "path": "data.nope", "expected": 1}],
    )
    monkeypatch.setattr(
        "app.services.executor.requests.request", _fake_request(200, {"data": {"status": "up"}})
    )

    run = client.post("/api/runs", json={"project_id": project_id}, headers=headers).json()["data"]

    assert run["failed"] == 1
    assert "字段 data.nope 不存在" in run["results"][0]["error_msg"]


def test_run_without_cases_is_rejected(client, make_user):
    _, headers = make_user()
    project_id = client.post(
        "/api/projects",
        json={"name": "空项目", "base_url": "http://127.0.0.1:8000", "description": ""},
        headers=headers,
    ).json()["data"]["id"]

    body = client.post("/api/runs", json={"project_id": project_id}, headers=headers).json()
    assert body["code"] == 1
    assert body["msg"] == "没有可执行的用例"


def test_internal_target_blocked_when_guard_enabled(client, make_user, monkeypatch):
    _, headers = make_user()
    project_id, _, _ = _setup(client, headers)
    monkeypatch.setattr(settings, "allow_private_target", False)

    run = client.post("/api/runs", json={"project_id": project_id}, headers=headers).json()["data"]
    result = run["results"][0]

    assert result["status"] == "error"
    assert "内网" in result["error_msg"]


def test_run_history_and_detail(client, make_user, monkeypatch):
    _, headers = make_user()
    project_id, _, _ = _setup(client, headers)
    monkeypatch.setattr(
        "app.services.executor.requests.request", _fake_request(200, {"data": {"status": "up"}})
    )

    created = client.post(
        "/api/runs", json={"project_id": project_id}, headers=headers
    ).json()["data"]

    history = client.get(
        "/api/runs", params={"project_id": project_id}, headers=headers
    ).json()["data"]
    assert len(history) == 1
    assert history[0]["id"] == created["id"]
    assert history[0]["created_at"]

    detail = client.get(f"/api/runs/{created['id']}", headers=headers).json()["data"]
    assert detail["total"] == 1
    assert len(detail["results"]) == 1


def test_other_user_cannot_read_run(client, make_user, monkeypatch):
    _, alice_headers = make_user("alice")
    project_id, _, _ = _setup(client, alice_headers)
    monkeypatch.setattr(
        "app.services.executor.requests.request", _fake_request(200, {"data": {"status": "up"}})
    )
    run_id = client.post(
        "/api/runs", json={"project_id": project_id}, headers=alice_headers
    ).json()["data"]["id"]

    _, bob_headers = make_user("bob")
    assert client.get(f"/api/runs/{run_id}", headers=bob_headers).json()["code"] == 403
    assert (
        client.get("/api/runs", params={"project_id": project_id}, headers=bob_headers).json()["code"]
        == 403
    )


def test_disabled_case_is_skipped(client, make_user, monkeypatch):
    _, headers = make_user()
    project_id, api_id, enabled_case = _setup(client, headers)

    client.post(
        "/api/cases",
        json={
            "api_id": api_id,
            "name": "已禁用的用例",
            "payload": {},
            "assertions": [{"type": "status_code", "expected": 200}],
            "enabled": False,
        },
        headers=headers,
    )
    monkeypatch.setattr(
        "app.services.executor.requests.request", _fake_request(200, {"data": {"status": "up"}})
    )

    run = client.post("/api/runs", json={"project_id": project_id}, headers=headers).json()["data"]

    assert run["total"] == 1
    assert run["results"][0]["case_id"] == enabled_case["id"]
