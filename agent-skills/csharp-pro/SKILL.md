---
name: csharp-pro
description: Use modern C# typing, nullable analysis, async, dependency injection, and performance practices.
---

# C# Pro Skill（for Agents）

## 适用场景
- 现代 C#、.NET 生产服务、库、后台任务和企业应用
- records、nullable reference types、pattern matching、LINQ、DI、async/await、Span 或性能分析

## 执行顺序

1. 先读取目标 framework、`Directory.Build.props`、集中包管理、分析器和 CI。
2. 让 nullable、异步、取消、异常和资源生命周期在公共边界明确表达。
3. 使用 records/不可变 DTO 表达数据；用 composition 和 DI 管理依赖。
4. 先以测试或 benchmark 建立行为和性能基线，再优化 LINQ、分配或线程调度。
5. 公共 API、序列化字段和 NuGet 依赖变更必须检查兼容性。

## 关键规则

- I/O 使用 async API 并传递 `CancellationToken`；禁止 `.Result`、`.Wait()` 和同步阻塞异步调用。
- `HttpClient` 通过 `IHttpClientFactory` 或仓库既有抽象管理；不要每次请求 new client。
- 使用 `ILogger` 记录可检索上下文，不记录 token、密码或完整个人敏感数据。
- LINQ 先保证语义，再关注枚举次数、数据库翻译、N+1 和分配。
- `Span<T>`、池化和 value type 只在 profile 证明热路径收益后引入。

## 验证

```bash
dotnet format --verify-no-changes
dotnet build
dotnet test
```

按仓库目标 framework 和 analyzer 调整命令；不要自动修改生成文件。

## 协作关系

- ASP.NET Core/EF Core：`dotnet-backend`
- API 契约：`api-contract`
- 测试与质量：`testing`、`quality-gates`
