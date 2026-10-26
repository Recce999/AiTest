# AITest · 轻量接口自动化测试平台

录入接口定义 → AI 生成测试用例 → 一键执行 → 可视化报告。

## 技术栈

| 层 | 选型 | 理由 |
| --- | --- | --- |
| 后端 | FastAPI + SQLAlchemy 2 + Pydantic v2 | 轻量、自带 OpenAPI 文档、代码量小 |
| 数据库 | SQLite（开发）→ MySQL（部署） | 零配置起步，上线只改一行 |
| 认证 | JWT + bcrypt | 无状态、部署简单 |
| 前端 | Vue3 + Vite + Element Plus + Pinia | 当前主流组合，组件齐全 |
| 部署 | Docker Compose + Nginx | 一条命令起服务 |

## 功能

- 注册 / 登录 / JWT 鉴权
- 项目、接口、用例三级管理（越权校验）
- 执行引擎：HTTP 请求 + 三类断言（状态码 / JSON 字段 / 响应耗时）
- 执行报告：通过率、失败原因、响应快照、历史记录
- AI 生成用例：大模型输出 + 结构校验，人工确认后入库；无密钥自动回退规则模板
- SSRF 防护：默认拦截内网目标（开发期可用开关放行）

## 目录结构

```text
aitest/
├── backend/
│   ├── app/
│   │   ├── main.py              # 入口：路由装配、CORS、异常、日志、建表
│   │   ├── api/                 # 路由层（只做参数校验与转发）
│   │   ├── core/                # 配置、数据库、安全、异常、日志
│   │   ├── models/              # 六张表
│   │   ├── schemas/             # 请求/响应校验
│   │   └── services/            # 业务层（认证、执行引擎、AI 生成、权限）
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # Vue3 + Vite + Element Plus
├── docs/                        # 设计说明书、手册、练习单
└── docker-compose.yml 等部署文件见 docs 第 9 章
```

## 本地启动

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

验证：`curl http://127.0.0.1:8000/health` → `{"code":0,...}`；文档 <http://127.0.0.1:8000/docs>

### 前端

```bash
cd frontend
pnpm install
pnpm dev
```

打开 <http://localhost:5173>，注册后登录。

## 接口一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | /health | 健康检查 |
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录 |
| GET | /api/auth/me | 当前用户 |
| GET/POST | /api/projects | 项目列表 / 新建 |
| PUT/DELETE | /api/projects/{id} | 更新 / 删除 |
| GET/POST | /api/apis | 接口列表 / 新建 |
| PUT/DELETE | /api/apis/{id} | 更新 / 删除 |
| GET/POST | /api/cases | 用例列表 / 新建 |
| PUT/DELETE | /api/cases/{id} | 更新 / 删除 |
| POST | /api/cases/ai-generate | AI 生成用例建议 |
| POST | /api/runs | 触发执行 |
| GET | /api/runs | 执行历史 |
| GET | /api/runs/{id} | 报告详情 |

## 开发约定

1. 所有接口返回 `{code, msg, data}`，`code=0` 表示成功；
2. 业务错误抛 `BizError`，不写 `try/except` 兜底；
3. 路由层不写业务逻辑，业务进 `services/`；
4. 配置只从 `core/config.py` 读，禁止硬编码；
5. 任何按 id 查数据的地方，都要走 `services/access.py` 校验归属。

## 断言格式

```json
[
  {"type": "status_code", "expected": 200},
  {"type": "json_field", "path": "data.status", "expected": "up"},
  {"type": "max_duration", "expected": 1000}
]
```
