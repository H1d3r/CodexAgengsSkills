---
name: api-contract
description: Define and evolve API schemas, compatibility, authentication, errors, pagination, and examples.
---

# API Contract Skill（for Agents）

## 适用场景
- REST/GraphQL 接口设计、变更评审、版本治理
- API 文档、鉴权、错误码、分页策略制订

## 核心原则

1. **先定义消费者**：先明确是谁会调 API、多久调几次、错误如何恢复。
2. **先定义契约再编码**：资源模型、错误模型、鉴权、速率和版本先确定。
3. **向后兼容优先**：优先新增不影响旧字段，不拆解旧行为。

## 强制执行清单

- 统一资源命名与状态码映射。
- 错误模型区分业务错误与系统错误。
- 分页、排序、过滤与筛选有明确边界。
- 版本策略（URL/Header/参数）提前声明，不无感知变更。
- 请求/响应样例和异常样例在文档中可复现。

## 常用实践

- `GET` 幂等、`POST/PUT` 明确幂等/重试策略。
- 身份鉴权、速率限制、幂等键（Idempotency-Key）按场景评估。
- schema 变更采用 `new field optional -> deprecate -> remove`。
- 合理选择 API 风格：REST 与 GraphQL 按消费方和演进成本决定。

## 反模式（避免）

- 未声明 breaking change 直接改字段语义。
- 同时混用多套错误码策略。
- 接口成功码泛化导致调用方无法分流。
- 文档滞后于实现（上线前一定回填）。

## 与项目约束优先级

- 以 OpenAPI/GraphQL schema 与网关/代理配置为准。
- 若文档与实现冲突，以 CI 合并规范和项目审阅结果为准。

## 国际化错误

- 需要多语言响应时，以稳定错误码作为程序契约，本地化消息只用于展示。
- `Accept-Language`、自定义语言头、默认语言和不支持语言的行为必须在契约中声明。
