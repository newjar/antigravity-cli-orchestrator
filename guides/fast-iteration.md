# Fast Iteration

Choose this workflow when speed and low latency matter more than exhaustive multi-stage reasoning.

## Recommended Model Setup

For fast iteration in Antigravity (`agy`), select high-speed Flash tier models across all roles:

In `.agy/config.toml`:

```toml
# Root / orchestrator
model = "gemini-3.8-flash-high"
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
- `worker.toml`: `gemini-3.8-flash-high`
- `tester.toml`: `gemini-3.8-flash-high`
- `reviewer.toml`: `gemini-3.8-flash-high`
- `researcher.toml`: `gemini-3.8-flash-high`

## Workflow Pattern

1. **Focused Exploration:** Spawn a single explorer if code paths are uncertain.
2. **Immediate Implementation:** Delegate directly to a worker with narrow file scope.
3. **Targeted Validation:** Run fast unit tests with the tester.
4. **Skip Heavy Review:** For low-risk, internal, or prototype changes, root can inspect diff directly or run a lightweight review.
