# agy-orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `agy-orchestrator`, a model-configurable AI agent orchestration setup for Google Antigravity (`agy`), adapted from `codex-orchestrator` with interactive installers, role configurations, orchestration skill, Antigravity token usage tracker, workflow guides, and automated tests.

**Architecture:** A standalone installer repository providing POSIX shell (`setup.sh`) and PowerShell (`setup.ps1`) interactive installers that install project-scoped Antigravity orchestration files into a target repository (`.agy/config.toml`, `.agy/agents/*.toml`, `.agents/skills/agy-orchestrator/SKILL.md`, and `GEMINI.md`/`AGENTS.md`), alongside a token tracker script (`scripts/token_usage.py`) that parses Antigravity session transcripts.

**Tech Stack:** POSIX Shell (`sh`), PowerShell (`pwsh`), Python 3 (standard library only), Markdown, TOML.

**Spec:** `docs/superpowers/specs/2026-10-03-agy-orchestrator-design.md`

## Global Constraints

- Standalone installer kit targeting another repository without requiring external dependencies beyond Python 3 and basic shell tools.
- No hardcoded model vendors or vendor-locked profiles; all 14 Antigravity models plus custom models selectable via numbered menu.
- Orchestration uses Antigravity native tool `invoke_subagent` (not `spawn_agent`).
- Role configs saved under `.agy/config.toml` and `.agy/agents/*.toml` in the target project.
- Token tracker reads Antigravity session logs at `~/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`.
- No emoji in code, commit messages, or technical documentation.

---

### Task 1: Scaffolding, Base Templates, and Project Rules

**Files:**
- Create: `templates/agy/config.toml`
- Create: `templates/agy/agents/explorer.toml`
- Create: `templates/agy/agents/worker.toml`
- Create: `templates/agy/agents/tester.toml`
- Create: `templates/agy/agents/reviewer.toml`
- Create: `templates/agy/agents/researcher.toml`
- Create: `templates/GEMINI.md`
- Create: `GEMINI.md`
- Create: `AGENTS.md`
- Create: `LICENSE`
- Create: `.gitignore`

**Interfaces:**
- Consumes: Spec sections 2, 3, 4
- Produces: Default TOML template structures read by `setup.sh` and `setup.ps1` to produce `.agy/` files in target repos.

- [ ] **Step 1: Create .gitignore and LICENSE**
  Write `.gitignore` (ignoring `__pycache__/`, `.pytest_cache/`, temp files) and Apache 2.0 `LICENSE`.

- [ ] **Step 2: Create root GEMINI.md and AGENTS.md**
  Write project orchestration instructions for `agy-orchestrator` itself in `GEMINI.md` and `AGENTS.md`.

- [ ] **Step 3: Create templates/agy/config.toml and role templates**
  Create `templates/agy/config.toml` and role files in `templates/agy/agents/` (`explorer.toml`, `worker.toml`, `tester.toml`, `reviewer.toml`, `researcher.toml`) with standard model defaults (`gemini-3.1-pro-high` for orchestrator/worker/reviewer, `gemini-3.8-flash-high` for explorer/tester/researcher).

- [ ] **Step 4: Create templates/GEMINI.md**
  Create the template rule file that gets appended into target repositories when installed.

- [ ] **Step 5: Verify template syntax**
  Check that all TOML templates parse cleanly without syntax errors using Python `tomllib` or basic validation.

---

### Task 2: Antigravity Orchestration Skill (`.agents/skills/agy-orchestrator/SKILL.md`)

**Files:**
- Create: `.agents/skills/agy-orchestrator/SKILL.md`

**Interfaces:**
- Consumes: Spec section 5
- Produces: Skill markdown definition loaded by Antigravity CLI and IDE.

- [ ] **Step 1: Write frontmatter and header**
  Define `name: agy-orchestrator` and a comprehensive description specifying triggers (multi-file features, cross-component debugging, parallel workstreams, delegation requests).

- [ ] **Step 2: Define Delegation Gate and Root Agent Responsibilities**
  Detail root responsibilities (architecture, decomposition, integration, verification) and hard gate: non-trivial tasks must invoke subagents using `invoke_subagent`.

- [ ] **Step 3: Define Subagent Invocation Policy with invoke_subagent**
  Document exact parameter usage:
  - `TypeName`: `research` for read-only roles (`explorer`, `researcher`); `self` for execution roles (`worker`, `tester`).
  - `Role`: 2-5 words.
  - `Prompt`: Structured contract (Objective, Scope, Context, Constraints, Deliverable, Acceptance Criteria).
  - `Model`: Read from `.agy/` config.
  - `Workspace`: `inherit` vs `branch`/`share`.

- [ ] **Step 4: Define Parallelism, Workflows, and Reactive Wakeup**
  Document multi-agent arrays in single `invoke_subagent` call for parallel independent tasks; sequential stages for dependent tasks; and reactive wakeup without polling.

- [ ] **Step 5: Define Verification and Completion Gate**
  Checklist before completing: all spawned subagents completed, diff reviewed, highest-value tests verified, no orphaned subagents.

---

### Task 3: Token Usage Tracker (`scripts/token_usage.py`) and Tests (`tests/test_token_usage.py`)

**Files:**
- Create: `tests/test_token_usage.py`
- Create: `scripts/token_usage.py`

**Interfaces:**
- Consumes: Spec section 6; Antigravity transcript format (`transcript.jsonl`)
- Produces: CLI script with `--list`, `--root <id>`, `--latest`, `--format md|json`

