---
name: go-pro
description: Design production Go services with clear package boundaries, errors, observability, and performance evidence.
---

# Go Pro Skill（for Agents）

## 适用场景
- 生产级 Go 服务、CLI、库、网关、gRPC、消息处理和基础设施组件
- 需要模块边界、错误语义、性能、可观测性或可部署性的 Go 任务

## 执行顺序

1. 先读取 `go.mod`、构建标签、入口包、CI 命令和已有依赖约定。
2. 先确定 API 边界、生命周期、取消语义、错误分类和兼容性要求。
3. 让核心逻辑保持可测试；HTTP、数据库、消息队列放在明确的 adapter 边界。
4. 先用基准、pprof、trace 或指标定位瓶颈，再优化分配、锁和批处理。
5. 变更公共接口时搜索调用方并补充迁移或兼容策略。

## 语言与架构

- 对外部 I/O 入口传递 `context.Context`，不要把 context 存入结构体。
- 错误使用 `%w` 保留原因；用 `errors.Is`/`errors.As` 做可判断分类。
- 小接口应由使用方定义；避免为每个 struct 创建无行为的 repository 包装。
- 配置、日志、指标和依赖注入集中初始化；业务函数不读取全局环境变量。
- 数据库操作明确事务、连接池、分页、超时和重试边界。

## 并发与性能

- goroutine 必须有退出条件、所有权和错误回收路径；优先结构化生命周期。
- channel 用于通信或所有权转移；共享状态需要明确同步原语和竞态测试。
- 避免无界队列、无界重试、循环创建 goroutine 和把 `panic` 当业务控制流。
- 使用 `go test -race`、benchmark、pprof 前后对比证明优化有效。

## 验证

```bash
gofmt -w .
go test ./...
go test -race ./...
go vet ./...
```

只执行仓库支持的命令；不要因格式化而改动无关文件。

## 协作关系

- 并发专项：`go-concurrency`
- 后端/API：`backend`、`api-contract`
- 测试与交付：`testing`、`quality-gates`
