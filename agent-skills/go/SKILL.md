---
name: go
description: Apply project-aware Go conventions for services, CLIs, packages, APIs, and tests.
---

# Go Skill（for Agents）

## 适用场景
- Go 服务端、CLI、库、网关、基础设施组件（K8s 工具等）
- API 与数据库交互、消息队列、gRPC、HTTP 服务
- 任务主导词：`golang`, `go`, `net/http`, `gin`, `grpc`, `sql`

## 强制执行

1. **先读模块边界**：先确认 `go.mod`、调用链、依赖图。
2. **最小补丁**：优先局部改动，避免引入额外并发通路。
3. **并发先评审**：涉及共享状态必须先评估竞态与生命周期。
4. **行为可验证**：`go test` 与 `go vet` 是最低验证线。

## 编码原则

- 对外入口优先显式 `context.Context`，在超时/取消点做兜底。
- 错误必须返回且携带上下文：`fmt.Errorf("xxx: %w", err)`。
- `defer` 只在安全可读场景使用，hot path 优先显式关闭。
- 避免 map/slice 并发读写，使用锁或 channel 保护。
- 关键业务逻辑与 transport 解耦，便于测试替身。
- 长期 Goroutine 负责域写入可恢复错误并可观察（trace/job id）。

## 常用检查清单

- `gofmt -w ./...`
- `go vet ./...`
- `go test ./...`
- `golangci-lint run`（如仓库启用）
- `go test -race`（并发变更后优先）

## 业务场景建议

- API 层：参数校验在 handler/adapter，核心逻辑放 service。
- 数据库层：预处理语句、事务边界明确，连接池统一配置。
- 异步任务：错误日志包含 trace/job id，区分可重试与不可重试错误。

## 触发最小文件规则
- `go`/`golang` 任务默认加载 `go`。
- `go` + `testing` 只补充 `testing`，不额外加语言外规则，保持最小集合。
- `go` + `api` 且出现鉴权或安全关键词时再补 `api-contract` 与 `security`。

## 常见反模式（避免）

- 忽略 `ctx` 导致泄漏或挂起
- 共享可变全局变量无同步
- 在 hot path 使用高频 `defer` 导致可见吞吐下降
- 直接 `panic` 作为业务控制流

## 与其他技能协作

- API 合约调整：`api-contract`
- 后端分层重构：`backend`
- 生产架构、性能与工具链专项：`go-pro`
- goroutine/channel/取消/背压专项：`go-concurrency`
- 并发与性能压测：`database-performance` / `quality-gates`
