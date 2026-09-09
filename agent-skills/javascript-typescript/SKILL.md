---
name: javascript-typescript
description: Apply project-aware JavaScript and TypeScript conventions for applications, libraries, and services.
---

# JavaScript / TypeScript Skill（for Agents）

## 适用场景
- Node.js 后端、前端应用（React/Vue/Svelte）、工具链脚本、自动化流程
- 需要在前后端边界处理类型、构建和发布的任务

## 核心原则

1. **类型先行**：优先 TypeScript；若是 JavaScript，新增类型注释与边界测试。
2. **最小修改**：避免大面积重构，优先修复问题处。
3. **可运行优先**：保证 lint + test + build 能在仓库指定方式通过。

## 强制执行清单

- 所有公共导出函数/组件 props 具备明确类型。
- 异步逻辑显式处理失败分支，避免无意义的 `catch` 空处理。
- 对外请求统一封装错误上下文：请求参数、状态码、耗时、trace id。
- 依赖版本和构建脚本以项目 lockfile 为准（`package-lock.json`/`pnpm-lock.yaml`/`yarn.lock`）。

## 推荐实践

- React/Vue 组件：单一职责、props 约束、hooks/组合逻辑最小化。
- Node：优先使用 structured logging，避免 `console.log` 污染生产日志。
- API 层：统一封装，避免重复拼接 URL、重复错误解析。

## 常用质量门禁

- `prettier --check .`
- `eslint .` / `eslint . --max-warnings=0`
- `tsc --noEmit`（或对应项目命令）
- `pnpm test` / `npm test` / `yarn test`（按仓库标准）

## 反模式（避免）

- 直接在页面层写大量业务拼接逻辑而不做提取。
- `any` 大面积泛滥，导致边界类型失效。
- `new Promise` 包装原有 Promise，导致异常链丢失。
- 忽略 bundle/编译警告直接提交。

## 与仓库冲突时的优先级

- 以项目构建配置（tsconfig/eslint/prettier）与 CI 脚本为准。
- 若与本文件冲突，明确记录“工程事实驱动”的处理方式。
