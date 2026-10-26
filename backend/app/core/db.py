"""数据库连接：引擎、会话、Base。

SQLite 换 MySQL 只需改 config 里的 database_url，这里一行都不用动。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

database_url = settings.database_url
# 部分云平台下发 postgres:// 前缀，SQLAlchemy 需要 postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# check_same_thread=False 是 SQLite 在 FastAPI 多线程下的必需参数
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(database_url, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """所有数据模型的基类。"""


def get_db():
    """FastAPI 依赖：每个请求拿一个会话，用完自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
