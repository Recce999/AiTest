"""新增用例：未知接口路径必须返回 404，前端路由仍然回退到页面。"""
import pytest

from app.main import FRONTEND_DIST, app


def test_unknown_api_path_returns_404(client):
    """不存在的接口路径要如实返回 404，不能回退成前端页面（否则永远是 200）。"""
    response = client.get("/api/definitely-not-exist")
    assert response.status_code == 404


def test_unknown_api_path_returns_json_when_frontend_mounted(client):
    """前端产物存在时，兜底层也要给出 JSON 404，而不是 HTML 页面。"""
    if not FRONTEND_DIST.is_dir():
        pytest.skip("本机没有前端产物，跳过挂载场景")
    response = client.get("/api/definitely-not-exist")
    assert response.status_code == 404
    assert response.json()["code"] == 404


def test_frontend_route_still_falls_back_to_index(client):
    """前端路由（如 /projects/1/apis）刷新时要能拿到页面，不能被当成 404。"""
    if not FRONTEND_DIST.is_dir():
        pytest.skip("本机没有前端产物，跳过挂载场景")
    response = client.get("/projects/1/apis")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_missing_static_asset_returns_404(client):
    """找不存在的 js/css 要返回 404，而不是塞一个页面回去。"""
    if not FRONTEND_DIST.is_dir():
        pytest.skip("本机没有前端产物，跳过挂载场景")
    response = client.get("/assets/missing-file.js")
    assert response.status_code == 404
