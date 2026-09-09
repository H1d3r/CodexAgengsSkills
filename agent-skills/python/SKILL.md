---
name: python
description: Apply project-aware Python conventions for services, libraries, scripts, refactors, and validation.
---

# Python Skill（for Agents）

## 适用场景
- Python 服务端、脚本、数据处理、异步任务、CLI、自动化运维
- FastAPI/Django/Flask 任务、数据校验与接口服务
- 任务主导词命中：`python`, `fastapi`, `asyncio`, `pydantic`, `uv`, `pytest`

## 强制执行

1. **先确认运行时与依赖**：优先确认 Python 版本、依赖管理方式、执行入口。
2. **先定义边界**：输入输出、异常边界、超时与幂等先确定。
3. **小步改动**：优先局部修复，不跨模块重构。
4. **可复现验证**：每次行为变更给最小失败-通过测试闭环。

## 编码原则

- 统一定义边界对象：参数、响应、配置改造建议显式 dataclass/pydantic。
- I/O 并发优先考虑 `asyncio`；CPU 密集任务拆到线程池/进程池。
- 外部依赖异常必须分支捕获，禁止 `except Exception: pass`。
- 数据库/API 调用统一加超时与重试边界，避免无限阻塞。
- 文件与网络资源用上下文管理（`with` / `async with`）安全关闭。
- 日志要求有最小可追踪上下文（request id / trace id / correlation id）。

## 常用执行清单

### Python 项目常规检查
- `ruff format .`
- `ruff check .`
- `ruff check . --select I`（导入排序）
- `mypy .` 或 `python -m mypy src/`
- `pytest -q`

### API/服务任务
- 输入校验：`pydantic` / `pydantic-settings`（按项目约定）
- 异常映射：统一业务异常与外部依赖异常
- 返回值：关键接口返回结构明确（含状态码、错误码）
- 配置管理：禁止直接 `os.environ` 分散读取，集中到配置层

### 触发最小文件规则
- `python` 任务优先读 `python`。
- `python` + `testing` 时补齐 `python-testing`。
- 同时出现 `python` + `api` 时再加载 `api-contract` 进行接口约束对齐。

## 常见反模式（避免）

- 在循环中做无边界阻塞请求
- 用 `dict` 隐式传参导致边界不清
- 忽略事务或重试边界导致重复副作用
- 生产代码写死密钥/endpoint/token
- 大函数内同时做参数解析+业务处理

## 验证要求

- 行为改动至少有一条对应测试，至少包含 1 个失败和 1 个边界场景。
- 关键流程失败路径要有可读日志（trace id + 简短上下文）。

## 与其他技能协作

- 需要数据库迁移/索引时读 `database-performance`
- 需要 REST/GraphQL 契约时读 `api-contract`
- 现代 Python、工具链、异步和性能专项：`python-pro`
- 需要测试策略扩展时读 `python-testing` / `python-testing-patterns` / `testing`
- 多步骤任务仍按 `task-template` + `quality-gates`
