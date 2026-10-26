"""认证：注册、登录、当前用户，以及安全相关的边界行为。"""


def test_register_and_me(client, make_user):
    user, headers = make_user("alice", "secret123")

    assert user["username"] == "alice"
    assert "password" not in user
    assert "password_hash" not in user

    me = client.get("/api/auth/me", headers=headers).json()
    assert me["code"] == 0
    assert me["data"]["username"] == "alice"


def test_duplicate_username_rejected(client):
    payload = {"username": "bob", "password": "secret123"}
    assert client.post("/api/auth/register", json=payload).json()["code"] == 0

    body = client.post("/api/auth/register", json=payload).json()
    assert body["code"] == 1
    assert body["msg"] == "用户名已存在"


def test_short_password_rejected_by_schema(client):
    response = client.post(
        "/api/auth/register", json={"username": "carl", "password": "123"}
    )
    assert response.status_code == 422


def test_wrong_password_and_missing_user_share_message(client, make_user):
    make_user("dave", "secret123")

    wrong = client.post(
        "/api/auth/login", json={"username": "dave", "password": "wrong-pass"}
    ).json()
    missing = client.post(
        "/api/auth/login", json={"username": "nobody", "password": "secret123"}
    ).json()

    # 统一提示，避免被用来枚举用户名
    assert wrong["code"] == 1
    assert wrong["msg"] == "用户名或密码错误"
    assert missing["msg"] == wrong["msg"]


def test_me_requires_valid_token(client):
    assert client.get("/api/auth/me").json()["code"] == 401

    invalid = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-token"}
    ).json()
    assert invalid["code"] == 401
