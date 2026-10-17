---
name: agent-runtime-compat
description: Adapt AGENTS.md and skill behavior across Codex, Cursor, Pi, GPT-6 Astra, and unknown future agent runtimes by detecting capabilities instead of guessing from model names.
---

# Agent Runtime Compatibility

## 适用场景

- 创建或维护 `AGENTS.md`、Agent Skills、Cursor rules、Pi 配置或模型兼容规则。
- 任务涉及 Codex、Cursor、Pi、GPT-6 Astra、工具能力、规划模式或子代理调度。

## 能力优先

执行前确认：

- 当前是只读规划还是允许修改。
- 可用的文件、终端、网络、浏览器、审批和外部系统工具。
- 是否支持子代理、异步工具调用、中途引导和长期任务续跑。
- 哪些动作仍需用户授权。

不得仅凭型号名称推断权限或工具；未知模型进入保守能力 profile。

## 指令与执行

- 系统/开发者/用户指令优先于 skill 建议；最近且更具体的项目规则优先。
- 复杂任务先检查可访问的指令和 skill 是否冲突，避免重复规则造成行为漂移。
- 获得执行授权后持续完成清晰的后续步骤，直到完成或出现真实阻塞。
- 验证范围与风险匹配；不要把“最彻底”误解为无条件运行全套测试。
- 用户或项目明确授权委派且运行时支持时，优先将独立工作交给低上下文 sidecar 子代理；立即阻塞主路径的工作本地做，小任务或共享编辑串行。派单、回收和顺序回退按需读取 [subagent-workflow](../subagent-workflow/SKILL.md)，不默认继承完整历史。

## 宿主资料

按需读取：

- `references/hosts.md`：Codex、Cursor、Pi 的规则发现差异。
- `references/gpt-6-astra.md`：已验证 Astra profile 与未知模型回退。
- `assets/runtime-capabilities.json`：机器可读能力记录。

## 禁止

- 不为每个宿主复制一套相同规则。
- 不把模型能力描述当作写入、发布、付费或外部通信授权。
- 不为未验证型号编造上下文长度、工具或权限。
