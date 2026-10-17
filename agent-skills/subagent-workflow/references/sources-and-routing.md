# 官方来源与适用边界

访问日期：2026-09-30。官方资料可能更新，实际工具与权限以当前宿主及上级规则为准。

## OpenAI：Codex Subagents

- 官方入口：https://developers.openai.com/codex/subagents
- 官方现址：https://learn.chatgpt.com/docs/agent-configuration/subagents
- 依据：独立探索、测试和日志分析可移出主线程，以摘要回收结果，减少主上下文噪声；并行写入需要防止冲突，子代理仍受沙箱与审批约束。
- 适用边界：减少主线程上下文不保证减少总 token；子代理独立执行可能增加总 token 消耗。文档不证明当前宿主已暴露派单、等待或关闭工具，也不提供额外授权；不得从示例推断固定并发数量。

## Anthropic：Agent Skills progressive disclosure

- 官方公开文章：https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- 依据：以 name/description 发现 skill，相关时读取 SKILL.md 正文，进一步细节按需读取 references，避免默认加载全部资料。
- 适用边界：渐进披露说明 skill 的上下文组织，不证明任何宿主具有子代理能力，也不保证委派降低总成本。

## 本 skill 的约束边界

bounded 派单、独立 sidecar 优先、不默认继承完整历史、立即 critical path 本地执行、写集隔离与顺序回退是本 skill 的执行规则，不是官方固定工具 API。只有用户或项目明确授权、上级规则允许且宿主支持时才委派；skill 被加载本身不构成授权。
