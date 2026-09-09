---
name: api-design
description: Design APIs and integrations with explicit consumers, resources, errors, idempotency, and lifecycle decisions.
---

# API Design & Integration Skill（for Agents）

## 适用场景
- REST / GraphQL / gRPC / Webhook 接口设计与联调
- 接口兼容性、错误码、鉴权、限流、文档化相关任务

## 核心原则

1. **先定义契约**：先确认 schema/字段与错误模型，再改实现。
2. **稳定优先**：兼容优于重构，避免非必要 breaking change。
3. **可观测优先**：接口调用必须可追踪（trace id、请求时长、状态码）。

## 强制执行清单

- 统一错误模型：可区分业务错误与系统错误。
- 输入校验在边界层完成，并返回可操作错误信息。
- 鉴权/授权边界清晰，避免越权读取。
- 幂等性（尤其是写接口）要有明确策略与字段。
- 文档同步：OpenAPI/Proto/markdown 文档与代码行为保持一致。

## 推荐实践

- 接口变更流程：新增字段（向后兼容）→ 弃用注释 → 淘汰窗口 → 移除。
- 版本策略：通过 URL、Header 或字段控制版本，避免静默行为变更。
- 速率控制、超时和重试行为要记录在 API 约定中。
- 关键接口加压测和异常场景用例（超时、重试、重复提交）。

## 常用质量门禁

- Schema 校验（`openapi`/`protobuf` lint）
- 集成测试（happy path + 异常码 + 限流/鉴权）
- 契约测试（consumer/provider）
- Mock/Stub 回归覆盖

## 反模式（避免）

- 返回字段随意变更导致下游兼容性破坏。
- 错误码复用，导致调用方无法做正确重试或告警。
- 认证失败与业务失败用同一 code。
- 未写明超时、重试、幂等策略即上线。

## 与仓库冲突时的优先级

- 以 OpenAPI/Proto 与网关/网管配置为准。
- 与本文件冲突时按接口规范和测试报告执行。
