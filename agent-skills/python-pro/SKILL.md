---
name: python-pro
description: Use modern Python tooling, typing, async, packaging, and evidence-based performance practices.
---

# Python Pro Skill（for Agents）

## 适用场景
- Python 3.12+、生产服务、异步 I/O、性能优化与现代工具链
- 使用 `uv`、`ruff`、`mypy`/`pyright`、`pyproject.toml` 的项目
- FastAPI、Pydantic、SQLAlchemy async、后台任务或高并发脚本

## 执行顺序

1. 先确认 Python 版本、依赖锁文件、启动入口和部署目标。
2. 区分 I/O 密集与 CPU 密集：前者用 async，后者优先进程池或经过测量的线程池。
3. 公共边界使用类型标注；API、配置和外部数据使用显式模型校验。
4. 先建立最小可复现测试，再做性能或并发优化。
5. 对外部调用定义超时、取消、重试、幂等和资源关闭策略。

## 现代工具链

- 优先遵循现有 `pyproject.toml` 与锁文件，不擅自替换包管理器。
- 项目允许时使用 `uv` 管理环境与依赖，使用 `ruff` 统一格式化和 lint。
- 类型检查使用仓库已采用的 `mypy` 或 `pyright`，不要并行引入第二套规则。
- 发布前检查依赖锁定、可复现安装、最小运行时镜像和安全扫描。

## 异步与性能

- 不要在 async 函数中直接调用长时间阻塞的同步网络、文件或数据库 API。
- 使用结构化并发，明确任务生命周期；取消时释放连接、锁、临时文件和后台任务。
- 性能问题先用基准或 profiler 定位，再修改数据结构、批量 I/O、缓存或并发度。
- 关注内存峰值、连接池、队列背压和重试风暴，不以“加并发”代替诊断。

## 验证

```bash
uv run ruff check .
uv run mypy .
uv run pytest -q
```

按仓库现有工具替换命令；没有 `uv` 时不要为了执行检查临时改造依赖管理。

## 反模式

- 把 `dict` 当作跨层契约，缺少输入和输出模型
- `except Exception: pass` 或无限重试
- 在循环中无超时地发起网络请求
- 未测量就引入缓存、进程池或复杂异步抽象

## 协作关系

- 详细测试策略：`python-testing`、`python-testing-patterns`
- REST/API 契约：`api-design`、`api-contract`
- 数据库与索引：`sql`、`database-performance`
