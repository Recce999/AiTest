"""执行引擎：把一条用例变成一次真实 HTTP 请求，再按断言判定通过/失败。

这是整个项目最核心、面试最值得讲的文件。
"""
import ipaddress
import json
import socket
import time
from urllib.parse import urlparse

import requests
from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BizError
from app.models.models import Api, Case, Project, Run, RunResult


def _guard_target(url: str) -> None:
    """SSRF 防护：不允许请求内网/回环地址（生产环境）。"""
    host = urlparse(url).hostname or ""
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
    except (socket.gaierror, ValueError):
        raise BizError(f"目标地址无法解析：{host}")
    if (ip.is_private or ip.is_loopback) and not settings.allow_private_target:
        raise BizError(f"目标地址属于内网网段，已拦截：{ip}")


def _pick(data, path: str):
    """按 a.b.0.c 的形式从嵌套 JSON 里取值。"""
    cur = data
    for part in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(path)
    return cur


def _judge(assertions: list, status_code: int, body, duration_ms: int, expected_status: int) -> list[str]:
    """返回失败原因列表；空列表代表全部通过。"""
    failures: list[str] = []

    if expected_status and status_code != expected_status:
        failures.append(f"状态码必须等于 {expected_status}，实际返回 {status_code}")

    for item in assertions or []:
        kind = item.get("type")
        expected = item.get("expected")
        if kind == "status_code":
            if status_code != expected:
                failures.append(f"状态码必须等于 {expected}，实际返回 {status_code}")
        elif kind == "json_field":
            path = item.get("path", "")
            try:
                actual = _pick(body, path)
            except (KeyError, IndexError, ValueError, TypeError):
                failures.append(f"返回内容里找不到字段 {path}")
                continue
            if actual != expected:
                failures.append(f"返回内容里 {path} 必须等于 {expected}，实际是 {actual}")
        elif kind == "max_duration":
            if duration_ms > int(expected):
                failures.append(f"响应耗时 {duration_ms} 毫秒，超过了允许的 {expected} 毫秒")
        else:
            failures.append(f"不认识的断言类型：{kind}")
    return failures


def execute_case(project: Project, api: Api, case: Case) -> RunResult:
    url = project.base_url.rstrip("/") + "/" + api.path.lstrip("/")
    method = api.method.upper()
    headers = dict(api.headers or {})
    body = case.payload if case.payload else (api.body or {})

    result = RunResult(case_id=case.id, case_name=case.name, status="error", duration_ms=0)

    try:
        _guard_target(url)
    except BizError as exc:
        result.error_msg = exc.msg
        return result

    start = time.perf_counter()
    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            json=body if method in ("POST", "PUT", "PATCH") else None,
            params=body if method == "GET" else None,
            timeout=settings.request_timeout,
        )
        duration_ms = int((time.perf_counter() - start) * 1000)
        try:
            parsed = resp.json()
        except json.JSONDecodeError:
            parsed = resp.text[:2000]

        failures = _judge(case.assertions or [], resp.status_code, parsed, duration_ms, api.expected_status)
        result.status = "passed" if not failures else "failed"
        result.status_code = resp.status_code
        result.response_body = json.dumps(parsed, ensure_ascii=False)[:4000]
        result.error_msg = "；".join(failures)
        result.duration_ms = duration_ms
    except requests.Timeout:
        result.error_msg = f"请求超时（{settings.request_timeout}s）"
        result.duration_ms = int((time.perf_counter() - start) * 1000)
    except requests.RequestException as exc:
        result.error_msg = f"请求异常：{exc}"
        result.duration_ms = int((time.perf_counter() - start) * 1000)

    return result


def execute_run(db: Session, project: Project, cases: list[Case]) -> Run:
    if not cases:
        raise BizError("没有可执行的用例")

    run = Run(project_id=project.id, total=len(cases))
    db.add(run)
    db.flush()  # 先拿到 run.id

    started = time.perf_counter()
    for case in cases:
        api = db.get(Api, case.api_id)
        if api is None:
            continue
        res = execute_case(project, api, case)
        res.run_id = run.id
        db.add(res)
        if res.status == "passed":
            run.passed += 1
        else:
            run.failed += 1

    run.duration_ms = int((time.perf_counter() - started) * 1000)
    db.commit()
    db.refresh(run)
    logger.info("执行完成 run={} 总{} 通过{} 失败{}", run.id, run.total, run.passed, run.failed)
    return run
