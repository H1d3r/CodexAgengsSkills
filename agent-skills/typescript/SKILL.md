---
name: typescript
description: Implement and review TypeScript code with project-version-aware configuration, gradual strictness, safe narrowing, and runtime validation at data boundaries.
---

# TypeScript

## 适用边界

- TypeScript 源码/声明、`tsconfig`、类型设计、JS→TS 渐进迁移和明确的 TS 类型诊断。
- 不因项目有 `package.json`、任务出现裸 `ts` 或存在 TS 依赖，就要求纯 JS 任务迁移语言；通用 JS/Node 行为按需使用 `javascript-typescript`。

## 先确认工程事实

- 读取所属 package 的 manifest、lockfile、继承后的 `tsconfig`、CI 与现有脚本；确认仓库 TypeScript 版本、运行时、模块解析及打包方式。
- 不按在线最新文档升级编译器或套用通用 `tsconfig`；`module`/`moduleResolution` 必须匹配实际宿主，保留项目的 ESM/CJS、emit 与 project references 约定。
- 用仓库已安装的工具和包管理器执行检查；不调用会临时下载未知版本的命令，不新增验证依赖。

## 类型安全与迁移

- 新 TS 项目在宿主兼容前提下以 `strict` 为起点；旧项目先记录诊断基线，在批准的模块/配置边界逐步迁移，不为了小改动全仓开 strict 或大量加 suppressions。
- `strict` 是一组随编译器版本演进的检查；`noUncheckedIndexedAccess`、`exactOptionalPropertyTypes` 等需单独评估，不能声称 strict 已覆盖它们。
- 外部 JSON、用户输入、存储和消息先视为 `unknown`，用运行时检查或现有 schema 工具验证后进入领域层；校验失败应显式返回/抛出错误。
- 不用 `any`、`as T`、`!` 或双重断言伪造安全；断言不校验数据。有外部库兼容等真实需要时，将例外局限在适配边界并说明证据与测试。
- 优先控制流收窄、判别联合和可验证的 type guard；guard 实现必须真检查结构。使用返回 `any` 的库（如 JSON.parse）时在入口隔离为 `unknown`。
- 内部实现允许可靠推断；公共 API/声明明确稳定契约。支持的编译器版本下可用 `satisfies` 检查约束并保留更具体的类型，不把它当运行时验证。
- JS 迁移按文件推进，按需使用 `allowJs`/JSDoc/`checkJs`；先处理边界和不安全类型，再考虑收紧配置，保留构建输出与调用方兼容性。

## 最小验证

1. 按所属 package 的既有 typecheck/test/build 脚本运行，覆盖继承配置、project references 或框架生成类型；不要用 `tsc file.ts` 冒充项目检查。
2. 只有工程本就支持独立 no-emit 检查时才使用对应本地编译器；emit、声明和引用工程沿用原脚本，不机械附加 `--noEmit`。
3. 类型检查不能代替运行时测试；边界变更验证有效、缺字段、错误类型以及可空/额外字段的既定策略，避免断言掩盖失败。
4. 记录本次新增诊断与旧基线、已验证脚本及未验证门禁；不以 `skipLibCheck`、`@ts-ignore` 等静默消除未知问题。

遇到配置选择、迁移或边界校验细节时读取 [官方依据与迁移检查](references/sources.md)。创建文件时加载 `project-structure`；测试设计按需加载 `testing`，不默认叠加前端框架 skill。
