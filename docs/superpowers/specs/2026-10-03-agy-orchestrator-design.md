# Design Specification: agy-orchestrator

- **Date:** 2026-10-03
- **Topic:** Antigravity (agy) AI Agent Orchestrator
- **Status:** Approved by User

## 1. Executive Summary

`agy-orchestrator` is a model-configurable AI agent orchestration framework designed specifically for Google Antigravity (`agy`). Adapted from `codex-orchestrator`, `agy-orchestrator` provides an interactive setup installer (`setup.sh` and `setup.ps1`), an orchestration skill leveraging Antigravity's native `invoke_subagent` mechanism, role-based configuration templates under `.agy/`, token usage tracking for Antigravity session transcripts, comprehensive workflow guides, and an automated test suite.

Unlike fixed-profile setups, `agy-orchestrator` does not enforce arbitrary profile tiers (such as Pro vs Plus). Instead, the installer presents a verified catalog of Antigravity models along with reasoning effort options, allowing direct per-role model and effort configuration.

---

## 2. Architecture and Repository Structure

The `agy-orchestrator` repository is located at `/home/nfajar/agy-orchestrator` and structured as follows:

```text
.
├── .agents/
│   └── skills/
│       └── agy-orchestrator/
│           └── SKILL.md            # Primary Antigravity orchestrator skill
├── templates/
│   ├── agy/
│   │   ├── config.toml             # Target root orchestrator and agents configuration
│   │   └── agents/
│   │       ├── explorer.toml       # Explorer role template
│   │       ├── worker.toml         # Worker role template
│   │       ├── tester.toml         # Tester role template
│   │       ├── reviewer.toml       # Reviewer role template
│   │       └── researcher.toml     # Researcher role template
│   └── GEMINI.md                   # Project instructions template for target repo
├── guides/
│   ├── fast-iteration.md           # Quick focused iterations
│   ├── complex-repo-work.md        # Large-scale multi-agent coordination
│   ├── routine-coding.md           # Standard daily feature workflows
│   ├── full-orchestration.md       # Complete 5-role orchestration cycle
│   ├── model-selection.md          # Guide on models and reasoning efforts
│   └── token-usage.md              # Token consumption monitoring guide
├── scripts/
│   └── token_usage.py              # CLI token tracker for Antigravity sessions
├── tests/
│   ├── test_model_configuration.py # Shell and PowerShell installer test suite
│   └── test_token_usage.py         # Token usage transcript parser test suite
├── setup.sh                        # POSIX shell interactive installer
├── setup.ps1                       # PowerShell interactive installer
├── AGENTS.md                       # Repository instructions
├── GEMINI.md                       # Antigravity project-level rules
├── README.md                       # Complete documentation
├── LICENSE                         # Apache 2.0 license
└── .gitignore                      # Standard VCS exclusions
```

---

## 3. Roles and Model Catalog

### 3.1 Model Catalog

The installer ships with 14 verified Antigravity model identifiers discovered from `agy models`, plus support for custom model inputs:

1. `gemini-3.8-flash-high` - Gemini 3.8 Flash (High reasoning)
2. `gemini-3.8-flash-medium` - Gemini 3.8 Flash (Medium reasoning)
3. `gemini-3.8-flash-low` - Gemini 3.8 Flash (Low reasoning)
4. `gemini-3.7-flash-high` - Gemini 3.7 Flash (High reasoning)
5. `gemini-3.7-flash-medium` - Gemini 3.7 Flash (Medium reasoning)
6. `gemini-3.7-flash-low` - Gemini 3.7 Flash (Low reasoning)
7. `gemini-3.6-flash-high` - Gemini 3.6 Flash (High reasoning)
8. `gemini-3.6-flash-medium` - Gemini 3.6 Flash (Medium reasoning)
9. `gemini-3.6-flash-low` - Gemini 3.6 Flash (Low reasoning)
10. `gemini-3.1-pro-high` - Gemini 3.1 Pro (High reasoning)
11. `gemini-3.1-pro-low` - Gemini 3.1 Pro (Low reasoning)
12. `claude-sonnet-4-6` - Claude Sonnet 4.6 (Thinking)
13. `claude-opus-4-6-thinking` - Claude Opus 4.6 (Thinking)
14. `gpt-oss-120b-medium` - GPT-OSS 120B (Medium reasoning)
15. `custom` - Free-form model ID string

Supported reasoning effort levels: `low`, `medium`, `high`, `xhigh`, `max`.

### 3.2 Recommended Role Defaults

