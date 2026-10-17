---
name: javascript-typescript
description: Apply project-aware JavaScript and TypeScript conventions for applications, libraries, and services.
---

# JavaScript / TypeScript Skill（for Agents）

## 适用场景
- Node.js 后端、前端应用（React/Vue/Svelte）、工具链脚本、自动化流程
- 需要在前后端边界处理类型、构建和发布的任务

## 核心原则

1. **项目语言优先**：保留既有 JS/TS 选择；纯 JavaScript 按需用 JSDoc 与边界测试，不默认迁移 TypeScript。
2. **最小修改**：避免大面积重构，优先修复问题处。
3. **可运行优先**：保证 lint + test + build 能在仓库指定方式通过。

## 强制执行清单

- 公共导出/组件 props 保持明确且稳定的契约；JS 可用 JSDoc，TS 内部实现允许可靠推断。
- 异步逻辑显式处理失败分支，避免无意义的 `catch` 空处理。
- 对外请求保留必要错误上下文（状态码、耗时、trace id）；参数按项目策略脱敏，不记录密钥或完整敏感请求。
- 依赖版本和构建脚本以项目 lockfile 为准（`package-lock.json`/`pnpm-lock.yaml`/`yarn.lock`）。

## 推荐实践

- React/Vue 组件：单一职责、props 约束、hooks/组合逻辑最小化。
- Node：优先使用 structured logging，避免 `console.log` 污染生产日志。
- API 层：统一封装，避免重复拼接 URL、重复错误解析。

## 常用质量门禁

优先所属 package 的已有脚本与本地版本；以下仅在项目已采用对应工具/模式时使用，不下载依赖或全仓机械执行。

- `prettier --check .`
- `eslint .` / `eslint . --max-warnings=0`
- `tsc --noEmit`（或对应项目命令）
- `pnpm test` / `npm test` / `yarn test`（按仓库标准）

## 反模式（避免）

- 直接在页面层写大量业务拼接逻辑而不做提取。
- `any` 大面积泛滥，导致边界类型失效。
- `new Promise` 包装原有 Promise，导致异常链丢失。
- 忽略 bundle/编译警告直接提交。

## Skill 协作

- 本入口处理 JS/TS 共有的异步、运行时和工具链约定；TS strict、类型收窄、声明与迁移任务使用独立 `typescript` skill，不在此重复细则。
- 创建文件时加载 `project-structure`；不因 package.json 自动加载特定前端框架。

## 与仓库冲突时的优先级

- 以项目构建配置（tsconfig/eslint/prettier）与 CI 脚本为准。
- 若与本文件冲突，明确记录“工程事实驱动”的处理方式。
