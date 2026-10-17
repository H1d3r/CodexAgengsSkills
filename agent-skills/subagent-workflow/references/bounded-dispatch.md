# Bounded 派单与结果契约

首次派单或边界含糊时读取；填入真实路径、命令和验收条件后发送。以下是 prompt 契约，不是虚构的工具 API；用当前宿主工具的实际 schema 调用。

## 派单模板

```text
goal:
  单一交付目标、完成判据与停止点。
ownership:
  cwd: 绝对工作目录；说明当前基线及已有改动。
  write_set: 明确到文件或单一所有权目录；只读任务填写 []。
  exclusions: 禁止修改路径；共享文件由父线程负责。
inputs:
  必要文件/符号/行范围、已确认事实和父线程需要的接口。
  最近 AGENTS.md 与本单命中 skill 路径；references 按需读取。
constraints:
  允许的工具与副作用、必须保留的行为、现有 sandbox/审批边界。
  不覆盖其他 writer、不扩范围、不递归派单、不自动发布。
  缺关键输入或发生所有权/权限冲突时停止相关动作并精确回报。
verification:
  在指定 cwd 执行的最小相关命令和成功判据。
  无法执行时记录原因、可替代证据与未验证门禁。
compact_results:
  status: done / blocked / failed / cancelled
  summary: 决策或结论，不含推理流水账。
  changes: 实际修改路径与关键符号；只读任务写 none。
  checks: 实际命令、cwd、退出状态；未运行不得写 passed。
  evidence: 文件行号、官方来源或必要日志定位，不含密钥。
  risks_or_blockers: 未验证项、共享接口影响、需要父线程的动作。
```

父线程发出前检查：本单输入充分、写集无交集、已有改动已标明、返回结果可直接用于下一步。不要发送整个父线程历史来替代这六项。

## 只读 sidecar 示例

```text
goal: 查明 src/session/refresh.ts 的超时是否会取消底层请求；返回证据，不实现修复。
ownership: cwd=<实际绝对路径>; write_set=[]; 不改源码、配置或测试。
inputs: refreshSession 符号、相关 transport 调用、最近 AGENTS.md；仅加载命中的语言/分析 skill。
constraints: 不访问生产服务，不递归派单，不输出全量文件；缺关键实现只报告精确缺口。
verification: 静态追踪取消信号；若需命令，先确认现有测试无外部副作用并仅运行相关用例。
compact_results: 返回取消链结论、文件行号、实际检查及未验证项，不超过完成目标所需的内容。
```

## 生命周期适配

1. 确认当前宿主的真实派单、等待/完成通知、结果读取、停止/关闭能力和授权；无安全派单能力则本地主线程顺序执行。
2. 只记录必要的 worker 标识、goal、owner、状态；明确父线程继续做什么、何时需要结果。
3. 按依赖回收，优先完成通知/有界等待和增量状态；明确失败后不无限轮询或无条件重派。
4. 核对 compact results 与实际变更，再串行集成共享接口并做最小检查。
5. 保留必要证据后关闭已完成 worker；宿主不支持关闭时记录未能回收的限制。
