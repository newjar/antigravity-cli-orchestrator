# Complex Repository Work

Choose this workflow for significant architectural changes, cross-service refactors, high-concurrency debugging, and safety-critical repository tasks.

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
max_concurrent_threads_per_session = 6
default_subagent_model = "gemini-3.8-flash-high"
default_subagent_reasoning_effort = "high"
```

In `.agy/agents/`:
- `explorer.toml`: `gemini-3.8-flash-high` (read-only mapping)
- `worker.toml`: `claude-sonnet-5-5-high` (high-accuracy implementation)
- `tester.toml`: `gemini-3.8-flash-high` (test execution & regression suites)
- `reviewer.toml`: `claude-opus-5-5-high` (rigorous diff review)
- `researcher.toml`: `gemini-3.8-flash-high` (documentation verification)

## Workflow Pattern

1. **Parallel Exploration:** Launch multiple explorers concurrently in one `invoke_subagent` call to inspect disparate modules (e.g. API frontend, backend services, database schema).
2. **Architectural Direction:** Root consolidates findings, defines boundaries, and breaks the task into independent workstreams.
3. **Workspace-Isolated Workers:** Spawn workers with `Workspace: "branch"` or `"share"` to isolate file modifications and avoid git workspace merge conflicts.
4. **Validation and Reproduction:** Testers run full test suites, reproduce reported bugs, and assert regression passes.
5. **Independent Audit:** Reviewer audits the unified diff against security standards, edge-case resilience, and regression risks.
6. **Final Synthesis:** Root verifies integration and presents a consolidated summary to the user.
