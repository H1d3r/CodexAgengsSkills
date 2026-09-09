---
name: python-testing-patterns
description: Apply pytest fixtures, mocks, parametrization, async tests, and property-based testing safely.
---

# Python Testing Patterns（for Agents）

## 适用场景
- Pytest 测试体系、fixture、mock、参数化、异步测试和回归测试
- 外部 API、数据库、队列等依赖的可控测试
- 属性测试、覆盖率、测试隔离和 CI 测试稳定性

## 核心规则

1. 每个测试只验证一个可观察行为，并在名称中说明场景和结果。
2. 新行为至少覆盖成功路径和失败或边界路径；先保留失败证据，再实现修复。
3. fixture 只负责生命周期和共享准备，避免隐藏业务断言与跨测试污染。
4. mock 外部副作用，但不要 mock 被测逻辑本身；关键集成路径使用真实边界测试。
5. 异步测试显式等待任务完成，验证取消、超时、重试和并发竞态。

## 推荐模式

- 用 `pytest.mark.parametrize` 覆盖输入矩阵，避免复制近似测试。
- 用 factory 或 builder 构造测试数据；敏感字段使用固定假值，不使用真实凭据。
- 对序列化、验证和纯函数优先做属性测试；对数据库/API 使用最小集成测试。
- 覆盖率用于发现盲区，不把百分比当作行为正确性的替代品。
- CI 中区分快速单元测试、集成测试和需要外部服务的可选测试组。

## 常用命令

```bash
pytest -q
pytest -q --maxfail=1
pytest -q --cov=<package>
```

## 反模式

- 只断言状态码或 truthy，不验证关键字段和副作用
- 依赖真实第三方服务、当前时间或测试执行顺序
- 一个 fixture 隐式创建全局状态并被所有测试复用
- 用 `sleep` 掩盖异步竞态，而不等待事件或轮询条件

## 协作关系

- 基础 Python 约束：`python`、`python-pro`
- 方法学：`testing`、`tdd`
- API 变更：`api-contract`
