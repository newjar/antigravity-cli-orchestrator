# Full Orchestration

Choose this pattern for comprehensive features that benefit from a dedicated root coordinator and specialized execution roles across the complete development lifecycle.

## Orchestration Topology

```text
Root Orchestrator (gemini-3.1-pro-high)
├── Explorer     (gemini-3.8-flash-high) - Read-only repository mapping
├── Researcher   (gemini-3.8-flash-high) - Documentation & API verification
├── Worker       (gemini-3.1-pro-high)   - Bounded implementation
├── Tester       (gemini-3.8-flash-high) - Test suites & regression checks
└── Reviewer     (gemini-3.1-pro-high)   - Independent post-change audit
```

## Configuration Files

The project-scoped configuration is stored under `.agy/`:

- `.agy/config.toml`: Top-level orchestrator model, subagent defaults, concurrency limit.
- `.agy/agents/explorer.toml`: Explorer role instructions and sandbox settings.
- `.agy/agents/worker.toml`: Worker role instructions and implementation rules.
- `.agy/agents/tester.toml`: Tester role instructions and testing guidance.
- `.agy/agents/reviewer.toml`: Reviewer role instructions and audit criteria.
- `.agy/agents/researcher.toml`: Researcher role instructions and documentation requirements.

## Execution Lifecycle

1. **Gate Evaluation:** Root determines if the task spans multiple files, multiple workstreams, or requires external research.
2. **Phase 1: Research & Discovery:**
   Spawn `explorer` and `researcher` in parallel using one `invoke_subagent` call.
3. **Phase 2: Architectural Decision:**
   Root digests exploration findings, formulates the implementation plan, and locks file boundaries.
4. **Phase 3: Implementation:**
   Spawn `worker` subagent(s) with explicit delegation contracts. For multiple concurrent workers, enable `Workspace: "branch"`.
5. **Phase 4: Verification:**
   Spawn `tester` subagent to execute existing suites, verify new functionality, and confirm bug reproduction paths.
6. **Phase 5: Independent Review:**
   Spawn `reviewer` to inspect the unified diff against regressions, security issues, and edge cases.
7. **Phase 6: Integration & Reporting:**
   Root synthesizes results, confirms all subagents finished, and delivers a concise final summary.
