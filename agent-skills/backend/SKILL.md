---
name: backend
description: Design or modify backend routes, services, repositories, configuration, and error handling with clear boundaries.
---

# Backend Development Skill（for Agents）

## 适用场景
- Node.js / TypeScript 后端服务、Express/Fastify/Nest 代码改造
- API 路由、控制器、服务层、仓储层、数据库访问、错误追踪类任务

## 核心原则

1. **分层不跳层**：`Route -> Controller -> Service -> Repository -> DB`
2. **可验证性优先**：先评估业务风险，再决定是否加测试与观测
3. **可维护优先**：控制器负责编排，业务放在 Service；DB 操作封装在 Repository

## 任务前快速检查（Backend Feasibility）

- 架构契合度（1~5）
- 业务复杂度（1~5）
- 数据风险（1~5）
- 运维风险（1~5）
- 可测试性（1~5）

建议：`(架构 + 可测试性) - (复杂度 + 数据风险 + 运维风险)` 若结果过低，先降级为试验路径。

## 强制执行清单

- 外部输入必须统一校验（schema/zod/validator）。
- Route 层仅做入参解析与响应拼接，不处理业务。
- Service 层用构造器注入依赖，避免内部 `new`。
- 数据库客户端不要在 controller 直接使用，统一 repository。
- 禁止裸 `process.env`：统一 config 模块。
- 异步错误必须链上报到可观测体系（Sentry/日志）。
- 每个业务变更至少补充一个单元/集成测试。

## 常用质量门禁

- `npm/yarn/pnpm test`（或 `go test` / `pytest` 按项目）
- `lint` + `format` + `typecheck`
- 覆盖核心路径：路由、service、仓储、错误分支

## 常见反模式（避免）

- 在路由直接写复杂事务逻辑。
- 业务代码里直接操作 SQL 字符串拼接。
- 静默捕获异常后返回通用失败。
- 依赖关系在 controller 直接 `new XxxRepo()`。
- 把关键字段直接放到 `req.body` 未校验即入库。

## 与项目冲突的优先级

- 以 `tsconfig/package.json` 的实际配置和现有框架规范为准。
- 与本文件不一致时，按项目约定与现有 CI 约束执行。

## 国际化边界

- 产品已启用 i18n 时，稳定错误使用语言无关错误码，消息在响应边界按项目约定本地化。
- 客户端语言头、默认语言和回退策略必须以现有 API 契约为准，不在业务层散落判断。
