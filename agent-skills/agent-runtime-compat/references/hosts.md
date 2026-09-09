# Agent Host Compatibility

## Shared baseline

- `AGENTS.md` carries the smallest cross-host behavioral contract.
- Skill bundles contain conditional domain guidance.
- Host-specific configuration should reference the shared source rather than duplicate it.
- More specific project rules override reusable defaults.

## Codex

- Use `AGENTS.md` for repository instructions and native `<skill>/SKILL.md` bundles for progressive disclosure.
- Respect the active collaboration mode, sandbox, approvals, tools, and developer-level delegation policy.
- A tool being available does not imply authorization to use it for side effects.

## Cursor

- Treat root `AGENTS.md` as the portable project baseline.
- Use Cursor project rules only when scoped or host-only behavior cannot be represented portably.
- Do not maintain a full duplicated copy of the shared rules.

## Pi

- Treat ancestor `AGENTS.md` or `CLAUDE.md` discovery as the instruction baseline.
- Use Agent Skills bundles for task-specific guidance.
- Avoid bare `pi` routing because mathematical and product uses are ambiguous; require phrases such as `pi coding agent` or `pi agent`.

## Unknown hosts

1. Detect instruction discovery and precedence.
2. Detect read/write and external action permissions.
3. Detect skill format and tool availability.
4. Use the portable baseline when host-only features are absent.
5. Record unverified capabilities instead of guessing.
