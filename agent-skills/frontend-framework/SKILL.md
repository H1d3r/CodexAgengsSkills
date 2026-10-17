---
name: frontend-framework
description: Build or review frontend framework components, state, routing, accessibility, and performance.
---

# Frontend Framework Skill（for Agents）

## 适用场景
- React / Vue / Svelte / Angular 组件与页面改造
- 前端状态管理、路由、构建优化、性能体验、无障碍相关任务

## 核心原则

1. **以用户体验为约束**：功能正确 + 可访问性 + 性能预算。
2. **最小改动**：优先修复现有组件行为，不重构状态架构。
3. **可维护优先**：UI 逻辑与业务逻辑分离，避免单文件内职责膨胀。

## 强制执行清单

- 页面/组件边界清晰：一个组件只承载单一职责。
- 网络请求与状态读取统一封装（Hooks/Store/服务层），避免散落。
- 输入表单增加校验、错误边界与空状态处理。
- 关键交互按现有监控方案验证错误与耗时；无实际需要不新增日志，不记录输入内容、Token 或个人数据。
- 静态资源与依赖版本按项目 lockfile 管理。

## 常见实践

- React：先定位渲染或请求瓶颈；仅在项目编译器与测量证据需要时使用 `useMemo` / `useCallback`，避免过早优化。
- Vue：组合式 API 的响应式依赖明确，watch 监听有清晰退出条件。
- Svelte/Angular：组件生命周期与外部副作用有明确清理。
- 路由与权限保持集中配置，不在页面散落判断。

## 常用质量门禁

- `npm/pnpm/yarn lint`
- `npm/pnpm/yarn test`
- `npm/pnpm/yarn build`
- Lint/类型检查通过（如 `eslint`, `stylelint`, `vitest`, `tsc`）

## 反模式（避免）

- 在 UI 中拼接鉴权和业务规则，导致重复难测。
- 绕过框架或既有表单库的数据流直接修改 DOM；受控与非受控模式依项目表单策略选择。
- 全局状态作为“万能盒子”，缺乏数据流边界。
- 忽略 key、列表 diff 与渲染性能问题。
- 大量 `any` 绕过类型，导致接口变更无人感知。

## 与仓库冲突时的优先级

- 以前端框架版本、构建脚本、eslint/prettier 配置及 CI 为准。
- 与本文件冲突时按实际项目约束执行，并记录差异原因。

## 国际化边界

- 产品已启用 i18n 时，新增用户文案进入既有翻译资源，不在组件内硬编码多套语言。
- API 语言头沿用项目统一客户端；不要由单个页面自行拼接。

## 按需专项

- Vue 任务由路由加载 `frontend-vue`；不要仅因前端项目安装了依赖就读取所有框架规则。
- 明确涉及视觉层级、布局、样式或 UI/UX 时触发 `ui-design` / `ui-review` 并加载 `frontend-design`；仅修复业务逻辑、类型或构建不改变视觉设计。
