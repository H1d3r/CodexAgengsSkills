# Artifact Taxonomy

| 分类 | 内容 | 默认位置 |
|---|---|---|
| `source` | 生产源码 | 语言或框架源码根 |
| `unit-test` | 单元测试 | 与源码共置或项目现有 unit test 根 |
| `integration-test` | 跨模块/外部依赖测试 | `tests/integration/` 或项目既有位置 |
| `e2e-test` | 完整用户流程测试 | `tests/e2e/`、`e2e/` 或框架既有位置 |
| `fixture` | 测试输入、golden data | 对应测试目录内的 `fixtures/`、`testdata/` |
| `snapshot` | 测试快照 | 测试工具约定目录，不进入生产源码 |
| `documentation` | 计划、设计、ADR、runbook、报告 | `docs/<category>/` |
| `migration` | 数据库或协议迁移 | 拥有该模型的服务或模块下 `migrations/` |
| `api-schema` | OpenAPI、Proto、GraphQL | 现有 `api/`、`openapi/`、`proto/` 或契约模块 |
| `script` | 可重复执行的辅助脚本 | `scripts/` 或项目既有 `tools/` |
| `tooling` | 开发工具及其源码 | `tools/` 或独立 workspace package |
| `deployment` | Docker、Kubernetes、IaC、发布配置 | `deploy/`、`infra/` 或工具约定路径 |
| `asset` | 图片、字体、模板、静态文件 | 拥有它的应用资源目录 |
| `generated` | 机器生成、不可手改内容 | 生成器配置指定目录并清楚标记 |
| `runtime-artifact` | 日志、dump、coverage、截图、缓存 | 系统临时目录或明确忽略的 artifact 目录 |
| `secret` | 密钥、token、真实环境配置 | 外部密钥系统或未提交本地配置 |

## 文档分类

```text
docs/
├── plans/       # 尚未完成的执行计划
├── design/      # 架构与设计说明
├── adr/         # 已决策且需要长期追踪的记录
├── runbooks/    # 运维与故障处理步骤
├── reports/     # 审计、测试、调研和交付报告
└── archive/     # 已退出活动规则或历史材料
```

## 决策顺序

1. 相同内容的既有文件位置。
2. 框架或构建工具要求的位置。
3. workspace/模块所有权边界。
4. 本表默认位置。
5. 影响长期结构时询问用户。
