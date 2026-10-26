"""请求与响应模型：负责校验输入、裁剪输出（绝不把 password_hash 返回给前端）。"""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------- 认证 ----------
class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=64)


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class TokenOut(BaseModel):
    token: str
    user: UserOut


# ---------- 项目 ----------
class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    base_url: str = Field(min_length=1, max_length=255)
    description: str = ""


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    base_url: str
    description: str
    created_at: datetime


# ---------- 接口 ----------
class ApiIn(BaseModel):
    project_id: int
    name: str
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "GET"
    path: str = "/"
    headers: dict = {}
    body: dict = {}
    expected_status: int = 200


class ApiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    name: str
    method: str
    path: str
    headers: dict
    body: dict
    expected_status: int


# ---------- 用例 ----------
class CaseIn(BaseModel):
    api_id: int
    name: str
    payload: dict = {}
    assertions: list[dict[str, Any]] = []
    enabled: bool = True


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    api_id: int
    name: str
    payload: dict
    assertions: list
    enabled: bool
    source: str


# ---------- 执行 ----------
class RunIn(BaseModel):
    project_id: int
    case_ids: list[int] | None = None  # 不传则执行该项目下全部启用的用例


class RunResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    case_id: int
    case_name: str
    status: str
    status_code: int | None
    response_body: str
    error_msg: str
    duration_ms: int


class RunOut(BaseModel):
    id: int
    total: int
    passed: int
    failed: int
    duration_ms: int
    results: list[RunResultOut]
