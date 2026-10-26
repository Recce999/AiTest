"""全局配置：所有可变量集中在 Settings，禁止在业务代码里硬编码。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 读取同目录上两级的 .env，缺失时使用下面的默认值（保证零配置可跑）
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AITest"
    debug: bool = True

    # 开发期用 SQLite，文件即数据库；上线换 MySQL 只改这一行
    database_url: str = "sqlite:///./aitest.db"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    # 执行引擎
    request_timeout: int = 5
    allow_private_target: bool = True  # 开发期允许打本机接口；上线必须改 false

    # 大模型（留空则走规则生成，不影响演示）
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-chat"


settings = Settings()
