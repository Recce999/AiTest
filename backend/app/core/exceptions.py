"""全局异常处理：业务异常返回友好提示，未捕获异常返回 500 并落日志。"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger


class BizError(Exception):
    """业务异常：主动抛出，例如“用户名已存在”“项目不存在”。"""

    def __init__(self, msg: str, code: int = 1):
        self.msg = msg
        self.code = code
        super().__init__(msg)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BizError)
    async def handle_biz_error(request: Request, exc: BizError):
        # HTTP 状态码保持 200，业务错误放在 code 里，前端好统一处理
        return JSONResponse(status_code=200, content={"code": exc.code, "msg": exc.msg, "data": None})

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        logger.exception("未捕获异常: {} {}", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"code": 500, "msg": "服务器内部错误", "data": None},
        )
