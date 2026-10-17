# AgengsSkills

面向 Codex、Cursor、Pi 等 AI Agent 的可复用约束、原生 Skill Bundle、确定性路由和项目目录治理库。

## 结构

```text
.
├── AGENTS.md                         # 跨 Agent 的高信号入口
├── README.md                         # 项目说明
├── agent-skills/
│   ├── AGENTS.md                     # 仅约束技能库维护
│   ├── README.md                     # Skill 索引
│   ├── skill-routing.json            # 路由唯一事实源
│   ├── skill-router.py               # 路由与一致性检查
│   ├── route-regression.json         # 固定回归用例
│   ├── <skill>/SKILL.md              # 原生 Skill Bundle
│   ├── project-structure/            # 目录治理 skill 与检查器
│   └── agent-runtime-compat/         # Agent/模型能力兼容规则
└── docs/                              # 架构、报告和历史材料
```

## 核心原则

- 根据任务文本、目标文件、项目事实和运行时事件加载最小 skill 集合。
- `SKILL.md` 保持短小，条件性细节放入 `references/`。
- 创建文件前先分类，优先遵循项目既有结构。
- 目录检查器只读审计，不自动移动或删除文件。
- 本仓库不包含技能库复制、安装或目标路径部署步骤。

## 开发调用

路径以调用者的实际技能库根目录为准；以下示例针对本仓库，不执行安装或全局同步。

```bash
python3 -B agent-skills/skill-router.py "C++ RAII review" --explain
python3 -B agent-skills/skill-router.py "fix component" --file src/App.vue --explain
python3 -B agent-skills/skill-router.py "fix types" --file src/parser.ts --project-root . --json
python3 -B agent-skills/skill-router.py "设计管理后台" --event ui-design --explain
python3 -B agent-skills/skill-router.py "实现独立模块" --event task-dispatch --explain
```

- 新增 C++、TypeScript 和 Vue 专项，依据项目版本与官方资料，而非强制升级或替换工具链。
- `frontend-design` 提供可引用的语义 token 与现代风格参考，仅在设计任务中加载；既有品牌与组件库优先。
- 授权且工具可用时，独立子任务优先交给子代理，主线程保留关键路径、集成与验收。
- 路由只输出候选路径，不自动执行工具或读取全部 skill；宿主需遵守 `AGENTS.md` 的读取约定。声明事件不会自行创建运行时 hook。

## 维护验证

```bash
python3 -B agent-skills/skill-router.py --check
python3 -B agent-skills/skill-router.py --self-test
python3 -B -m unittest discover -s agent-skills/tests -p 'test_*.py'
python3 -B agent-skills/frontend-design/scripts/validate-tokens.py --self-test
python3 -B agent-skills/project-structure/scripts/project-layout-check.py --root . --check
```

## 文档

- `docs/architecture/skill-system.md`：v3 架构、路由和扩展规则。
- `docs/reports/2026-09-08-framework-audit.md`：本轮审计与迁移决策。
- `docs/archive/tgcustomer-rust-rule.md`：已退出全局路由的历史项目规则。
