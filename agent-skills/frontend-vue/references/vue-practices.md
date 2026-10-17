# Vue 实践与版本门禁

以下是官方资料的原创归纳，不是固定架构模板。访问日期均为 **2026-09-30**，通过网络 CLI 实际读取官方 HTML 与 Vercel 官方仓库原始 Markdown（HTTP 200）；web 工具未返回可读正文，不作为证据。后续使用时先核对项目版本与最新文档。

## 响应性与异步

- Vue 3 的 `reactive` 对象保持引用；解构其基本类型属性会失去关联，必要时用 getter、`toRef`/`toRefs`，不要给所有状态机械套同一方案。
- **Vue 3.5+** 的同一 `<script setup>` 内 `defineProps` 解构访问有编译器响应性支持；3.4 及以下不能假定此行为。把解构 props 传给 watcher/composable 时仍需 getter（如 `watch(() => foo, ...)`），传入值不是响应性来源。
- `defineModel` 要核对 **3.4+** 能力与已有 v-model 协议；子组件默认值可能造成父子初始状态不同步，不隐式改变表单契约。
- **3.5+** 的 `onWatcherCleanup` 必须在同步执行阶段调用，不能放在 `await` 后。旧版本可用 watcher 回调提供的 `onCleanup`；尽早注册清理，必要时同时用 AbortController 与请求序号防陈旧响应。`watchEffect` 仅追踪第一次 `await` 前同步读取的依赖。
- 同步在 setup 中创建的 watcher 随组件卸载停止；异步回调中创建的 watcher 要保留停止句柄。用 `flush: 'post'` 的理由应是读取更新后的 DOM，而不是默认设置。
- SSR 的状态按请求隔离；浏览器访问放入客户端生命周期或适当保护，初始服务端/客户端输出保持一致。不要把服务端密钥序列化进客户端状态。

## 性能顺序

| 问题 | 优先动作 | 避免 |
|---|---|---|
| 首屏依赖过大 | 测 bundle、选择已有架构允许的按需导入/路由拆分 | 未测量就添加库或重写 SSR |
| 独立请求串行 | 在现有数据层并发无依赖请求 | 对有因果依赖或权限顺序的请求盲目并行 |
| 更新昂贵 | 稳定子组件 props、分析更新范围 | 所有组件都加 memo |
| 大量列表 DOM | 保留稳定业务 key；评估虚拟列表的焦点与读屏策略 | index key 掩盖数据身份变化 |
| 大型不可变数据 | 证明瓶颈后评估 `shallowRef` 并整体替换根值 | 浅响应后仍期望深层变更自动触发 |

## 验证选择

- 优先已有测试栈；Vite 项目可评估 Vitest，组件可用 Vue Test Utils，E2E 沿用现有浏览器工具，不为 skill 强制安装任何一个。
- 用 DOM 行为验证 props/emits、表单校验、loading/error/empty、请求乱序与卸载清理；异步渲染按工具等待 Vue 更新及 Promise 完成。
- 至少人工检查受影响页面的标题层级、label、tab 顺序、skip link（适用时）、路由后的焦点和错误提示。自动可访问性扫描不能证明所有体验合格。

## 官方来源与用途

| 官方 URL | 用途 |
|---|---|
| https://vuejs.org/guide/typescript/overview.html | Vite 转译与 vue-tsc 类型检查的区别 |
| https://vuejs.org/guide/typescript/composition-api.html | Composition API 的 props/emits/ref 类型与类型检查 |
| https://vuejs.org/api/sfc-script-setup.html | props 解构、defineModel 和编译器小版本门禁 |
| https://vuejs.org/guide/essentials/reactivity-fundamentals.html | ref/reactive 与解构限制 |
| https://vuejs.org/guide/essentials/watchers.html | 清理、异步依赖追踪与 watcher 生命周期 |
| https://vuejs.org/guide/best-practices/accessibility.html | 语义、表单、skip link 与焦点 |
| https://vuejs.org/guide/best-practices/performance.html | 加载/更新、props 稳定、浅响应与虚拟化 |
| https://vuejs.org/guide/scaling-up/testing.html | 行为导向与测试层次 |
| https://vuejs.org/guide/scaling-up/ssr.html | SSR 环境与跨请求状态污染 |
| https://raw.githubusercontent.com/vercel-labs/agent-skills/main/README.md | 借鉴性能风险分级与可复用 skill 组织；React/Next 专属规则不移植 |
