"""应用入口：装配路由、中间件、异常处理、日志、建表。

启动：uvicorn app.main:app --reload
文档：http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import apis, auth, cases, health, projects, runs
from app.core.config import settings
from app.core.db import Base, engine
from app.core.exceptions import register_exception_handlers
from app.core.logger import setup_logger
from app import models  # noqa: F401  必须导入，否则建表时找不到模型


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    Base.metadata.create_all(bind=engine)  # 开发期自动建表；生产建议用 Alembic 迁移
    logger.info("{} 启动，debug={}", settings.app_name, settings.debug)
    yield
    logger.info("{} 已关闭", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="接口自动化测试平台：录入接口 → AI 生成用例 → 执行 → 报告",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router)
for module in (auth, projects, apis, cases, runs):
    app.include_router(module.router, prefix="/api")


# ---------- 前端静态文件（生产镜像里由同一个容器托管） ----------
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


class SPAStaticFiles(StaticFiles):
    """找不到静态文件时回退到 index.html，交给 vue-router 处理前端路由。

    只有「像前端路由」的路径才回退。接口路径与静态资源必须如实返回 404，
    否则兜底会把所有不存在的地址都变成 200 + HTML，调用方和测试工具都拿不到真实状态码。
    """

    async def get_response(self, path: str, scope):
        # Windows 下 StaticFiles 会把分隔符规范化成反斜杠，这里统一回斜杠再判断
        normalized = path.replace("\\", "/").lstrip("/")
        try:
            return await super().get_response(normalized, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404:
                raise
            if self._is_frontend_route(normalized):
                return await super().get_response("index.html", scope)
            return JSONResponse(
                status_code=404,
                content={"code": 404, "msg": f"接口不存在：/{normalized}", "data": None},
            )

    @staticmethod
    def _is_frontend_route(path: str) -> bool:
        path = path.replace("\\", "/").lstrip("/")
        if path in ("", "index.html"):
            return True
        # 接口路径交给后端返回真实的 404，不能回退成页面
        if path == "health" or path.startswith("api/"):
            return False
        # 带扩展名的请求是静态资源（js/css/png…），找不到就是真的找不到
        return "." not in path.rsplit("/", 1)[-1]


# 本地开发只跑后端时 dist 不存在，跳过挂载；Docker 构建后自动生效
if FRONTEND_DIST.is_dir():
    app.mount("/", SPAStaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
