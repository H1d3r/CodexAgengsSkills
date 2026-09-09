---
name: java
description: Apply project-aware Java conventions for applications, services, libraries, and tests.
---

# Java Skill（for Agents）

## 适用场景
- Spring Boot / Spring MVC / Spring Cloud / Android / 后端服务模块
- API、任务调度、数据访问、依赖注入、并发与配置管理任务

## 核心原则

1. **先看工程约定**：先确认 `mvn/gradle` 配置、Profiles 与运行环境。
2. **最小变更**：只改任务直接相关逻辑，不发散到架构重构。
3. **错误可追踪**：异常要有分层语义，不能把错误静默吞掉。

## 强制执行清单

- 优先使用构建工具标准生命周期（`mvn/gradlew`）与标准测试入口。
- `RuntimeException` 滥用要降级，尽量使用自定义业务异常。
- 外部调用（HTTP/DB/消息）统一超时和重试策略。
- 配置值统一来源于配置中心/环境变量，不硬编码。

## 推荐实践

- 使用 `@ControllerAdvice`/统一异常处理器，不在每层重复 try-catch。
- 数据库查询避免 N+1，优先分页与索引验证。
- 并发任务显式线程模型与取消/中断策略。
- DTO 与实体分离，减少跨层污染。

## 常用质量门禁

- `./mvnw -q -DskipTests=false test`
- `./gradlew test`
- `./mvnw -q spotless:check` / `./gradlew spotlessCheck`（若启用）
- `./mvnw -q checkstyle:check` / `./gradlew checkstyleMain`

## 反模式（避免）

- Service 层直接拼 SQL 字符串而无参数化验证。
- 控制器层混入大量业务判断。
- 捕获 `Exception` 后只打印不处理。
- 大事务中混入网络调用。

## 与仓库冲突时的优先级

- 以 `pom.xml` / `build.gradle` / CI pipeline 为准。
- 本文件仅作为默认行为，遇到工程约束按真实命令与规则执行。
