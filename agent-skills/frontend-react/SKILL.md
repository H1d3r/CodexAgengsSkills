---
name: frontend-react
description: Build or review React and TypeScript UI behavior, state, accessibility, performance, and tests.
---

# Frontend (React/TS) Skill（for Agents）

## 适用场景
- React + TypeScript 前端任务：组件、页面、数据抓取、状态管理、路由、性能优化
- 与 UI 交互、重构及可访问性改造相关

## 核心原则

1. **先判断复杂度**：若影响首屏/交互性能，先做范围与性能风险评估。
2. **组件分治**：单文件只承担单一职责，特性按 feature 切分。
3. **数据边界清晰**：API 不在组件内内联调用，提到 API 层。

## 强制执行清单

- 组件 props/type 定义明确（`interface` + 默认导出/命名导出约定一致）。
- 禁止在组件中散落大量业务逻辑；优先提取 hook/helper。
- 关键加载/错误状态由统一机制处理，不用随意 `return` 自定义 loading。
- 列表项渲染加 key，异步 effect 有取消/cleanup。
- `useCallback/useMemo` 只在真实性能压力点使用，避免过度优化。
- 表单校验与请求状态集中管理，避免重复。

## 推荐实践

- 新特性目录建议：`feature/{feature-name}/{api,components,hooks,types}`。
- 数据查询优先以 query 框架统一缓存策略。
- 样式策略：小组件内联样式；大组件样式分离。
- 发生路由变更时同步更新菜单/面包屑/鉴权。
- 主题与文案支持本地化（i18n）

## 性能优先级（按实际证据采用）

- 先排查无依赖请求的串行 waterfall 和关键 bundle，再处理局部重渲染；有依赖/鉴权顺序的请求不能盲目并发。
- 复用项目已有路由/框架的数据加载与缓存机制；不因性能建议强制安装 query 框架或把普通 React 项目改造成 Next.js。
- 官方依据（访问日期 2026-09-30）：[Vercel React Best Practices](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/react-best-practices/SKILL.md)、[React Effect 数据抓取限制](https://react.dev/reference/react/useEffect#fetching-data-with-effects)。仅借鉴已适用原则，不复制框架专属规则。

## 常用质量门禁

- `lint` / `typecheck` / `build`
- 组件测试 + API 交互测试（如项目规范）
- 性能门禁：首屏、重渲染、打包体积（按项目阈值）

## 反模式（避免）

- 在组件直接发起裸 fetch，并无统一 loading/error 约束。
- 组件负责三层职责（展示+数据层+路由跳转+错误处理）。
- 相同转换逻辑在多个页面 copy-paste。
- 列表/表格未处理空状态、异常状态。

## 与其他技能冲突时

- 与现有项目脚手架/路由方案（Next/Remix/Vue 等）和 lint 规则为准。
- 与本文件冲突时，按项目真实依赖树和历史风格执行。
