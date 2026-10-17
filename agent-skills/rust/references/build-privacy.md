# Rust 构建产物隐私

适用于 Rust 可分发的可执行文件、静态库、动态库及其构建、原生 SDK 打包和路径泄露排查。必须同时执行[构建路径隐私共用约束](../../security/references/build-path-privacy.md)中的原生依赖、签名状态、扫描及 qualification 门禁。普通业务代码修改不默认触发。

允许中性源码路径、模块名、相对文件名和必要上游来源信息，不承诺隐藏全部项目结构、任意编码数据或独立用户名字符串。`--release` 不是路径隐私保证；裁剪符号和映射路径需要分别配置、验证。

## 接入发布入口

- 先读取项目规则、manifest、workspace、MSRV / 工具链、release profile、Cargo 配置、CI、`build.rs` 和真实构建入口，扩展已有构建器，不另建平行流程。
- 发布构建使用锁定依赖和明确的 release profile，例如已有锁文件下的 `cargo build --locked --profile release`；保留原优化、features、架构、ABI 导出、链接参数及 panic 行为，不为隐私修改 panic 策略。
- 不修改全局 Cargo 配置，不自动安装工具、部署、发布或更新历史产物资格。

## 映射来源与参数

1. 在实际发布环境解析映射来源；构建器清理环境时在其受控环境内注入参数，不能仅依赖外部环境变量。不为此升级工具链。
2. 使用稳定版 rustc 的 `--remap-path-prefix=FROM=TO`，将真实路径前缀替换为固定虚拟前缀，例如 `/src`、`/cargo`、`/rust-toolchain`、`/build-home`、`/build-out`。虚拟前缀不得包含真实账号、主机名、私有仓库名或凭证。
3. 枚举实际 workspace、用户主目录、`CARGO_HOME`（未设置时通常为 `$HOME/.cargo`）、`rustc --print sysroot`、自定义 target / `OUT_DIR`、外部 path 依赖及 CI / 临时目录。映射是文本替换，不会自动解析符号链接或统一路径分隔符；按实际输入补充逻辑路径、物理路径和 Windows 路径变体。相对路径若含敏感前缀也必须映射，不能只检查绝对路径。
4. 多个规则命中时最后一个匹配生效；宽泛映射放前面，更具体的源码、Cargo 和工具链映射放后面。保留足够的相对目录结构用于诊断，避免把所有文件映成同一名字。

以下是参数结构示例，`<...>` 必须由实际构建环境解析并替换；Cargo 配置不会自动展开 `$HOME` 等 shell 变量。真实私有路径通过构建包装脚本或临时配置注入，不提交进公共仓库：

```toml
[build]
rustflags = [
    "--remap-path-prefix=<absolute-build-home>=/build-home",
    "--remap-path-prefix=<absolute-temp-root>=/build-temp",
    "--remap-path-prefix=<absolute-cargo-home>=/cargo",
    "--remap-path-prefix=<absolute-rust-sysroot>=/rust-toolchain",
    "--remap-path-prefix=<absolute-workspace>=/src",
    "--remap-path-prefix=<absolute-target-root>=/build-out",
]
```

## 确保实际生效

- Cargo 按顺序选择 `CARGO_ENCODED_RUSTFLAGS`、`RUSTFLAGS`、匹配的 `target.*.rustflags`、`build.rustflags`，不是把四层全部合并。审计 `CARGO_TARGET_<TRIPLE>_RUSTFLAGS` 等 target 环境变量及 Cargo 配置，先解析原有效参数，再合并路径映射；环境 flags 可能覆盖配置，不能默默丢失原配置。
- 注入前保留必要 linker、SONAME、页面对齐、sysroot 及其他平台参数，不只保留路径选项。不能仅测试 flags 字符串存在，而不验证实际编译 / 链接行为。
- 工具链支持 `--remap-path-scope` 时，保留默认的完整映射范围；不得仅映射 `debuginfo` 而遗漏宏展开和 panic 路径。不为旧工具链默认追加它不支持的参数，仅设置前缀映射即可。
- 路径含空格时，不用未经验证的空格拼接 `RUSTFLAGS`。优先使用 Cargo 配置数组，或用 U+001F 分隔参数的 `CARGO_ENCODED_RUSTFLAGS`；保留原有效参数和正确编码。
- 参数必须到达目标 crate 及重新编译的依赖；仅 `cargo rustc -- ...` 给最终 crate 追加参数不足。使用 `--target` 时 flags 通常仅传给目标编译，host build script / proc-macro 不在同一覆盖范围；核查它们生成或嵌入的内容。需要查看详细编译命令时在本地检查，公开日志只保留脱敏证据。
- 路径映射不会重写已编译的标准库、原生库或预编译对象。实际工具链若已用 `/rustc/<hash>/...` 这类不含本机账号的虚拟路径，允许保留；不得为追求空路径无故启用 nightly 或重建标准库。发现真实私有路径时处理对应来源并保留验证门禁。

