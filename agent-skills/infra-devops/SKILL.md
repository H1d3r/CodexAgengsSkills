---
name: infra-devops
description: Change infrastructure, CI/CD, containers, cloud resources, and deployment workflows with rollback and security controls.
---

# Infra / DevOps Skill（for Agents）

## 适用场景
- Docker / Compose / CI-CD / 构建发布 / 运行时环境配置 / 监控告警
- 与部署、回滚、发布流程相关的变更任务

## 核心原则

1. **先读基础设施边界**：先确认环境（local/staging/prod）的差异再改。
2. **可重复部署**：任何变更都应支持可复现、可回滚。
3. **风险可控**：优先灰度发布、分阶段验证、最小停机。

## 强制执行清单

- 所有环境变量与密钥通过 Secret/CI Secret 管理，不写入仓库明文。
- 构建镜像固定 base 与依赖版本（避免浮动标签）。
- 健康检查、就绪检查、指标和日志路径保持可观测。
- 发布脚本保留幂等性和失败回退路径。
- 运维文档同步更新（端口、卷、资源配额、鉴权信息）。

## 推荐实践

- 结构化日志（JSON）与统一 trace id。
- 针对关键服务设置资源 limits/requests 与健康检查阈值。
- 大规模改动先在灰度环境验证：`build -> test -> deploy -> smoke test -> canary`。
- 使用分支策略避免环境配置“脏”传播。

## 常用质量门禁

- `docker build` / 镜像安全扫描（如项目约定）
- `.github/workflows/*.yml` / GitLab CI 脚本语法检查
- 关键命令 dry-run（尤其是数据库迁移、脚本批量操作）
- 发布后验收脚本（如有）至少覆盖关键接口

## 反模式（避免）

- 未做备份就直接执行有副作用的脚本。
- 使用 `latest` 作为生产镜像标签。
- 临时禁用安全组/防火墙后未恢复。
- 日志级别默认 debug 在生产泄露过量信息。

## 与仓库冲突时的优先级

- 以 CI/CD、K8s/容器配置与运维 SOP 为准。
- 与本文件冲突时，按真实发布流程与合规要求执行，并说明原因。
