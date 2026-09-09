# Project AGENTS

本仓库维护可复用的 Agent Skills、确定性路由和项目目录约束，适用于 Codex、Cursor、Pi 等支持 `AGENTS.md` 或 Agent Skills 的运行时。
>  `agent-skills` 路径位于 `~/.codex/` 下面提到的 `agent-skills` 统一默认在这个地方查找对应的skill

## 指令优先级

- 系统/开发者/用户当前指令 > 最近且更具体的项目规则 > 本仓库通用 skill。
- 项目 manifest、锁文件、CI、框架配置和既有目录事实优先于通用建议。
- 规则冲突时不得静默任选；采用高优先级规则并记录差异。

## 默认工作流

- 先理解意图和边界，再读取上下文；“查看”不等于“修改”。
- 先读后写，只做有证据的最小改动，不顺手重构无关代码。
- 多步骤任务维护有序 TODO，同时只保留一个进行中事项。
- 修改后运行最小相关检查；无法运行时说明替代验证和未验证门禁。
- 达到完成条件后停止，不擅自扩展范围。

## Skill 路由

- `agent-skills/skill-routing.json` 是路由、优先级、依赖和事件触发的唯一事实源。
- 根据任务文本、目标文件、项目 manifest 和运行时事件读取命中的最小 skill 集合，不全量加载。
- 维护路由时使用 `python3 -B agent-skills/skill-router.py --check` 和 `--self-test`。
- 在修改 `agent-skills/` 本身时，额外遵循 `agent-skills/AGENTS.md`。

## 文件创建门禁

- 创建文件、目录或生成产物前，必须加载 `project-structure` skill，并先分类内容与确认目标路径。
- 事件路由：`--event file-create`、`--event directory-create`、`--event artifact-generate`。
- 优先复用已有相似文件的位置；只有绿地项目才应用默认语言布局。
- 不因无关任务移动历史文件；目录不确定且会影响架构时才询问用户。
- 根目录 Markdown 只允许 `AGENTS.md` 与 `README.md`；其他文档放入 `docs/` 或子项目的 `docs/`。

## 安全与 Git

- 不泄露或提交密钥、Token、`.env`、日志、构建产物和运行时 dump。
- 不执行会丢失他人改动的 destructive Git 操作。
- 不自动发布、部署或修改外部系统，除非用户明确授权。

## 语言

- 过程说明使用中文；代码、代码注释和提交信息默认使用英文。
- 面向用户的产品文案按项目既有 i18n 规则处理。