## 调试信息及其他来源

- release 默认关闭调试信息，SDK 优先 `strip = "debuginfo"` 以保留必要链接符号；不要给 SDK 套用 `strip = "symbols"` 而破坏链接或 ABI。检查 MSRV 支持情况，workspace profile 在根 manifest 配置，保留既有优化、LTO 和 panic 策略。例如合并到现有 release profile：

  ```toml
  [profile.release]
  debug = 0
  strip = "debuginfo"
  ```
- strip 不会删除 `file!()`、panic 位置及其他程序字符串中的路径。`env!("CARGO_MANIFEST_DIR")`、`env!("OUT_DIR")`、`option_env!`、`include_str!`、生成代码、`build.rs` 和版本注入不得把真实构建环境作为业务字符串嵌入；修复信息来源，而不是认为路径映射会修改任意字符串。
- `cc` / CMake、汇编、外部链接器及静态 / 动态库执行共用原生依赖约束：检查 CFLAGS、CXXFLAGS、target 变体及 cc-rs shell 转义解析。Rust 参数不能覆盖其全部行为。
- 预编译标准库的调试路径可能进入静态 archive；按目标格式仅剥离调试信息后验证真实链接。macOS OSO、dylib install name、Windows PDB 等按实际平台检查；Mach-O 修改仅允许明确 unsigned / ad-hoc 状态，不能覆盖正式签名或在未知状态下继续。
- 调试符号、PDB/dSYM、原始日志和私有构建收据不随公开包分发；需要诊断信息时受控保存并检查路径，不能未经评估删除必要链接符号。

## 发布前验证

1. 在 qualification、打包或分发前检查实际可执行文件、库及解包内容，包括缓存复用产物和预编译依赖；各目标分别验证，不能只检查中间 `.rlib` 或本机样例。
2. 运行共用约束中的流式扫描，覆盖源码根、主目录、Cargo 缓存、sysroot、target / `OUT_DIR`、CI、临时目录及平台主目录模式。验证空格、非 ASCII 用户名、UTF-8、UTF-16LE/BE 和跨块路径；失败返回非零状态、拒绝 qualification，错误仅输出固定分类。
3. 实际编译验证 `file!()`、原生依赖的 `__FILE__` 和生成代码；在隔离环境运行安全的错误 / panic / backtrace 场景，确认位置为中性或相对路径。环境字面值与源字符串单独处理，不能以修改 panic hook 代替产物清理。
4. 按实际改动验证参数合并、环境优先级与平台参数保留、静态 SDK 真实链接、动态库加载和必要 ABI 导出；涉及签名修改时覆盖共用约束的 unsigned、ad-hoc、正式签名及未知状态分支。
5. 构建 helper 纳入现有输入固定和来源记录。区分配置测试、编译器 fixture、完整产品构建及平台验收，说明覆盖入口、已验证产物及未验证平台；旧二进制、旧哈希及旧验收记录需重新构建、扫描并按原流程验收，不自动继承新约束。

## 官方依据

访问日期：2026-10-17。以项目锁定的 rustc / Cargo 支持为准；不默认依赖 nightly 的路径裁剪功能。

- [rustc 源码路径映射：文本替换、规则顺序及平台限制](https://doc.rust-lang.org/rustc/remap-source-paths.html)
- [Cargo 配置：rustflags 优先级、编码与 target 范围](https://doc.rust-lang.org/cargo/reference/config.html#buildrustflags)
- [Cargo profiles：debug、strip 与 workspace](https://doc.rust-lang.org/cargo/reference/profiles.html)
