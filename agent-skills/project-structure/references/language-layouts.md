# Language Layout Profiles

这些是绿地默认，不覆盖已经成立的项目约定、框架脚手架或 workspace 配置。

## Python

```text
project/
├── pyproject.toml
├── src/<package>/
├── tests/
├── scripts/
└── docs/
```

测试目录镜像生产包。应用入口、迁移和资源放在拥有它们的 package 内；不要同时维护互相重叠的根 package 与 `src/` package。

## Go

```text
project/
├── go.mod
├── cmd/<app>/
├── internal/<domain-or-adapter>/
├── api/                 # 仅在拥有外部契约时
├── scripts/
└── docs/
```

测试通常以 `_test.go` 与 package 共置，fixture 使用 `testdata/`。只有代码明确面向外部项目复用时才创建 `pkg/`。

## Rust

```text
project/
├── Cargo.toml
├── src/lib.rs | src/main.rs
├── src/bin/
├── tests/
├── examples/
└── benches/
```

workspace 项目把 crate 放入现有成员目录；单元测试可与模块共置，跨 crate 行为进入 `tests/`。

## Java

```text
project/
└── src/
    ├── main/java/
    ├── main/resources/
    ├── test/java/
    └── test/resources/
```

遵循 Maven/Gradle source set；生成源码必须使用构建工具配置的 generated source 路径。

## JavaScript / TypeScript

普通服务或库默认使用 `src/`。测试采用仓库既有的共置方式或 `tests/`，不得在同一 package 混用两套无明确边界的约定。Next、Nuxt、SvelteKit、Angular 等框架保留目录优先于通用模板。

## C# / .NET

```text
project/
├── <solution>.sln
├── src/<Project>/
├── tests/<Project>.Tests/
└── docs/
```

公共构建设置保留在 solution 根；项目源码和资源进入对应 `.csproj`，不要在 solution 根散放 `.cs` 文件。

## Android

使用模块内 `src/main/`、`src/test/`、`src/androidTest/`；资源进入对应 source set。不要绕过 Gradle module 边界创建平行源码树。

## iOS

遵循现有 Xcode project/workspace 和 target：生产源码、Unit Tests、UI Tests、资源分别归属目标 target。文件系统路径与 Xcode group 不一致时先确认项目现状。

## Monorepo

```text
repository/
├── apps/                 # 面向用户的应用
├── services/             # 可独立部署的服务，可按现有工具省略
├── packages/ | libs/     # 共享包，二选一并遵循现状
├── tools/
└── docs/
```

由 workspace 工具决定真实边界。每个子项目保留自己的 manifest、测试和文档；不要把不同语言的实现混进同一个 package 目录。
