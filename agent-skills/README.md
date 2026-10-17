# Agent Skills Index

本目录包含原生 `<skill>/SKILL.md` Bundle、确定性路由和目录治理工具。普通任务只加载命中的最小集合。

## 路由与维护文件

- `skill-routing.json`：skill 路径、层级、优先级、文本/事件/项目事实触发、依赖和兼容宿主。
- `skill-router.py`：路由、解释输出、一致性检查和固定回归。
- `route-regression.json`：关键词、歧义、事件和项目事实回归用例。
- `AGENTS.md`：仅约束本技能目录的维护。

## Skill Bundles

- `python`：Apply project-aware Python conventions for services, libraries, scripts, refactors, and validation.
- `python-pro`：Use modern Python tooling, typing, async, packaging, and evidence-based performance practices.
- `python-testing`：Plan and implement Python tests with focused unit, integration, and regression coverage.
- `python-testing-patterns`：Apply pytest fixtures, mocks, parametrization, async tests, and property-based testing safely.
- `go`：Apply project-aware Go conventions for services, CLIs, packages, APIs, and tests.
- `go-pro`：Design production Go services with clear package boundaries, errors, observability, and performance evidence.
- `go-concurrency`：Design and review Go concurrency, cancellation, backpressure, goroutine ownership, and shutdown behavior.
- `rust`：Apply project-aware Rust conventions for services, CLIs, libraries, async systems, and validation.
- `rust-pro`：Handle advanced Rust ownership, lifetimes, traits, unsafe code, FFI, and measured performance work.
- `rust-async`：Design Rust async tasks, cancellation, timeouts, backpressure, and Tokio lifecycle behavior.
- `csharp`：Apply project-aware C# conventions for applications, libraries, APIs, and tests.
- `csharp-pro`：Use modern C# typing, nullable analysis, async, dependency injection, and performance practices.
- `dotnet-backend`：Design ASP.NET Core and EF Core services with clear layers, validation, security, and background work.
- `javascript-typescript`：Apply project-aware JavaScript and TypeScript conventions for applications, libraries, and services.
- `frontend-react`：Build or review React and TypeScript UI behavior, state, accessibility, performance, and tests.
- `java`：Apply project-aware Java conventions for applications, services, libraries, and tests.
- `project-structure`：Classify and place new source, tests, docs, scripts, migrations, generated files, and runtime artifacts without polluting a repository.
- `agent-runtime-compat`：Adapt AGENTS.md and skill behavior across Codex, Cursor, Pi, GPT-6 Astra, and unknown future agent runtimes by detecting capabilities instead of guessing from model names.
- `frontend-framework`：Build or review frontend framework components, state, routing, accessibility, and performance.
- `mobile`：Apply iOS and Android lifecycle, permissions, state, networking, accessibility, and release-aware practices.
- `backend`：Design or modify backend routes, services, repositories, configuration, and error handling with clear boundaries.
- `api-design`：Design APIs and integrations with explicit consumers, resources, errors, idempotency, and lifecycle decisions.
- `api-contract`：Define and evolve API schemas, compatibility, authentication, errors, pagination, and examples.
- `sql`：Design and change relational schemas, queries, transactions, migrations, and data access safely.
- `database-performance`：Diagnose and improve database performance using query plans, indexes, measurements, and safe rollout.
- `infra-devops`：Change infrastructure, CI/CD, containers, cloud resources, and deployment workflows with rollback and security controls.
- `security`：Review and implement authentication, authorization, secrets, input handling, privacy, and compliance controls.
- `testing`：Plan focused unit, integration, contract, and end-to-end testing with reproducible evidence.
- `task-template`：Structure multi-step engineering work with a single active item, focused validation, and explicit delivery notes.
- `tdd`：Use red-green-refactor when test-first development is requested or materially reduces implementation risk.
- `quality-gates`：Select proportionate validation gates and report commands, results, impact, and remaining risk.
- `coding-standards`：Apply cross-language readability, naming, error handling, typing, and minimal-change standards.

- `cpp`：Implement and review C++ code using project-selected standards, RAII ownership, lifetime safety, and focused compiler, CMake, and test checks.
- `typescript`：Implement and review TypeScript code with project-version-aware configuration, gradual strictness, safe narrowing, and runtime validation at data boundaries.
- `frontend-vue`：Build or review Vue UI components, reactivity, accessibility, performance, and tests using the project's installed Vue version and TypeScript conventions.
- `frontend-design`：Design or refine user-facing web layouts, visual hierarchy, responsive styling, themes, and accessible interactions when explicitly requested; not for pure TypeScript logic or routine nonvisual fixes.
- `subagent-workflow`：Delegate bounded independent work to supported subagents when the user or project explicitly requests delegation or lower main-thread context; avoid generic agent or task mentions.

## 使用

```bash
python3 -B agent-skills/skill-router.py "python api testing"
python3 -B agent-skills/skill-router.py --event file-create "add a helper" --explain
python3 -B agent-skills/skill-router.py --project-root . --json "review implementation"
python3 -B agent-skills/skill-router.py --file src/App.vue --explain "fix component"
python3 -B agent-skills/skill-router.py --event ui-design --explain "design dashboard"
python3 -B agent-skills/skill-router.py --event task-dispatch --explain "implement independent modules"
```

## 新增或修改 Skill

1. 使用 `<name>/SKILL.md`，目录名与 frontmatter `name` 一致。
2. `description` 只描述真实能力和触发边界。
3. 条件性长说明放 `references/`，确定性复用逻辑放 `scripts/`。
4. 在 `skill-routing.json` 注册显式优先级和最小触发集合。
5. 增加命中与不误触发回归，然后运行 `--check`、`--self-test` 和单元测试。

## 验证

```bash
python3 -B agent-skills/skill-router.py --check
python3 -B agent-skills/skill-router.py --self-test
python3 -B -m unittest discover -s agent-skills/tests -p 'test_*.py'
```

本目录不包含技能库复制、安装或目标路径部署说明。
