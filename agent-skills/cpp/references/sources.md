# C++ 官方依据与按需工具说明

访问日期：**2026-09-30**。下列资料是官方/项目维护者的一手来源；规则为本仓库原创归纳，不复制第三方 skill。在线最新文档不是项目升级依据，使用命令前核对本地版本与 CI。

## 所有权、借用与并发

- C++ Core Guidelines：https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines
  - R.1：资源由作用域对象管理；R.3：裸指针通常非 owning；R.20/R.21：智能指针表达所有权，非共享场景优先唯一所有权。
  - F.43：不返回局部对象的指针/引用；C.20：能避免自定义特殊成员就避免；CP.20/CP.22：RAII 管锁，持锁时不调用未知代码。
  - 工程应用：先画清 owner、borrower 和销毁顺序，再检查异常/早退、容器重分配、异步回调捕获等失效路径。
  - Core Guidelines 是设计指导，不授权打破既有 ABI、关闭异常策略或全量改写历史代码。

## CMake：按项目版本选工具

- 编译特性与标准要求：https://cmake.org/cmake/help/latest/manual/cmake-compile-features.7.html
  - 用 `target_compile_features` 表达最低标准；公共头文件有相应要求才向调用方传播，否则保持 PRIVATE。最低标准不是精确锁定标准，也不自动保证所有标准库设施可用。
- Presets：https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html
  - 优先复用已有 configure/build/test preset；核对本地 CMake 支持的 preset schema、generator 和 toolchain，不自动迁移。
- Compilation database：https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html
  - `CMAKE_EXPORT_COMPILE_COMMANDS` 主要适用于 Makefile/Ninja generators；不能假设任意 generator 均输出数据库，官方也提示 UNITY_BUILD 组合限制。
- CTest：https://cmake.org/cmake/help/latest/manual/ctest.1.html
  - 用 `-R` 选择相关测试、`--output-on-failure` 留失败证据。确认确有匹配测试，零测试不算通过；本地版本支持时可用 `--no-tests=error`。

已有 preset 时，替换下列名称后运行；不存在 preset 时用仓库文档中的构建方式，不为示例新增配置：

```sh
cmake --preset <configure-preset>
cmake --build --preset <build-preset>
ctest --preset <test-preset> --output-on-failure -R '<affected-test-pattern>'
```

先构建被选测试依赖的目标。无 preset 时可以按已有 build tree 使用 `cmake --build <build-dir> --target <target>` 与 `ctest --test-dir <build-dir>`；多配置 generator 要匹配仓库的配置参数。

## Clang：带真实编译上下文的检查

- clang-tidy：https://clang.llvm.org/extra/clang-tidy/
  - compilation database 提供 include、define、标准等上下文；使用仓库 `.clang-tidy` 与匹配版本，不直接启用全部 checks 或自动修复全库。
  - 已有数据库时：`clang-tidy -p <build-dir> <changed-source.cpp>`。生成工具或数据库缺失时报告门禁，而非安装新依赖。
- ASan：https://clang.llvm.org/docs/AddressSanitizer.html
  - 适合越界、use-after-free 等；典型参数 `-fsanitize=address`，诊断构建可配 `-g -fno-omit-frame-pointer`。编译和最终链接都需 sanitizer 支持。
- UBSan：https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
  - `-fsanitize=undefined` 检查部分未定义行为；它不覆盖所有 UB，不代替测试与生命周期分析。
- TSan：https://clang.llvm.org/docs/ThreadSanitizer.html
  - `-fsanitize=thread` 用于数据竞争诊断，核对目标平台与运行成本；不要与 ASan 放进同一诊断构建。

工具的检查范围、库与平台覆盖有限；只有实际执行过的目标、测试及诊断运行才能作为验证证据。
