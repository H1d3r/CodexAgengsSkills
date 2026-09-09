---
name: python-testing
description: Plan and implement Python tests with focused unit, integration, and regression coverage.
---

# Python Testing（for Agents）

## 适用场景
- Python 代码测试设计、Pytest 结构、fixtures、Mock 与边界测试
- 迁移到 `uv`/`ruff`/`mypy` 后的测试链路稳定性验证
- 任务主导词：`python-testing`, `pytest`, `hypothesis`, `mock`, `fixtures`

## 核心原则

- 测试要先于实现或紧接实现并说明“为什么失败”。
- 每个测试只验证一个行为。
- 保留失败到通过闭环；没有失败证据的测试改动不算完成。

## 强制清单

- 新增行为：至少一个成功 + 一个失败/边界测试。
- fixture 明确生命周期，避免跨测试污染。
- 第三方服务依赖采用 mock/stub，网络调用应可控。
- 参数化/属性测试按场景拆分，不做过宽断言。

## 推荐实践（Python）

- 优先 `pytest`，配合 `pytest-cov`、`pytest-xdist`（必要时）。
- 异步测试使用 `pytest.mark.asyncio` 或框架对应插件。
- 回归失败用例保留最小复现：输入、预期、日志线索。

## 常用命令

- `pytest -q`
- `pytest -q --maxfail=1`
- `pytest -q --cov=my_pkg`

## 反模式（避免）

- 只测“主流程成功”，不测异常路径
- 真实调用真实第三方服务
- 用大量 `print` 代替 assert
- 多个行为揉在一个测试名里

## 与其他技能协作

- 非 Python 语言测试策略：`testing`
- 回归与交付验收：`quality-gates`
- 涉及 API 契约变更：`api-contract`
