# Go 构建产物隐私

适用于 Go 可分发的可执行文件、静态库、动态库及其构建、打包和路径泄露排查。必须同时执行[构建路径隐私共用约束](../../security/references/build-path-privacy.md)中的原生依赖、签名状态、扫描及 qualification 门禁。普通业务代码修改不默认触发。

目标是避免泄露真实用户名、主目录、源码、依赖缓存及工具链安装路径；允许中性路径、模块名、导入路径、相对文件名及必要上游信息，不承诺隐藏全部项目结构、任意编码数据或独立用户名字符串。

## 构建入口

1. 读取项目规则、`go.mod`、工具链版本、构建脚本、CI、Dockerfile、发布配置、buildmode 和 CGO 设置，扩展已有构建器，区分本地诊断与可分发构建。保留既有优化、tags、架构、链接参数、ABI 导出和必要版本注入；不要全局执行 `go env -w GOFLAGS=...`。
2. 发布构建必须带 `-trimpath`。它把记录的文件路径替换为模块路径与版本或包导入路径，适用于堆栈等编译器记录的位置；不会清除业务字符串、资源内容、模块身份或全部文件名。
3. 默认启用 `-buildvcs=false`，控制自动嵌入的 VCS 信息；不会移除模块依赖信息，也不能代替路径裁剪。必要的公开版本字段通过既有受审查的注入方式保留。
4. 公开产物按项目调试策略使用 `-ldflags='-s -w'`。合并现有 `-ldflags`，不丢失 `-X` 版本字段及必要的外部链接设置；SDK 先确认链接符号与 ABI 要求。诊断符号受控保存，不随公开包分发；删除符号不能代替路径裁剪。
5. 审计实际生效的 GOFLAGS、CGO 和 target 参数；构建器清理环境时在其受控环境内注入，不能只依赖外部环境变量。不为隐私目的自动安装工具、部署、发布或更新旧产物资格。

以下仅展示独立可执行文件的参数组合；集成时合并原有 flags，入口、buildmode 和输出位置按项目替换，沿用已有目录：

```sh
go build -trimpath -buildvcs=false -ldflags='-s -w' -o ./dist/app ./cmd/app
```

检查实际二进制及 `go version -m ./dist/app` 暴露的模块、依赖和构建元数据；不能仅凭命令声明已启用参数。

## 编译器之外的泄露来源

- `-ldflags -X` 只注入明确允许公开的版本字段，不注入 `pwd`、用户名、主机名、构建环境全集或密钥。
- 检查 `//go:embed`、代码生成器、配置模板、日志中的硬编码路径以及 `runtime.Caller` / panic 输出。`-trimpath` 不会改写任意字符串或嵌入文件内容。
- CGO、汇编、外部链接器、原生库和预编译对象按共用约束单独处理；映射有效 CFLAGS、CXXFLAGS、CGO 参数及 target 变体，并保留 sysroot 和交叉编译器。不假定 Go 参数清理所有第三方内容，不直接禁用 CGO 破坏功能。

## 发布前验证

1. 对各发布 OS、架构和构建模式检查实际交付物，包括缓存复用产物及预编译依赖；新规则不能自动授予旧二进制、旧哈希或旧验收记录合格资格。
2. 将源码根、用户主目录、GOROOT、GOPATH / 模块缓存、临时目录和 CI 工作目录及其变体作为运行时扫描输入；执行共用约束中的流式、UTF-8 / UTF-16LE/BE、空格及跨块扫描。失败非零退出，仅输出固定分类，拒绝 qualification。
3. 在隔离环境验证 `runtime.Caller`、安全错误 / 堆栈路径及 CGO 的 `__FILE__`；静态 SDK 由真实调用方链接验证，动态 SDK 检查加载及必要 ABI 导出。修改 Mach-O 时执行共用签名状态分支。
4. 按实际改动覆盖参数合并、平台设置保留及扫描失败场景；已有 CI 固化构建和检查门禁，共享 helper 纳入构建输入固定和来源记录。
5. 交付说明覆盖的入口、工具链、已验证产物及未验证平台；区分配置测试、编译器 fixture、完整产品构建和平台验收，保留剩余风险，不公开原始敏感日志或私有收据。

## 官方依据

访问日期：2026-10-17。以项目实际 Go 工具链的 `go help build`、`go tool link -h` 为准；工具链不支持所需参数时明确说明限制，不静默省略。

- [Go build flags：trimpath、buildvcs、ldflags](https://pkg.go.dev/cmd/go#hdr-Compile_packages_and_dependencies)
- [Go linker：-s、-w、-X](https://pkg.go.dev/cmd/link)
- [Go version：构建信息检查](https://pkg.go.dev/cmd/go#hdr-Print_Go_version)
