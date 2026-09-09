---
name: task-template
description: Structure multi-step engineering work with a single active item, focused validation, and explicit delivery notes.
---

# 任务执行模板（可复用）

## 任务开始

- [ ] 明确目标（修复/重构/分析/新增）
- [ ] 确认语言与主入口
- [ ] 识别必须遵循的仓库级约束

## 变更执行

- [ ] 逐步最小改动
- [ ] 每次改完同步记录文件
- [ ] 避免一次性批量大改

## 验证

- [ ] 运行对应语言/模块命令
- [ ] 失败时给出根因与降级方案
- [ ] 无法运行时给出替代手工验证方式

## 交付

- [ ] 影响范围说明
- [ ] 未满足项与风险说明
- [ ] 下一步建议（必要时）
