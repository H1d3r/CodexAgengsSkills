---
name: database-performance
description: Diagnose and improve database performance using query plans, indexes, measurements, and safe rollout.
---

# Database Performance & Optimization Skill（for Agents）

## 适用场景
- 查询慢、超时、CPU/IO 压力大、索引设计疑难、容量瓶颈
- 数据库架构演进与迁移风险评估

## 核心原则

1. **先证据后优化**：先有执行计划与指标，后改 SQL/索引。
2. **索引按场景定制**：按过滤/排序/连接链路创建，不“为了优化而优化”。
3. **可回滚优先**：大改动作必须可回滚与回归验证。

## 强制执行清单

- 使用 `EXPLAIN`/`ANALYZE` 识别主路径。
- 对高频查询优先做索引/查询重写，再考虑缓存。
- 检查事务范围，避免长事务锁表。
- 连接池、超时、会话参数与并发上限检查。
- 验证前后至少做同等负载回放。

## 常用优化方向

- 读写分离与索引覆盖。
- 分页/偏移优化（keyset、游标）
- 去除 N+1 与重复查询。
- 预聚合、缓存和物化视图（按写入代价权衡）。
- 大表变更走在线方案（`ADD CONCURRENTLY`/分批迁移）。

## 反模式（避免）

- 仅凭感觉添加索引。
- 直接在主库上执行重建/重索引未评估窗口。
- 线上回归未跑压力基线就发布。
- 优化后未监控，导致新瓶颈。

## 与项目约束优先级

- 以数据库类型和迁移机制（Liquibase/Flyway/Prisma migration）为准。
- 与现有 SQL 风格与 DBA SOP 兼容为前提。
