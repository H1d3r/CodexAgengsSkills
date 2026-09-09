---
name: coding-standards
description: Apply cross-language readability, naming, error handling, typing, and minimal-change standards.
---

# Coding Standards Skill（for Agents）

## 适用场景
- 通用代码质量约束：JS/TS 为主，也用于 Python/Java/Go 等跨语言复用规范讨论
- 审查 PR/重构前后的可读性和一致性

## 核心原则

1. **可读性第一**：变量/函数名表达意图，代码本身可解释。
2. **KISS/DRY/YAGNI**：简单实现优先，减少重复；不预埋未来功能。
3. **类型友好**：关键路径明确类型，尽量减少 any/反模式。

## 质量清单（最小）

- 统一格式化与 lint。
- 统一错误处理，不吞错。
- 异步并发明确边界（并行/串行/超时）。
- 数据不可变优先，避免副作用污染。
- 每次行为修改伴随最小测试。

## 常用约定

- 命名：函数名动宾式（`fetchUserProfile`）、变量名语义化。
- 避免函数参数超过合理数量，长参数用对象。
- 不在生产代码里用 `console.log`/`print` 泄漏敏感行为。
- 重复逻辑优先抽象成 helper，不创建伪通用抽象。
- 注释只解释“为什么”，不解释“是什么”。

## 反模式（避免）

- 大量 `any` 与不完整类型。
- 无界面测试直接 merge。
- 以复杂技巧掩盖清晰度。
- 直接在核心逻辑里硬编码常量。
- 不必要的深层回调/嵌套（适当拆函数）。

## 与多语言任务的映射

- JS/TS：按项目 lint + tsconfig。
- Python：配合 `ruff`/`mypy` 的规则。
- Go：遵守 `gofmt` + 错误语义。
- Rust：错误语义分层 + `clippy`。
- Java/C#：统一异常与空值策略。

## 语言与注释

- 代码、标识符和代码注释默认使用英文；注释解释原因、约束和非显然权衡。
- 项目已有更具体的语言或文档规范时遵循项目约定。