- [ ] **Step 1: Write unit tests in tests/test_token_usage.py**
  Create table-driven tests for:
  - Reading step entries from mock `transcript.jsonl` files (extracting `input_tokens`, `cache_read_tokens`, `output_tokens`).
  - Associating subagent conversation IDs from `invoke_subagent` calls with the parent session.
  - Aggregating totals by thread and role.
  - Markdown table output and JSON formatting.
  - CLI argument parsing (`--list`, `--root`, `--latest`, `--format`).

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest tests/test_token_usage.py -v`
  Expected: FAIL with `ModuleNotFoundError` or test errors because `scripts/token_usage.py` does not exist yet.

- [ ] **Step 3: Implement scripts/token_usage.py**
  Implement the standard-library Python utility:
  - Path discovery in `~/.gemini/antigravity-cli/brain/` and `~/.gemini/antigravity-cli/conversations/`.
  - JSONL stream reader handling both compact `transcript.jsonl` and full transcripts.
  - Subagent linkage via `invoke_subagent` tool calls.
  - Aggregation engine and reporting formatters (Markdown tables and JSON).

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 -m unittest tests/test_token_usage.py -v`
  Expected: PASS all tests.

---

### Task 4: Interactive Installers (`setup.sh`, `setup.ps1`) and Tests (`tests/test_model_configuration.py`)

**Files:**
- Create: `tests/test_model_configuration.py`
- Create: `setup.sh`
- Create: `setup.ps1`

**Interfaces:**
- Consumes: Spec section 3 & 4; templates from Task 1; skill from Task 2
- Produces: Executable setup scripts that configure target repositories.

- [ ] **Step 1: Write tests in tests/test_model_configuration.py**
  Write tests for:
  - `test_skill_directory_uses_agy_name`: skill dir is `.agents/skills/agy-orchestrator`.
  - `test_skill_templates_are_vendor_neutral`: no legacy vendor strings hardcoded in skill instructions.
  - `test_shell_installer_numeric_selection`: running `setup.sh` with simulated answers (numeric model choice, custom concurrency, target repo path) correctly writes `.agy/config.toml` and `.agy/agents/*.toml`.
  - `test_shell_installer_defaults`: pressing Enter keeps recommended defaults.
  - `test_shell_installer_gemini_md_merging`: existing `GEMINI.md` content is preserved and appended cleanly.
  - `test_powershell_installer`: tests `setup.ps1` if PowerShell is available.

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest tests/test_model_configuration.py -v`
  Expected: FAIL because `setup.sh` does not exist yet.

- [ ] **Step 3: Implement POSIX shell installer setup.sh**
  Implement:
  - Target directory prompt and validation (rejecting empty or same source directory).
  - Numbered model catalog menu (1-14 + 15 Custom) with reasoning effort levels.
  - Per-role prompts with recommended default presets (Orchestrator, Worker, Explorer, Tester, Reviewer, Researcher, Default Subagent).
  - Maximum concurrent subagents prompt.
  - Copy and configure `.agy/config.toml` and `.agy/agents/*.toml` using portable `awk` / `sed`.
  - Install `.agents/skills/agy-orchestrator/SKILL.md`.
  - Smart append to target `GEMINI.md` / `AGENTS.md`.
  - Overwrite safety detection and warnings.
  - Make executable: `chmod +x setup.sh`.

- [ ] **Step 4: Implement PowerShell installer setup.ps1**
  Implement corresponding logic in PowerShell with cross-platform support (Windows PowerShell 5.1 & PowerShell 7+).

- [ ] **Step 5: Run test to verify it passes**
  Run: `python3 -m unittest tests/test_model_configuration.py -v`
  Expected: PASS all tests.

---

### Task 5: Workflow Guides (`guides/`) and README (`README.md`)

**Files:**
- Create: `guides/fast-iteration.md`
- Create: `guides/complex-repo-work.md`
- Create: `guides/routine-coding.md`
- Create: `guides/full-orchestration.md`
- Create: `guides/model-selection.md`
- Create: `guides/token-usage.md`
- Create: `README.md`

**Interfaces:**
- Consumes: Spec sections 1-7
- Produces: User-facing documentation and workflow playbooks.

- [ ] **Step 1: Write guides**
  Author all 6 guides covering iterative development, complex multi-agent execution, routine coding, full 5-role orchestration, model selection strategies, and token monitoring.

- [ ] **Step 2: Write README.md**
  Author comprehensive README detailing:
  - Project overview and origin.
  - Architecture and layout.
  - Available Antigravity model catalog.
  - Setup instructions (Linux/macOS shell and Windows PowerShell).
  - Role responsibilities and delegation rules.
  - Token tracking usage.
  - Running automated tests.

---

### Task 6: End-to-End Verification and Export Documentation

**Files:**
- Create: `.antigravity/plans/agy-orchestrator-plan.md`
- Create: `.antigravity/changelog/2026-10-03-1840-initial-agy-orchestrator.md`
- Create: `.antigravity/walkthroughs/agy-orchestrator-walkthrough.md`

**Interfaces:**
- Consumes: User rules 6 & 7 (Definition of Done)
- Produces: Audit trail and verification evidence.

- [ ] **Step 1: Run complete test suite**
  Run: `python3 -m unittest discover tests/ -v`
  Ensure 100% tests pass.

- [ ] **Step 2: Run end-to-end dry run installation**
  Run `./setup.sh` targeting a temporary directory, verify generated `.agy/` configs and `.agents/skills/agy-orchestrator/SKILL.md`.

- [ ] **Step 3: Run token_usage.py on current active session**
  Run `python3 scripts/token_usage.py --latest` to ensure it successfully reads the current session transcript.

- [ ] **Step 4: Export plan, changelog, and walkthrough to .antigravity/**
  Write:
  - `.antigravity/plans/agy-orchestrator-plan.md`
  - `.antigravity/changelog/2026-10-03-1840-initial-agy-orchestrator.md`
  - `.antigravity/walkthroughs/agy-orchestrator-walkthrough.md`
