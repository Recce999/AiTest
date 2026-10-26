"""统一返回格式：所有接口都返回 {code, msg, data}。

为什么必须统一：前端只需要写一次拦截器，就能判断成功/失败；
测试同学也能用同一套断言规则覆盖全部接口。
"""
from typing import Any


def success(data: Any = None, msg: str = "ok") -> dict:
    return {"code": 0, "msg": msg, "data": data}


def fail(code: int = 1, msg: str = "error", data: Any = None) -> dict:
    return {"code": code, "msg": msg, "data": data}
