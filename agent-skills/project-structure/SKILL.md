---
name: project-structure
description: Classify and place new source, tests, docs, scripts, migrations, generated files, and runtime artifacts without polluting a repository.
---

# Project Structure

## 适用场景

- 创建文件、目录、模块、脚手架或生成产物。
- 设计、审计或整理项目目录。
- 任务触发 `file-create`、`directory-create`、`artifact-generate`、`project-scaffold` 或 `repository-audit`。

## 创建前门禁

1. 读取最近的 `AGENTS.md`、manifest、workspace、框架配置和相似文件位置。
2. 按 `references/artifact-taxonomy.md` 分类目标内容。
3. 优先采用已有结构；绿地项目才使用 `references/language-layouts.md`。
4. 检查目标路径是否会污染根目录、混合职责或提交运行时产物。
5. 只有多个合理路径会造成长期架构差异时才询问用户。

## 强制规则

- 不在无关任务中搬迁历史文件或大规模重排目录。
- 根目录 Markdown 默认只允许 `AGENTS.md` 与 `README.md`；例外必须由项目策略明确声明。
- 计划、设计、ADR、runbook、报告和归档进入 `docs/` 对应分类。
- 测试数据靠近测试；迁移靠近拥有数据模型的服务；API schema 靠近契约所有者。
- 日志、dump、coverage、截图、缓存和临时输出不得作为源码散落或提交。
- 密钥和真实环境配置不得写入仓库；只保留无敏感值的模板。
- 项目确需例外时使用 `.agent-layout.json`；格式见 `references/policy-overrides.md`。

## 审计

使用只读检查器；它只报告，不移动或删除文件：

```bash
python3 -B agent-skills/project-structure/scripts/project-layout-check.py --root . --check
python3 -B agent-skills/project-structure/scripts/project-layout-check.py --root . --json
python3 -B agent-skills/project-structure/scripts/project-layout-check.py --root . --explain path/to/file
```

## 停止条件

确认内容分类、目标路径、项目事实和最小验证后停止。不要为了追求模板一致性覆盖框架生成结构。
