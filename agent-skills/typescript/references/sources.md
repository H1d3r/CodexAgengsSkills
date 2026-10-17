# TypeScript 官方依据与按需检查

访问日期：**2026-09-30**。仅使用 TypeScript 官方文档归纳实践，不复制第三方 skill。先核对 lockfile 中的编译器版本；文档中的新语法/配置不得直接变成项目升级要求。

## 配置与渐进迁移

- JS→TS 官方迁移指南：https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html
  - `allowJs` 可让 JS/TS 共存；JSDoc 与 `checkJs` 可按工程现状辅助迁移。改语言、诊断门禁与运行输出是不同变更，不一次性全做。
  - 推荐次序不是固定开关清单：先确认现有编译输出/错误基线，再选包或文件边界补类型、处理入口数据，最后在批准的配置边界收紧检查。
- strict：https://www.typescriptlang.org/tsconfig/strict.html
  - strict 开启一组检查，未来编译器可能扩展该组；升级时比较新增诊断。共享配置不适合本次变更时，先局部强化类型，不暗中修改全局门禁。
- 索引访问：https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html
  - 对缺少确定声明的索引访问加入 `undefined`；采用前检查真实容器/索引行为，不靠 `!` 抹掉不确定性。
- 可选属性：https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html
  - 区分属性不存在与显式赋 `undefined`，迁移时检查对象构造、序列化及调用方语义。
- 完整编译选项：https://www.typescriptlang.org/tsconfig/
  - 上述两项不属于 strict 的自动开关集合；`skipLibCheck` 跳过声明检查，不是修复重复/不兼容依赖类型的方法。
- 宿主与模块选项：https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html
  - Node、bundler、直接执行等宿主存在不同解析和 emit 约定；不要为“现代化”统一套 `bundler` 或改 ESM/CJS。
- tsc CLI：https://www.typescriptlang.org/docs/handbook/compiler-options.html
  - 命令行直接指定输入文件会忽略 `tsconfig.json`。优先工程脚本，独立检查才按现有配置使用本地编译器的 `-p`；引用工程继续用原有 `-b`/框架流程。

## 收窄与运行时边界

- Narrowing：https://www.typescriptlang.org/docs/handbook/2/narrowing.html
  - 使用 `typeof`、非空检查、属性检查及判别联合缩小 `unknown`；注意 `typeof null === "object"`，数组、可选字段等也需按契约确认。
  - 自定义 type predicate 的正确性由实现承担；写成 `value is T` 不代表编译器验证过其业务结构。
- 类型断言：https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions
  - 类型断言编译后被移除，不会检查 JSON、捕获异常或确保值非空；泛型参数/接口声明同样不能替代 runtime validation。
- `satisfies`（TS 4.9 起）：https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html
  - 静态检查表达式与类型的兼容性，同时保留更具体类型。仍需考虑上下文类型，不声称类型永远完全不受影响。

按需边界检查表（使用已有 validator 或小型手写 guard，不新装 schema 库）：

| 输入 | 至少确认 | 验证证据 |
|---|---|---|
| JSON/API/消息 | 非空对象/数组形状、字段类型、必要范围与判别值 | 有效、畸形、缺字段、错误类型样例 |
| 可选/可空字段 | 缺失、null、undefined 各自契约 | 序列化/反序列化及调用方测试 |
| 额外字段 | 保留、剥离或拒绝沿用既定策略 | 策略回归测试，而非默认拒绝全部 |
| 依赖返回 any | 入口先收为 unknown，验证后传给领域层 | 失败分支不会继续处理不合法值 |

静态类型安全不自动保证业务范围、权限或第三方协议正确；验证范围限于本次实际契约，不借机重建整套 API 层。
