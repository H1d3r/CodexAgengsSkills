---
name: frontend-design
description: Design or refine user-facing web layouts, visual hierarchy, responsive styling, themes, and accessible interactions when explicitly requested; not for pure TypeScript logic or routine nonvisual fixes.
---

# 现代个性化前端设计

## 使用边界

- 仅在页面布局、UI/UX、视觉风格、响应式、主题或交互设计任务中使用；纯 TS、API、状态逻辑、构建或性能修复不自动触发设计。
- 已有产品的设计系统、组件、品牌、文案与用户指定素材优先。局部维护不默认重设计，不强制装 UI 库、字体或图标包，不顺便改路由、数据协议或商业流程。
- 本 skill 与 assets 是可选指导和素材，不会自动接入项目；使用前说明作用域与映射，按授权修改。参考大厂原则，不复制其正文、商标、专有素材或可识别品牌外观。

## 设计流程

1. **内容先行**：确认受众、主要任务、真实内容与设备约束，列出关键 loading/empty/error/success/disabled 状态；没有证据时说明假设，不以虚构评价、Logo 或 KPI 填充版面。
2. **保留身份**：记录现有视觉事实与本次允许改动；绿地或明确要求个性化时才从 [有界风格配方](references/style-recipes.md) 选方向。差异化来自内容、字体层级、布局与节奏，不默认紫色渐变、玻璃卡片或全屏装饰。
3. **清晰层级**：每个任务区突出一个主动作，其余按语义降权；标题、正文、辅助信息有稳定层级。长文限制行宽，表格/仪表盘优先比较效率，不把所有内容拆成卡片。
4. **响应式**：按内容失效点调整布局，不按设备标签猜断点；窄屏重排并保留任务入口，不仅缩小字号。检查长文、国际化、200% 文本放大及 320 CSS px 回流，二维数据视图按必要例外处理。
5. **语义与可访问性**：颜色按文本/表面/边界/动作/状态职责命名，错误配文字或图标；普通文本对比至少 4.5:1，大字至少 3:1，必要控件边界及图形至少 3:1。使用原生语义、可见 focus、键盘路径、合适点击区域；sticky 区域不得遮挡焦点。
6. **主题与动效**：验证 light/dark 及系统高对比；动效只解释状态/空间变化，避免默认自动播放、视差与循环装饰。响应 reduced motion 时移除非必要位移动效，仍保留即时反馈。

## 可复用资源（按需读取）

- [设计系统与 token 契约](references/design-system.md)：官方来源、主题优先级、导入方式、对比度与验证门禁。
- `assets/design-tokens.json` 与 `assets/design-tokens.css`：原创中性示例，`fd` 命名空间、显式作用域；先映射到已有 tokens，必要时才使用原值。不是任何厂商 token 标准或认证。
- token 改动后运行 `python3 -B agent-skills/frontend-design/scripts/validate-tokens.py --self-test`；这是静态门禁，不代替浏览器验收。
- [风格配方](references/style-recipes.md)：可组合但有边界的编辑型、工具型、品牌表达、舒适阅读方向。

## 完成门禁

交付本次改动及选择理由；用真实内容检查窄/宽屏、键盘、focus、明暗主题、reduced motion 与高对比。复用现有测试并区分代码/静态检查和浏览器/读屏/真实设备验证；未测不声称合格。达到约定范围即停止。
