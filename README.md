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

- 根据任务文本、项目事实和运行时事件加载最小 skill 集合。
- `SKILL.md` 保持短小，条件性细节放入 `references/`。
- 创建文件前先分类，优先遵循项目既有结构。
- 目录检查器只读审计，不自动移动或删除文件。
- 本仓库不包含技能库复制、安装或目标路径部署步骤。

## 维护验证

```bash
python3 -B agent-skills/skill-router.py --check
python3 -B agent-skills/skill-router.py --self-test
python3 -B -m unittest discover -s agent-skills/tests -p 'test_*.py'
python3 -B agent-skills/project-structure/scripts/project-layout-check.py --root . --check
```

## 文档

- `docs/architecture/skill-system.md`：v3 架构、路由和扩展规则。
- `docs/reports/2026-09-08-framework-audit.md`：本轮审计与迁移决策。
- `docs/archive/tgcustomer-rust-rule.md`：已退出全局路由的历史项目规则。
