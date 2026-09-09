---
name: rust-pro
description: Handle advanced Rust ownership, lifetimes, traits, unsafe code, FFI, and measured performance work.
---

# Rust Pro Skill（for Agents）

## 适用场景
- 需要所有权、生命周期、trait、零成本抽象、性能或安全边界的 Rust 任务
- 服务端、CLI、系统组件、FFI、序列化和跨线程数据流

## 执行顺序

1. 先读取 `Cargo.toml`、workspace、feature、MSRV、构建脚本和 CI 约定。
2. 先画清所有权、借用、生命周期和线程边界，再决定 clone、Arc 或内部可变性。
3. 公共错误使用明确枚举；业务错误用 `thiserror`，应用聚合用 `anyhow`。
4. 任何 `unsafe`、FFI 或性能改动都写出不变量和验证方式。
5. 修改公共 trait、泛型或 feature 时搜索调用方与编译矩阵。

## 类型与性能

- 优先用类型表达状态和不变量，避免用裸 `String`、整数或布尔值承载多个语义。
- 跨 `await` 不持有阻塞锁；避免为满足借用检查器而盲目 clone 大对象。
- 先用 benchmark、`criterion`、profile 或 flamegraph 定位，再优化分配和拷贝。
- 生产路径不使用 `unwrap`、`expect` 或 `panic!`，除非不变量已在边界证明并有说明。

## 安全与验证

- `unsafe` 代码最小化并集中隔离；检查别名、生命周期、对齐、初始化和线程安全不变量。
- 外部输入先解析和验证；文件、网络、数据库资源通过 RAII 正确释放。
- 运行 `cargo fmt --check`、`cargo check --workspace`、`cargo test --workspace`，并按仓库约定执行 clippy。

## 协作关系

- Tokio/async：`rust-async`
- 高频项目补充：`rust-pro` / `rust-async`
- 通用测试与质量：`testing`、`quality-gates`
