---
name: go-concurrency
description: Design and review Go concurrency, cancellation, backpressure, goroutine ownership, and shutdown behavior.
---

# Go Concurrency Patterns（for Agents）

## 适用场景
- goroutine、channel、worker pool、errgroup、取消传播和竞态修复
- 并发网络服务、后台任务、批处理、限流、背压和资源生命周期

## 设计清单

1. 为每个 goroutine 写出启动者、所有者、退出条件和错误回收者。
2. 根 context 负责取消；子任务不得在父任务退出后继续泄漏运行。
3. 明确 channel 的关闭方；接收方不要关闭不拥有的 channel。
4. 有界队列优先于无界队列，满载时定义阻塞、丢弃或降级策略。
5. 共享可变状态优先减少共享；必须共享时选择 mutex、atomic 或单线程 owner，并说明原因。

## 错误与超时

- 使用 `errgroup.WithContext` 聚合相关任务，首个不可恢复错误触发取消。
- 每个外部 I/O 都有 deadline；重试必须区分可重试错误并设置上限和退避。
- 任务退出前释放 ticker、连接、文件和临时资源；不要依赖进程结束清理。
- 关闭服务时先停止接收，再等待在途任务，最后关闭依赖。

## 验证

```bash
go test -race ./...
go test -run TestName -count=50 ./path/to/pkg
go test -bench=. -benchmem ./path/to/pkg
```

用 `go.uber.org/goleak` 或等价工具时，只在仓库已有约定下引入；不要用 sleep 证明没有泄漏。

## 反模式

- fire-and-forget goroutine 没有取消和错误通道
- 用 channel 代替所有锁，导致所有权更不清晰
- 用无界 goroutine 扛流量，最终耗尽内存或连接池
- 竞态测试未通过却声称并发修复完成
