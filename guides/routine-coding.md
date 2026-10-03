# Routine Coding

Choose this workflow for predictable day-to-day coding tasks, localized bug fixes, and well-specified feature additions where cost efficiency and rapid delivery are balanced.

## Recommended Model Setup

In `.agy/config.toml`:

```toml
# Root / orchestrator
model = "claude-sonnet-5-5-high"
model_reasoning_effort = "high"

approval_policy = "on-request"
sandbox_mode = "workspace-write"

[agents]
enabled = true
max_concurrent_threads_per_session = 4
default_subagent_model = "gemini-3.8-flash-high"
default_subagent_reasoning_effort = "high"
```

In `.agy/agents/`:
- `explorer.toml`: `gemini-3.8-flash-high`
- `worker.toml`: `gemini-3.8-flash-high` (or `claude-sonnet-5-5-high`)
- `tester.toml`: `gemini-3.8-flash-high`
- `reviewer.toml`: `claude-sonnet-5-5-high`
- `researcher.toml`: `gemini-3.8-flash-high`

## Workflow Pattern

1. **Lightweight Exploration:** Root or a fast Flash explorer identifies the precise files to modify.
2. **Bounded Implementation:** Worker implements the change adhering to existing codebase patterns.
3. **Targeted Testing:** Tester executes relevant unit and integration tests.
4. **Focused Review:** Reviewer audits the diff for regressions, boundary errors, or missing test cases.
5. **Presentation:** Root presents what changed, tests run, and verification evidence.
