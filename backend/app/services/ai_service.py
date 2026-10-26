"""AI 用例生成。

两种模式：
1. 配了 LLM_API_KEY：调用大模型，让它按固定 JSON 结构输出；
2. 没配：走规则生成（按接口定义产出正常/边界/异常用例），保证离线也能演示。
面试重点：模型输出必须校验后再入库，不能直接信任。
"""
import json

import requests
from loguru import logger

from app.core.config import settings
from app.core.exceptions import BizError
from app.models.models import Api

PROMPT = """你是接口测试工程师。根据下面的接口定义，生成 5 条测试用例。
只输出 JSON 数组，不要解释。每个元素格式：
{"name":"用例名","payload":{},"assertions":[{"type":"status_code","expected":200}]}
断言类型只能是 status_code / json_field / max_duration。
接口定义：method={method}, path={path}, expected_status={expected_status}, body={body}"""


def _rule_based(api: Api) -> list[dict]:
    """不依赖网络与密钥的兜底生成：覆盖正常、边界、异常三类。"""
    base_assert = {"type": "status_code", "expected": api.expected_status}
    return [
        {
            "name": f"[正常] {api.method} {api.path} 返回成功",
            "payload": api.body or {},
            "assertions": [base_assert, {"type": "max_duration", "expected": 3000}],
        },
        {
            "name": f"[正常] 响应时间在 1s 内",
            "payload": api.body or {},
            "assertions": [base_assert, {"type": "max_duration", "expected": 1000}],
        },
        {
            "name": f"[边界] 空请求体",
            "payload": {},
            "assertions": [base_assert],
        },
        {
            "name": f"[异常] 不存在的路径应返回 404",
            "payload": {},
            "assertions": [{"type": "status_code", "expected": 404}],
        },
        {
            "name": f"[异常] 缺少必填参数",
            "payload": {},
            "assertions": [{"type": "status_code", "expected": 422}],
        },
    ]


def _llm_based(api: Api) -> list[dict]:
    prompt = PROMPT.format(
        method=api.method, path=api.path, expected_status=api.expected_status, body=json.dumps(api.body, ensure_ascii=False)
    )
    resp = requests.post(
        f"{settings.llm_base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": settings.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    # 模型常把 JSON 包在 ```json 里，先剥掉
    content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("模型返回的不是数组")
    return data


def generate_cases(api: Api, limit: int = 10) -> list[dict]:
    raw: list[dict]
    if settings.llm_api_key:
        try:
            raw = _llm_based(api)
            logger.info("AI 生成 {} 条用例（模型）", len(raw))
        except Exception as exc:  # 模型不稳时不能拖垮主流程
            logger.warning("模型调用失败，回退规则生成：{}", exc)
            raw = _rule_based(api)
    else:
        raw = _rule_based(api)
        logger.info("AI 生成 {} 条用例（规则兜底）", len(raw))

    # 无论哪种来源都要校验结构，防止脏数据入库
    cleaned: list[dict] = []
    for item in raw[:limit]:
        if not isinstance(item, dict) or "name" not in item:
            continue
        assertions = item.get("assertions") or []
        if not isinstance(assertions, list):
            raise BizError("模型返回的断言格式不正确")
        cleaned.append(
            {
                "name": str(item["name"])[:120],
                "payload": item.get("payload") or {},
                "assertions": [a for a in assertions if isinstance(a, dict)][:5],
            }
        )
    if not cleaned:
        raise BizError("未生成有效用例，请检查接口定义")
    return cleaned
