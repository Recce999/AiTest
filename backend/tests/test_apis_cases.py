"""接口与用例：CRUD、AI 生成建议、越权校验。"""


def _create_project(client, headers, name="项目"):
    return client.post(
        "/api/projects",
        json={
            "name": name,
            "base_url": "http://127.0.0.1:8000",
            "description": "",
        },
        headers=headers,
    ).json()["data"]


def _create_api(client, headers, project_id, name="健康检查", method="GET", path="/health"):
    return client.post(
        "/api/apis",
        json={
            "project_id": project_id,
            "name": name,
            "method": method,
            "path": path,
            "headers": {},
            "body": {},
            "expected_status": 200,
        },
        headers=headers,
    ).json()["data"]


def _create_case(client, headers, api_id, name="正常用例", enabled=True):
    return client.post(
        "/api/cases",
        json={
            "api_id": api_id,
            "name": name,
            "payload": {},
            "assertions": [{"type": "status_code", "expected": 200}],
            "enabled": enabled,
        },
        headers=headers,
    ).json()["data"]


def test_api_create_list_update_delete(client, project):
    project_data, headers = project

    created = client.post(
        "/api/apis",
        json={
            "project_id": project_data["id"],
            "name": "健康检查",
            "method": "GET",
            "path": "/health",
            "headers": {},
            "body": {},
            "expected_status": 200,
        },
        headers=headers,
    ).json()
    assert created["code"] == 0
    api = created["data"]

    listing = client.get(
        "/api/apis", params={"project_id": project_data["id"]}, headers=headers
    ).json()
    assert [item["id"] for item in listing["data"]] == [api["id"]]

    updated = client.put(
        f"/api/apis/{api['id']}",
        json={
            "project_id": project_data["id"],
            "name": "健康检查（改）",
            "method": "GET",
            "path": "/healthz",
            "headers": {},
            "body": {},
            "expected_status": 200,
        },
        headers=headers,
    ).json()
    assert updated["data"]["path"] == "/healthz"

    assert client.delete(f"/api/apis/{api['id']}", headers=headers).json()["code"] == 0
    assert (
        client.get("/api/apis", params={"project_id": project_data["id"]}, headers=headers)
        .json()["data"]
        == []
    )


def test_case_create_and_list(client, project):
    project_data, headers = project
    api = _create_api(client, headers, project_data["id"])

    case = _create_case(client, headers, api["id"])
    assert case["source"] == "manual"
    assert case["enabled"] is True

    listing = client.get(
        "/api/cases", params={"api_id": api["id"]}, headers=headers
    ).json()
    assert [item["id"] for item in listing["data"]] == [case["id"]]


def test_ai_generate_returns_suggestions_without_saving(client, project):
    project_data, headers = project
    api = _create_api(client, headers, project_data["id"])

    body = client.post(
        "/api/cases/ai-generate", json={"api_id": api["id"], "limit": 3}, headers=headers
    ).json()

    assert body["code"] == 0
    assert len(body["data"]) == 3
    assert all("name" in item and isinstance(item["assertions"], list) for item in body["data"])

    # 只返回建议，不自动入库
    assert (
        client.get("/api/cases", params={"api_id": api["id"]}, headers=headers)
        .json()["data"]
        == []
    )


def test_other_user_cannot_touch_api_or_case(client, make_user):
    _, alice_headers = make_user("alice")
    _, bob_headers = make_user("bob")

    project_id = _create_project(client, alice_headers)["id"]
    api = _create_api(client, alice_headers, project_id)
    _create_case(client, alice_headers, api["id"])

    # 查别人项目的接口列表
    forbidden_list = client.get(
        "/api/apis", params={"project_id": project_id}, headers=bob_headers
    ).json()
    assert forbidden_list["code"] == 403

    # 往别人项目里建接口
    forbidden_create = client.post(
        "/api/apis",
        json={
            "project_id": project_id,
            "name": "偷偷插入",
            "method": "GET",
            "path": "/x",
            "headers": {},
            "body": {},
            "expected_status": 200,
        },
        headers=bob_headers,
    ).json()
    assert forbidden_create["code"] == 403

    # 查别人接口下的用例
    forbidden_cases = client.get(
        "/api/cases", params={"api_id": api["id"]}, headers=bob_headers
    ).json()
    assert forbidden_cases["code"] == 403


def test_update_and_delete_case(client, project):
    project_data, headers = project
    api = _create_api(client, headers, project_data["id"])
    case = _create_case(client, headers, api["id"])

    updated = client.put(
        f"/api/cases/{case['id']}",
        json={
            "api_id": api["id"],
            "name": "改名后的用例",
            "payload": {"q": 1},
            "assertions": [{"type": "max_duration", "expected": 1000}],
            "enabled": False,
        },
        headers=headers,
    ).json()
    assert updated["data"]["name"] == "改名后的用例"
    assert updated["data"]["enabled"] is False

    assert client.delete(f"/api/cases/{case['id']}", headers=headers).json()["code"] == 0
    assert (
        client.get("/api/cases", params={"api_id": api["id"]}, headers=headers)
        .json()["data"]
        == []
    )
