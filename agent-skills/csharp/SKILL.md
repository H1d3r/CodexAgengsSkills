---
name: csharp
description: Apply project-aware C# conventions for applications, libraries, APIs, and tests.
---

# C# Skill（for Agents）

## 适用场景
- ASP.NET Core / Web API / 微服务 / MCP 或后台服务
- 数据访问、DI、鉴权、并发与中间件任务
- 任务主导词：`csharp`, `c#`, `dotnet`, `asp.net`, `mvc`, `entityframework`

## 强制执行

1. **先读项目约定**：优先加载 `Directory.Build.props`、`Directory.Packages.props`、CI 配置。
2. **最小变更**：不引入与当前任务无关的新框架或过度抽象。
3. **异步优先**：I/O 与外部调用统一 `async/await`。
4. **可观测优先**：关键路径要有可追踪日志和 trace id。

## 关键规则

- `HttpClient`, 数据库、外部 SDK 使用异步 API。
- 避免在业务逻辑中随处 `new` 服务；DI 注册集中在启动阶段。
- 避免 `.Result` / `.Wait()` 造成线程阻塞（尤其在 ASP.NET 上下文）。
- 启用可空上下文（`nullable`）时补齐空值处理分支。
- 错误处理显式分支，避免空 catch。
- 使用 `ILogger` 且日志包含请求上下文（Correlation-Id / UserId / TraceId）。

## 常用质量命令

- `dotnet format`
- `dotnet restore`
- `dotnet build`
- `dotnet test`

## 常见反模式（避免）

- 把领域逻辑放到 Controller 或 Middleware
- `catch (Exception)` 后吞掉不记录
- Controller 中直接处理数据库/外部 API 细节
- 用 `DateTime` 处理跨时区时间

## 触发最小文件规则

- `csharp` / `c#` 默认加载 `csharp`。
- `csharp` + `testing` 同时加载 `testing`。
- `csharp` + `security` 同时加载 `security`。
- `asp.net` + `api` 时优先对齐 `api-contract`。

## 与架构建议

- 与数据库密集逻辑关注 N+1、连接池、事务边界。
- API 返回建议统一错误码 + 多语言文案；文案与后端语言策略一致。
- 如涉及高并发，先验证中间件和数据库连接池设置再上线。

## 与其他技能协作

- 接口契约/字段变更先对齐 `api-contract`
- 现代 C#、nullable、DI、async 与性能专项：`csharp-pro`
- ASP.NET Core、EF Core、认证与后台服务：`dotnet-backend`
- 测试优先读 `testing` / `quality-gates`
