# 设计系统与 token 契约

## 官方研究边界

访问日期均为 **2026-09-30**。实际读取方式：网络 CLI（HTTP 200 HTML/Markdown；Spectrum 使用同一官方 HTML 内嵌的页面数据）。web 工具未返回可读正文，不作为证据。以下为原创归纳和工程选择，只借鉴原则，不复制品牌资产或第三方正文；外部 guideline 更新后需重核。大厂公开实践不等于项目必须采用其组件库。

| Primary source URL | 借鉴范围与不采用的部分 |
|---|---|
| https://raw.githubusercontent.com/vercel-labs/agent-skills/main/README.md | 借鉴精简入口、按需规则、性能风险排序和 UI review；React/Next 专属实现不泛化到 Vue |
| https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/web-design-guidelines/SKILL.md | 借鉴可验证 UI 审查形式；这里不自动执行第三方脚本或假定工具已安装 |
| https://vercel.com/design/guidelines | 借鉴键盘、focus、表单反馈、布局与动效；不照搬品牌口吻及品牌专属样式，对比度以 WCAG 任务基线为准 |
| https://fluent2.microsoft.design/design-tokens | 借鉴全局/语义 token 层次与主题替换，不复制 Microsoft token 值 |
| https://fluent2.microsoft.design/color | 借鉴中性、品牌与状态色角色，现有品牌事实优先 |
| https://spectrum.adobe.com/page/design-tokens/ | 借鉴 token 的职责和消费方式，示例不是 Spectrum schema |
| https://spectrum.adobe.com/page/color-system/ | 借鉴主题下的色彩层级与适应性，不复制 Adobe 配色 |
| https://developer.android.com/design/ui/mobile/guides/styles/color | Google 官方 Material 3 颜色角色，用作概念参考，不强制 Material 外观或把 Android 单位/API 当 Web 实现 |
| https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | 文本对比度的最低要求与例外 |
| https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | 必要界面信息的非文本对比度 |
| https://www.w3.org/WAI/WCAG22/Understanding/reflow.html | 窄视口/缩放回流与二维内容例外 |
| https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion | 降低非必要动效的 CSS 偏好检测 |
| https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors | 系统色、高对比与 box-shadow 等限制 |

Material 3 网站 URL `https://m3.material.io/styles/color/roles` 本次仅返回客户端外壳，没有可读角色正文，未作为结论依据；采用上表 Google Android 官方指南的实际正文。

## 原创资源契约

- `assets/design-tokens.json` 是此 bundle 的数据事实源，`schemaVersion: 1` 是自定义格式，不声称 DTCG/Fluent/Spectrum 兼容。`common` 保存排版/间距/尺寸/动效；`themes.light/dark` 保存语义颜色与主题阴影；`preferences` 保存偏好覆盖。
- 每个叶值均为 CSS 字符串，JSON 键 `color-text` 对应 CSS 变量 `--fd-color-text`（前缀来自 `prefix`）。无隐藏引用、构建插件或远程依赖。
- CSS 是配套的静态展开结果；修改 JSON 后同步 CSS，验证所有分支和值，而不只比较默认主题。不要把 CSS 当自动连接到应用的管线。
- `color-text`/`color-muted` 用于 bg、surface、surface-raised；accent/accent-hover 配 on-accent；success/warning/danger/info 各配同名 `*-bg`。不要任意交叉配对或依赖透明叠层后仍有相同对比度。
- `control-target` 是示例目标尺寸，不等于所有项目或 WCAG 对控件的统一强制尺寸。`text-title` 的 clamp、阴影和圆角也都是可替换起点。

## 显式使用与优先级

仅当项目允许采用示例时才导入 CSS，在应用拥有的区域显式加属性，例如：

```html
<section data-fd-theme="auto">
  <button class="primary-action">保存</button>
</section>
```

```css
.primary-action {
  color: var(--fd-color-on-accent);
  background: var(--fd-color-accent);
  min-block-size: var(--fd-control-target);
  border-radius: var(--fd-radius-control);
}
```

- 无 `data-fd-theme` 的区域不被示例 CSS 选择；变量和主题不会全局接管 `:root`，不附带 reset、布局或组件库。导入位置沿用项目现有策略。
- `light`/`dark` 为显式偏好；`auto` 响应 `prefers-color-scheme`。不识别的属性值暂按浅色兜底，不是主题校验器。应用自己保存主题偏好并处理 SSR 初始值，避免 hydration 不一致与闪烁。
- 顺序：common + light → 显式 dark 或 auto 的系统 dark → 对比偏好 → reduced-motion → forced-colors（系统色最终优先）。避免主题作用域嵌套；确需嵌套时核对后代继承与 focus。
- `prefers-contrast: more` 增强文本/边界/focus；不假定所有浏览器都支持。`forced-colors: active` 用 Canvas/CanvasText/LinkText/Highlight 等系统色并去除示例阴影，不设置 `forced-color-adjust: none` 来对抗用户偏好。
- scoped `:focus-visible` 使用 outline 而不只靠阴影。配色只是默认组合，透明叠层、照片背景、sticky 遮挡仍需实际检查；不要去掉原生 focus 后无替代。
- reduced-motion 覆盖 duration 与位移 tokens；**不会消除消费方任意硬编码的 animation、transform 或 smooth scrolling**，这些需在组件自身的 media 分支处理。即刻更新仍保留语义反馈。

## 验证门禁

1. JSON 可解析，common/每个主题/偏好叶值与 CSS 对应规则完全一致；所有使用的 `--fd-*` 变量已声明。
2. 用 WCAG sRGB 相对亮度公式核对实际搭配：普通文本与状态正文 ≥4.5:1，必要控件边界与 focus 对相邻示例表面 ≥3:1。系统色值由 OS 决定，不用静态 hex 检查宣称 forced-colors 合格。
3. 浏览器核对显式主题覆盖系统主题、auto 两分支、more-contrast 与 forced-colors、reduced-motion；再检查键盘/焦点、200% 文本放大、320 CSS px 回流、长内容及国际化。静态 token 检查不等于浏览器、读屏或真实设备验收。

可重复静态自查（标准库、只读、无需安装依赖），从项目根运行：

```sh
python3 -B agent-skills/frontend-design/scripts/validate-tokens.py --self-test
```

检查器只解析本素材约定的 CSS 子集，并枚举主题/偏好覆盖；不是通用 CSS 验证器或浏览器。负向测试在内存中破坏 CSS 同步及颜色对比，确认门禁会拒绝。
