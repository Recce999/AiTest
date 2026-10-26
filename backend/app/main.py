"""应用入口：装配路由、中间件、异常处理、日志、建表。

启动：uvicorn app.main:app --reload
文档：http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

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
