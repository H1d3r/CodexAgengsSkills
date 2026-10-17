---
name: cpp
description: Implement and review C++ code using project-selected standards, RAII ownership, lifetime safety, and focused compiler, CMake, and test checks.
---

# C++

## 适用边界

- C++ 源码、公共头文件、原生库，以及明确服务于 C++ 的 CMake/Clang 构建与诊断任务。
- 不把纯 C、C#、仅调用原生库的其他语言任务或孤立的 CMake 文件当成 C++ 任务。

## 先确认工程事实

- 读取相邻构建配置、preset/toolchain、CI 与测试目标，确认 C++ 标准、编译器/标准库版本、平台、依赖和 ABI 边界。
- 项目版本优先；不因在线文档使用新标准，就升级标准、工具链或依赖。`span`、`jthread` 等先检查标准和库支持；尊重既有异常/RTTI 策略。
- 使用已有构建方式；CMake 项目优先 target 级依赖和编译特性，不顺手全局改 flags、重写构建系统或格式化全库。

## 发布构建与路径隐私

- 仅在配置可分发构建、原生 SDK 打包或排查路径泄露时，读取并执行[构建路径隐私共用约束](../security/references/build-path-privacy.md)；普通业务代码修改不默认触发。
- 按实际编译器能力映射路径：GCC/Clang 可使用 `-ffile-prefix-map`，MSVC 使用适配其版本的映射选项；覆盖有效 CFLAGS、CXXFLAGS、CGO 及 target 变体。经 cc-rs 使用 shell 转义参数时启用对应解析，不假定所有 native 构建器读取相同变量。
- 扩展既有构建入口并保留 sysroot、目标编译器、优化、平台链接参数和 ABI 导出。SDK 仅按需剥离调试信息，验证静态库真实链接、动态库加载和必要符号，不以符号全删代替路径映射。
- qualification 前以支持空格、UTF-8、UTF-16LE/BE 和跨块匹配的流式扫描检查实际产物；失败返回非零状态且不打印敏感原值。遵循共用约束中的预编译库、Mach-O 签名状态分支和旧产物重新验收规则。

## 所有权与生命周期

- 用 RAII 封装内存、文件、锁等资源及失败路径；优先值语义、容器和 `unique_ptr`，仅真实共享所有权才用 `shared_ptr`，检查引用环。
- 裸指针/引用通常表达借用；对历史或外部 API 先确认所有权契约，再决定包装，不机械替换全部指针。
- `string_view`、迭代器、指针和 `span` 不拥有数据；检查临时对象、容器失效和跨异步/线程使用，禁止返回局部对象的引用或借用视图。
- 资源类型优先 Rule of Zero；确需自定义特殊成员时一并检查复制、移动、析构及异常保证。移动后不假定原值仍在，`noexcept` 必须符合实际实现。
- 锁采用作用域管理；持锁期间避免调用未知代码。共享所有权不等于线程安全，先确认取消、析构与线程结束顺序。

## 最小验证

1. 按仓库命令编译受影响 target，并执行相关测试；公共头文件或 ABI 变更覆盖实际调用方。
2. 已有 `clang-tidy` 时使用当前工具链生成的 compilation database，只检查受影响文件；不拿错误 include/define/标准的裸命令替代工程配置。
3. 生命周期/越界问题按支持情况启用 ASan，未定义行为用 UBSan；数据竞争另用 TSan。工具需编译及链接支持，不默认安装、启用或改变发布配置。
4. 新增行为或修复至少验证成功、失败及释放路径；明确记录未跑的平台、工具和测试，不把编译通过等同运行安全。

仅当任务涉及相应细节时读取 [官方依据与工具用法](references/sources.md)。创建文件时加载 `project-structure`；通用测试设计按需加载 `testing`，不默认叠加其他语言 skill。
