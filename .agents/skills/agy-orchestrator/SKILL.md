---
name: agy-orchestrator
description: Orchestrate complex Antigravity (agy) coding work with model and role assignments configured in .agy/config.toml and .agy/agents/*.toml. Use for multi-file features, debugging across components, repo-wide changes, parallelizable workstreams, or whenever the user asks to delegate or use subagents. Do not use for trivial one-file edits or simple questions.
---

# Antigravity Orchestrator

The user's explicit instructions take precedence over this skill.

## Goal

Use the root agent as the high-quality orchestrator.

Delegate bounded execution work to specialized subagents using Antigravity's `invoke_subagent` tool, then have the root integrate, verify, and present the final result.

The expected default topology is:

- root: configured in `.agy/config.toml`
- explorer: configured in `.agy/agents/explorer.toml`
- worker: configured in `.agy/agents/worker.toml`
- tester: configured in `.agy/agents/tester.toml`
- reviewer: configured in `.agy/agents/reviewer.toml`
- researcher: configured in `.agy/agents/researcher.toml`

Use the model and reasoning effort configured for each role.

This is a requirement, not a preference. Use the model and reasoning effort selected for each role; do not assume a particular model or effort.

Do not override a role's selected model or reasoning effort unless the user explicitly asks for escalation or an agent reports that the task requires higher-level reasoning.

---

## Delegation gate

Before doing substantive repository work, classify the task as either:

- root-only
- delegated

Use root-only only when the task is genuinely small, localized, and does not materially benefit from independent exploration, implementation, testing, research, or review.

The task MUST be delegated when at least one of the following is true:

- the task spans multiple files, modules, services, or components
- there are two or more independent workstreams
- repository exploration is needed before implementation
- implementation and verification benefit from separate context
- debugging requires tracing across components
- multiple modules or services need inspection
- external or version-specific facts need verification
- an independent post-change review is materially useful
- the user explicitly asks for delegation, parallelism, agents, or subagents

When a task qualifies for delegation, the root MUST call `invoke_subagent` before performing the delegated work itself.

Do not merely describe, simulate, or internally reason about delegation. Actual subagents must be invoked.

If `invoke_subagent` is unavailable or fails, explicitly report that failure. Do not silently fall back to doing required delegated work in the root thread.

For every delegated task, invoke at least one subagent. Do not create subagents solely to satisfy this rule when the task is genuinely root-only.

---

## Root-agent responsibilities

The root agent owns:

1. understanding the user's actual goal
2. choosing the architecture and implementation direction
3. decomposing the task
4. deciding which tasks can run in parallel
5. invoking the appropriate subagents via `invoke_subagent`
6. giving each subagent a bounded delegation contract
7. resolving conflicting subagent findings
8. integrating changes
9. reviewing the final diff
10. running or coordinating final verification
11. presenting the final result to the user

Subagents provide evidence and bounded execution. They do not own the overall direction. The root must not offload architectural ownership to a subagent.

---

## Subagent invocation policy

When invoking subagents via `invoke_subagent`, use the configuration defined in `.agy/config.toml` and `.agy/agents/*.toml`:

- **explorer**: configured in `.agy/agents/explorer.toml`
  - `TypeName`: `"research"` (read-only tools)
  - `Workspace`: `"inherit"`
- **worker**: configured in `.agy/agents/worker.toml`
  - `TypeName`: `"self"` (full write and execution capabilities)
  - `Workspace`: `"inherit"` for single/linear tasks, or `"branch"` / `"share"` when running concurrent workers that could edit conflicting files
- **tester**: configured in `.agy/agents/tester.toml`
  - `TypeName`: `"self"` (ability to run tests and write test files)
  - `Workspace`: `"inherit"`
- **reviewer**: configured in `.agy/agents/reviewer.toml`
  - `TypeName`: `"research"` (read-only diff audit)
  - `Workspace`: `"inherit"`
- **researcher**: configured in `.agy/agents/researcher.toml`
  - `TypeName`: `"research"` (web search and documentation lookup)
  - `Workspace`: `"inherit"`

### Invocation parameters

For every delegated task:

1. Call `invoke_subagent` with the `Subagents` array.
2. Specify a clear, descriptive `Role` (e.g. `"Backend Explorer"`, `"Feature Worker"`, `"Regression Tester"`).
3. Assign the configured `Model` (e.g. tier `"pro"`, `"flash"`, `"flash_lite"`, or the explicit model ID configured in `.agy/`).
4. Set the appropriate `Workspace` mode (`"inherit"`, `"branch"`, or `"share"`).
5. Provide a bounded delegation contract in `Prompt`.

Do not silently substitute the root agent for a required configured worker. Routine execution should follow the configured role models and reasoning efforts.

---

## Delegation contract

Every subagent prompt MUST follow this structured contract:

- **Objective:** One concrete outcome.
- **Scope:** Exact files, module, subsystem, or question.
- **Context:** Only the essential information needed to succeed.
- **Constraints:** What must not change or be touched.
- **Deliverable:** What the subagent must return or implement.
- **Acceptance criteria:** How success will be checked.

Prefer narrow tasks that can finish independently.

Good contract example:
```markdown
## Objective
Trace where POST /api/v1/invoices validates currency codes.

## Scope
src/billing/ and tests/billing/

## Context
We are adding support for multi-currency transactions.

## Constraints
Do not edit any files. Read-only exploration.

## Deliverable
Return the exact file paths, line ranges, validation logic, and existing unit tests.

## Acceptance Criteria
Concrete file and line references pinpointing currency validation.
```

---

## Role selection

Use `explorer` for:
- repository mapping
- tracing execution or data flow
- locating symbols, functions, and tests
- dependency and configuration inspection
- identifying implementation boundaries

Use `worker` for:
- bounded implementation
- small refactors with explicit scope
- targeted bug fixes
- adding requested features to clearly owned files

Use `tester` for:
- bug reproduction
- targeted test suite execution
- validation and regression checks
- writing new test cases for modified features

Use `reviewer` for:
- independent post-change review
- correctness, race-condition, and edge-case checks
- security review (secrets, sanitization, permissions)
- regression analysis and test completeness audit

Use `researcher` for:
- current API or framework behavior
- dependency, library, or version compatibility questions
- primary documentation verification

---

## Parallelism and workflows

### Parallel execution

When two or more delegated tasks are independent, pass all of them in a single `invoke_subagent` call:

```json
{
  "Subagents": [
    {
      "TypeName": "research",
      "Role": "Backend API Explorer",
      "Prompt": "...",
      "Model": "flash",
      "Workspace": "inherit"
    },
    {
      "TypeName": "research",
      "Role": "Frontend Component Explorer",
      "Prompt": "...",
      "Model": "flash",
      "Workspace": "inherit"
    }
  ]
}
```

Do not invoke independent subagents one-by-one with intervening pauses unless later tasks genuinely depend on earlier results.

### Sequential execution for dependent tasks

Serialize dependent work:
1. **Explore:** Spawn explorers to map the affected areas.
2. **Architect:** Root decides implementation direction and file boundaries.
3. **Implement:** Spawn worker(s) with bounded ownership.
4. **Test:** Spawn tester to run suites and check for regressions.
5. **Review:** Spawn reviewer for independent diff review.
6. **Final Verification:** Root validates final diff and runs top-level checks.

### Multi-worker workspace isolation

When delegating tasks to multiple workers simultaneously, set `Workspace: "branch"` or `"share"` to prevent git workspace collision. The root integrates or cherry-picks the verified branches.

---

## Reactive wakeup and monitoring

Antigravity operates with a **reactive wakeup** model:
- When a subagent completes or sends a message, the orchestrator is automatically woken up.
- **Do NOT run manual sleep or polling loops.** Stop tool calls and allow the system to notify you upon completion.
- To check active subagents, use `manage_subagents` with action `"list"`.
- To send additional instructions to a running subagent, use `send_message`.

---

## Cost and context discipline

- Use each role's selected model for routine subagent execution.
- Keep the root context clean: summarize evidence, critical diffs, test results, and reviewer findings rather than pasting thousands of lines of raw logs.
- Subagents should return conclusions, file paths, line ranges, commands run, and test outcomes.

---

## Escalation and failure handling

A subagent should report back instead of expanding scope when encountering:
- an architectural decision
- a breaking API or schema change
- a new dependency requirement
- unclear requirements with conflicting outcomes
- changes outside its assigned scope

The root decides what to do next. The root owns model escalation decisions.

If a subagent fails:
1. Inspect the failure reason.
2. Decide whether the task should be retried, narrowed, reassigned, or handled by the root.
3. Do not silently ignore failed delegations.
4. If `invoke_subagent` fails repeatedly, record the fallback explicitly.

---

## Completion gate and final verification

Before producing the final answer for a delegated task, confirm that:
- every required subagent completed or explicitly failed
- material findings and diffs were integrated
- conflicting findings were resolved
- required verification was performed
- no required subagent is left unhandled

Before claiming completion, the root must:
1. Inspect the final diff.
2. Confirm the requested behavior is actually implemented.
3. Check material reviewer findings.
4. Run or confirm highest-value tests.
5. State any validation that could not be performed.

---

## User-facing reporting

Summarize the results concisely:
- What was changed
- Files modified
- Tests run and validation evidence
- Remaining risks or limitations
- Subagents that contributed (role, model, status)
