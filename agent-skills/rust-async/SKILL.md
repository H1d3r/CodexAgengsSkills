---
name: rust-async
description: Design Rust async tasks, cancellation, timeouts, backpressure, and Tokio lifecycle behavior.
---

# Rust Async Patterns（for Agents）

## 适用场景
- Tokio、async trait、streams、channels、并发网络服务和异步资源管理
- 异步代码中的取消、超时、背压、任务泄漏或死锁问题

## 设计规则

1. 明确 runtime 所有权与入口；不要在已有 runtime 中嵌套启动 runtime。
2. 每个 spawned task 都要有生命周期、取消路径和错误处理者。
3. 外部 I/O 设置 timeout；把可重试、不可重试和取消错误分开。
4. 跨 `await` 不持有 `std::sync::MutexGuard` 或长时间占用阻塞资源。
5. stream、channel 和 buffer 设定容量与背压策略，避免无界积压。

## Tokio 检查点

- `JoinHandle` 要么被等待，要么有明确的 abort/监督机制。
- `select!` 分支取消后，检查被中断操作是否留下半完成状态。
- CPU 密集任务移出异步 worker；阻塞库使用受控的 `spawn_blocking`。
- shutdown 先停止接收新工作，再等待在途任务和依赖关闭。

## 验证

```bash
cargo fmt --check
cargo test --workspace
cargo clippy --workspace -- -D warnings
```

针对竞态、取消和超时增加 deterministic test；不要用任意 sleep 代替同步信号。