When users accept recommended defaults (by pressing Enter):
- **Root / Orchestrator:** `gemini-3.1-pro-high` (effort: `high`) - Architecture, task decomposition, synthesis.
- **Worker:** `gemini-3.1-pro-high` (effort: `high`) - High-precision implementation.
- **Reviewer:** `gemini-3.1-pro-high` (effort: `high`) - Independent audit, regression detection, security checks.
- **Explorer:** `gemini-3.8-flash-high` (effort: `high`) - Rapid read-only codebase mapping.
- **Tester:** `gemini-3.8-flash-high` (effort: `high`) - Test execution, reproduction, and test authoring.
- **Researcher:** `gemini-3.8-flash-high` (effort: `high`) - Documentation and external API verification.
- **Default Subagent:** `gemini-3.8-flash-high` (effort: `high`).
- **Max Concurrent Subagents:** `4`.

---

## 4. Configuration Storage in Target Repository

When installed into a target project, configurations are organized as:
- `.agy/config.toml`: Defines root orchestrator model, effort, approval policy, sandbox mode, and default subagent parameters.
- `.agy/agents/{explorer,worker,tester,reviewer,researcher}.toml`: Defines model, effort, workspace mode, and developer instructions per role.
- `.agents/skills/agy-orchestrator/SKILL.md`: The orchestration skill loaded by Antigravity.
- `GEMINI.md` / `AGENTS.md`: Instruction rules directing the agent to activate `agy-orchestrator` for non-trivial coding tasks.

---

## 5. Antigravity Tooling and Orchestration Mechanics

### 5.1 Subagent Invocation

Delegation is executed via Antigravity's native `invoke_subagent` tool:
- `TypeName`: `research` (read-only tools) for `explorer` and `researcher`; `self` (full write/command tools) for `worker` and `tester`.
- `Role`: 2-5 descriptive words (e.g. `Codebase Explorer`, `Implementation Worker`).
- `Model`: Mapped from `.agy/` configuration (tier `pro`, `flash`, `flash_lite`, `inherit`, or exact model identifier).
- `Workspace`:
  - `inherit` for `explorer`, `tester`, `researcher`.
  - `inherit` for single/linear `worker`.
  - `branch` or `share` for concurrent workers to isolate modifications.
- `Prompt`: Enforces the strict Delegation Contract: Objective, Scope, Context, Constraints, Deliverable, Acceptance Criteria.

### 5.2 Delegation Gate and Parallelism
- Tasks crossing multiple files, modules, services, or requiring independent exploration/review must spawn at least one subagent.
- Independent tasks must be spawned concurrently in a single `invoke_subagent` call by specifying multiple entries in the `Subagents` array.
- Dependent tasks must be executed sequentially (Explore -> Architect -> Implement -> Test -> Review -> Final Verification).
- Reactive Wakeup: Antigravity automatically awakens the root agent when subagents complete or send messages; no manual polling or sleep loops are permitted.

---

## 6. Token Usage Tracker (`scripts/token_usage.py`)

A pure standard-library Python utility tailored for Antigravity:
- Inspects `~/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` and session databases.
- Aggregates `input_tokens`, `cache_read_tokens`, and `output_tokens` across all turns for the root session and child subagent sessions spawned via `invoke_subagent`.
- Commands:
  - `--list [--date YYYY-MM-DD]`: Lists sessions with start time, opening prompt, and total token consumption.
  - `--root <id-or-prefix> [--format md|json]`: Displays formatted breakdown table by role and model.
  - `--latest`: Automatically analyzes the most recent session.

---

## 7. Testing Strategy

Automated test suites in `tests/`:
1. `tests/test_model_configuration.py`:
   - Validates skill directory naming (`agy-orchestrator`) and frontmatter.
   - Verifies neutrality and clean templating.
   - Tests `setup.sh` with simulated user inputs (numeric selections, default enter keys, concurrency limits, file conflict warnings, `GEMINI.md` appending).
   - Tests `setup.ps1` with PowerShell when available.
   - Validates generated `.agy/config.toml` and `.agy/agents/*.toml` content.
2. `tests/test_token_usage.py`:
   - Tests transcript reading, token summation, subagent linking, and output formatting.

---

## 8. Definition of Done Checklist

- [x] Design specification written and approved.
- [ ] Templates for `.agy/` configs and `GEMINI.md` created.
- [ ] Skill `.agents/skills/agy-orchestrator/SKILL.md` implemented.
- [ ] Installers `setup.sh` and `setup.ps1` implemented and executable.
- [ ] Guides in `guides/` written.
- [ ] Python script `scripts/token_usage.py` implemented.
- [ ] Automated tests in `tests/` implemented and passing.
- [ ] Root `README.md`, `LICENSE`, `AGENTS.md`, and `GEMINI.md` created.
- [ ] Implementation plan and walkthrough exported to `.antigravity/plans/` and `.antigravity/walkthroughs/`.
