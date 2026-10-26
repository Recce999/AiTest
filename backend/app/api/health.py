"""系统接口：健康检查。部署后第一件事就是 curl 这个地址。"""
from fastapi import APIRouter

from app.core.config import settings
from app.core.response import success

router = APIRouter(tags=["系统"])


@router.get("/health", summary="健康检查")
def health():
    return success({"status": "up", "app": settings.app_name, "version": "0.1.0"})
