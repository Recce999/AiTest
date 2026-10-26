"""日志：同时输出到控制台与文件，按天切割、保留 7 天。"""
import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


def setup_logger() -> None:
    Path("logs").mkdir(exist_ok=True)
    logger.remove()  # 去掉默认 handler，避免重复输出

    logger.add(
        sys.stdout,
        level="DEBUG" if settings.debug else "INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | "
        "<cyan>{name}</cyan>:{line} - {message}",
    )
    logger.add(
        "logs/aitest_{time:YYYY-MM-DD}.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
    )
