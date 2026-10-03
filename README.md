# Antigravity Orchestrator (agy-orchestrator)

A model-configurable AI agent orchestration setup for Google Antigravity (`agy`), featuring independent model and reasoning-effort selection per role, native `invoke_subagent` delegation, workspace isolation, interactive shell/PowerShell installers, and session token tracking.

---

## Origin and Design Basis

This repository is adapted from [`codex-orchestrator`](https://github.com/newjar/codex-orchestrator) (itself inspired by `donvito/codex-astra-luna-orchestrator`), re-engineered specifically for Google Antigravity (`agy`).

Key Antigravity adaptations:
- **Direct Model Selection:** Rather than imposing fixed plan tiers, the installer presents a verified catalog of 14 Antigravity models (`gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.6-flash`, `gemini-3.1-pro`, Claude models, and GPT-OSS) with thinking/reasoning effort settings.
- **Native Tooling:** Replaces Codex's `spawn_agent` with Antigravity's native `invoke_subagent` tool, leveraging Antigravity's reactive wakeup mechanism.
- **Workspace Isolation:** Supports Antigravity workspace modes (`inherit`, `branch`, `share`) to isolate concurrent worker edits.
- **Project Structure:** Writes project-scoped role configurations to `.agy/config.toml` and `.agy/agents/*.toml`, installs `.agents/skills/agy-orchestrator/SKILL.md`, and configures `GEMINI.md` / `AGENTS.md`.
- **Transcript Token Tracking:** Includes `scripts/token_usage.py` tailored to parse Antigravity's session transcripts (`transcript.jsonl`) and aggregate tokens across root and subagent turns.

---

## Layout

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

## Recommended Role Defaults

When users accept recommended defaults during setup:

| Role | Default Model | Reasoning Effort | Primary Focus |
| :--- | :--- | :--- | :--- |
| **Root / Orchestrator** | `gemini-3.1-pro-high` | High | Architecture, task decomposition, integration, synthesis |
| **Worker** | `gemini-3.1-pro-high` | High | Bounded implementation with focused diffs |
| **Reviewer** | `gemini-3.1-pro-high` | High | Independent diff review, security, and edge-case validation |
| **Explorer** | `gemini-3.8-flash-high` | High | Read-only repository mapping and symbol tracing |
| **Tester** | `gemini-3.8-flash-high` | High | Bug reproduction, regression validation, test execution |
| **Researcher** | `gemini-3.8-flash-high` | High | External API verification and documentation search |
| **Default Subagent** | `gemini-3.8-flash-high` | High | Generic fallback subagent |
| **Concurrency Limit** | `4` | - | Maximum concurrent subagent threads |

---

## Project Setup

Clone or copy this repository to your machine.

### Linux and macOS

Run the interactive shell installer:

```bash
./setup.sh
```

### Windows (PowerShell)

Run the PowerShell installer:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Or using PowerShell 7 (`pwsh`):

```powershell
pwsh -File .\setup.ps1
```

### Setup Prompts

1. **Target repository path:** Enter the absolute or relative path to the existing target project.
2. **Model selections:** Choose model numbers (1-14 + 15 Custom) for root, default subagent, explorer, worker, tester, reviewer, and researcher, or press Enter to keep recommended defaults.
3. **Concurrency limit:** Set maximum concurrent subagents (default: 4).
4. **Components:** Choose whether to install `.agy`, `agy-orchestrator` skill, and `GEMINI.md`.

---

## Subagent Roles and Invocation

In Antigravity (`agy`), delegation is performed via the native `invoke_subagent` tool:

```json
{
  "Subagents": [
    {
      "TypeName": "research",
      "Role": "Backend Explorer",
      "Prompt": "...",
      "Model": "flash",
      "Workspace": "inherit"
    },
    {
      "TypeName": "self",
      "Role": "Implementation Worker",
      "Prompt": "...",
      "Model": "pro",
      "Workspace": "branch"
    }
  ]
}
```

- `explorer` & `researcher`: Read-only tools (`TypeName: "research"`).
- `worker` & `tester`: Full tool access (`TypeName: "self"`).
- Independent tasks are launched in parallel in a single `invoke_subagent` call.
- Parallel workers use `Workspace: "branch"` or `"share"` to prevent git workspace collisions.

---

## Token Usage Tracking

Monitor and aggregate token consumption across root sessions and spawned subagents:

```bash
# View the most recent session
python3 scripts/token_usage.py --latest

# List recent sessions
python3 scripts/token_usage.py --list

# Inspect a specific conversation
python3 scripts/token_usage.py --root <conversation-id>

# Output machine-readable JSON
python3 scripts/token_usage.py --latest --format json
```

---

## Running Automated Tests

Run the full automated test suite:

```bash
python3 -m unittest discover tests/ -v
```

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
