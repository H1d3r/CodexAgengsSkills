---
name: frontend-vue
description: Build or review Vue UI components, reactivity, accessibility, performance, and tests using the project's installed Vue version and TypeScript conventions.
---

# Vue 前端

## 边界与前置事实

- 适用于 Vue 页面、组件、交互、响应性和测试；纯 TypeScript 工具逻辑不因使用 TS 自动成为 Vue 或视觉设计任务。
- 先读 manifest、锁文件、Vue/编译器版本、构建与测试脚本，识别 Vue 2/3、Nuxt/SSR、路由、状态库与现有设计系统。不要用最新文档推断已安装能力。
- 新 Vue 3 代码优先 Composition API、SFC 与 `<script setup lang="ts">`，但服从现有项目约定；不为局部修复迁移 Options API、Vue 2 或升级依赖。
- 视觉个性化仅在用户要求时处理；优先复用项目组件、token 与 i18n，不强制引入 UI 库或重设计。

## 实施决策

1. **响应性**：明确状态所有者与更新路径；派生值用 `computed`，副作用才用 watcher。避免解构 `reactive` 的基本类型属性丢失响应性；`ref` 的 `.value` 与模板自动解包按实际位置区分。
2. **组件契约**：用项目现有 TS 风格定义 props/emits；props 单向流动，不借由子组件变更嵌套 props 偷改父状态。表单模型与事件协议沿用现有约定。
3. **异步生命周期**：处理 loading、empty、error、success，防止旧请求覆盖新结果；watcher/effect 注册清理，卸载时释放订阅、计时器和请求。SSR 中不要在模块级共享用户状态或无保护地访问浏览器 API。
4. **可访问性**：先用原生语义控件、关联 label、键盘操作和可见 focus；路由/弹窗变化要管理焦点并保留可退出路径。错误不能只靠颜色；有意义的图片与图标提供文本替代。
5. **性能**：先区分首屏加载与更新性能，测量实际瓶颈；优先压缩关键依赖、拆分路由、稳定 props，长列表按需要虚拟化。浅响应、`v-memo`、`v-once` 仅在数据语义与测量支持时采用。
6. **类型与测试**：Vite 转译不等于类型检查；使用项目已有 `vue-tsc`/Nuxt 类型检查命令。测试面向用户行为和公开契约，不锁定组件内部实现；覆盖异步竞争、错误恢复和关键键盘流程。

## 按需参考

- 涉及 API 小版本、响应性、SSR、性能或测试选择时读取 [Vue 实践与官方来源](references/vue-practices.md)。
- 不把 React hooks/RSC、Next.js 缓存规则照搬到 Vue；跨框架原则仍需对照 Vue/Nuxt 的实际运行模型。

## 完成门禁

运行项目已有的最小相关 typecheck、组件测试与 build；视觉或交互改动检查窄屏、键盘、浅深主题与 reduced motion。报告命令、结果和无法验证的浏览器/真实设备门禁；没有运行就不声称通过。
