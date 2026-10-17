---
name: rust
description: Apply project-aware Rust conventions for services, CLIs, libraries, async systems, and validation.
---

# Rust Skill（for Agents）

## 适用场景
- Rust 服务端、CLI、异步系统、系统工具
- tokio/axum/actix-web/sqlx/serde 等栈相关任务
- 任务主导词：`rust`, `tokio`, `cargo`, `clippy`, `thiserror`, `anyhow`

## 强制执行

1. **确认所有权与借用边界**：任何数据流变更先确认 Move、Borrow、生命周期。
2. **先做小补丁**：优先修复最小路径，不提前引入新抽象。
3. **错误语义分层**：业务错误、参数错误、外部错误分开表达。
4. **无回归测试不合入**：新行为至少补充一个可复现测试。

## 编译与发布隐私（强制）

- 配置发布构建、CI、容器、原生 SDK 打包或排查路径泄露时，读取 [references/build-privacy.md](references/build-privacy.md) 及其中的共用门禁，扩展实际构建入口；普通业务代码修改不默认触发。
- 公开可执行文件、静态库和动态库使用锁定依赖和明确的 release profile，并使用稳定版 `--remap-path-prefix=FROM=TO`。至少映射项目、主目录、Cargo 缓存、工具链、target 和临时构建目录，兼顾词法及解析后路径；宽泛映射在前、具体映射在后，覆盖依赖编译。
- 审计 encoded、普通环境、target 环境及 Cargo 配置中实际生效的 flags；保留参数边界，合并必要 linker、SONAME、页面对齐、平台参数、features 和架构。构建器清理环境时在其受控环境注入，不修改全局 Cargo 配置，不默认引入 nightly / `-Z`。
- release 默认 `debug = 0`；SDK 优先 `strip = "debuginfo"` 以保留必要链接符号，不为隐私改变 panic 策略。`--release` 或 strip 不能代替路径映射，也不能追溯修改预编译标准库或原生依赖。
- 禁止通过 `env!` / `option_env!`、`build.rs`、生成代码或资源，将真实构建路径、账号、主机名及凭证作为任意字符串嵌入发布产物；检查 `file!()`、panic 位置、`OUT_DIR` 和原生链接产物。
- qualification、打包或分发前扫描实际产物（含缓存及预编译依赖）；失败返回非零状态，不授予合格资格，也不输出敏感匹配值。SDK 验证真实链接、动态加载和必要导出；Mach-O 仅在已确认 unsigned / ad-hoc 状态下修改，正式签名及未知状态停止修改，旧产物资格不自动继承。

## 编码原则

- 避免生产路径使用 `unwrap` / `expect`（仅测试/明确不可能时）。
- 借用/持有规则可读：跨 `await` 避免持有重锁。
- 使用 `thiserror` 定义业务错误，`anyhow` 做应用层聚合。
- 不在核心逻辑散落 `String` 与 `&str` 转换，统一边界。
- 并发场景首选所有权转移清晰、避免过度克隆。
- `Result` 链路保留上下文并在边界统一落地。

## 常用命令（仓库常见）

- `cargo fmt --check`
- `cargo check --workspace`
- `cargo test --workspace`
- `cargo clippy --workspace -- -D warnings`

## 架构与质量建议

- 模块边界保持稳定：修改公共接口时同步评估调用方影响。
- 异步调用与超时：外部调用加超时与重试策略。
- 性能优化：通过基准测试或 `criterion` 评估后再改；避免过早优化。

## Skill 协作

- Rust 基础任务只加载本 skill。
- 所有权、trait、unsafe、FFI 与性能任务补充 `rust-pro`。
- Tokio、任务生命周期、取消与背压任务补充 `rust-async`。
- 通用测试方法在任务明确涉及 testing 时加载 `testing`。

## 目录与项目事实

- 遵循现有 Cargo workspace 和 crate 成员关系。
- 绿地默认使用 Cargo 的 `src/`、`tests/`、`examples/`、`benches/` 布局。
- 创建或移动文件时加载 `project-structure`，不复用历史客户项目目录作为全局模板。

## 反模式（避免）

- `panic!` 替代错误链传播。
- 并发场景无约束 clone 大对象。
- 通过 `Option`/`Result` 直接 `unwrap` 触发崩溃。
- 单文件承载业务、持久化和网络三层逻辑。

## 优先级

若通用建议与项目真实编译、依赖或更具体规则冲突，以项目事实为先并记录差异。
