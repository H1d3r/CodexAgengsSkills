---
name: dotnet-backend
description: Design ASP.NET Core and EF Core services with clear layers, validation, security, and background work.
---

# .NET Backend Patterns（for Agents）

## 适用场景
- ASP.NET Core Web API、Minimal API、Controller、EF Core、Dapper、认证和后台服务
- 需要中间件、DI 生命周期、健康检查、缓存、限流或数据库性能判断的 .NET 任务

## 分层规则

- Endpoint/Controller 只做协议适配、授权和输入转换；领域逻辑放在 application/domain 层。
- DI 注册集中在启动组合根，区分 singleton、scoped、transient 的生命周期和线程安全。
- 使用 request/response DTO 隔离持久化模型；变更字段时同步 OpenAPI、客户端和迁移。
- 统一 ProblemDetails 或项目既有错误格式；不要把堆栈和内部 SQL 返回给客户端。

## 数据与外部调用

- EF Core 查询检查 N+1、投影、分页、`AsNoTracking`、事务和并发冲突。
- Dapper/原生 SQL 使用参数化；迁移、索引和连接池变更必须有回滚思路。
- 外部 HTTP 使用命名 client、超时、取消、有限重试和熔断边界；不要在 Controller 里直接 new SDK。
- 健康检查区分 liveness 与 readiness；后台服务支持优雅停止和失败可观测。

## 安全与验证

- 鉴权、授权、租户边界和资源所有权在服务端强制执行，不信任客户端传来的身份或角色。
- 日志脱敏，配置和密钥从安全配置源读取；不要提交 `appsettings.*` 中的真实秘密。
- 至少执行 `dotnet build`、`dotnet test`；数据库/HTTP 行为用集成测试验证，避免只测 Controller。

## 协作关系

- C# 基础与异步：`csharp`、`csharp-pro`
- API 设计：`api-design`、`api-contract`
- 数据库性能：`sql`、`database-performance`
