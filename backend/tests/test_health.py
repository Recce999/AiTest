"""健康检查：部署后的第一条验证。"""


def test_health(client):
    body = client.get("/health").json()

    assert body["code"] == 0
    assert body["data"]["status"] == "up"
    assert body["data"]["app"] == "AITest"
