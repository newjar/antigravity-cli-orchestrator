# Model Selection and Reasoning Effort

Antigravity (`agy`) provides a diverse catalog of models tailored for different execution speeds, reasoning depths, and token cost profiles.

## Available Model Catalog

| Identifier | Display Name | Best Suited For |
| :--- | :--- | :--- |
| `gemini-3.8-flash-high` | Gemini 3.8 Flash (High) | Fast exploration, tester runs, researchers, high-efficiency workers |
| `gemini-3.8-flash-medium` | Gemini 3.8 Flash (Medium) | Balanced speed and cost for routine subagent tasks |
| `gemini-3.8-flash-low` | Gemini 3.8 Flash (Low) | Minimal latency, simple lookups, and basic test execution |
| `gemini-3.7-flash-high` | Gemini 3.7 Flash (High) | Stable flash tier for exploration and testing |
| `gemini-3.7-flash-medium` | Gemini 3.7 Flash (Medium) | Medium-effort tasks on previous-generation Flash |
| `gemini-3.7-flash-low` | Gemini 3.7 Flash (Low) | Low-effort fast responses |
| `gemini-3.6-flash-high` | Gemini 3.6 Flash (High) | Legacy Flash model with high reasoning effort |
| `gemini-3.6-flash-medium` | Gemini 3.6 Flash (Medium) | Legacy Flash model with medium reasoning effort |
| `gemini-3.6-flash-low` | Gemini 3.6 Flash (Low) | Legacy Flash model with low reasoning effort |
| `gemini-3.1-pro-high` | Gemini 3.1 Pro (High) | Root orchestrator, critical workers, deep architecture, security reviewer |
| `gemini-3.1-pro-low` | Gemini 3.1 Pro (Low) | Fast Pro-tier execution with lower reasoning overhead |
| `claude-sonnet-4-6` | Claude Sonnet 4.6 (Thinking) | Complex coding refactors, nuanced logic audits, and high-stakes reviews |
| `claude-opus-4-6-thinking` | Claude Opus 4.6 (Thinking) | Maximum reasoning depth for mission-critical architectural design |
| `gpt-oss-120b-medium` | GPT-OSS 120B (Medium) | Open-weight foundation model alternative |
| `custom` | Custom Model ID | Any custom model identifier supported by your environment |

## Reasoning Effort Levels

Antigravity CLI supports configuring reasoning effort via `--effort <level>`:
- `low`: Minimal thinking tokens; fastest response times.
- `medium`: Balanced reasoning for typical coding steps.
- `high`: Deep reasoning effort; ideal for complex algorithms, test design, and architecture.
- `xhigh`: Extended reasoning effort for edge-case resolution.
- `max`: Maximum reasoning effort for difficult mathematical or multi-system constraints.

## Best Practice Allocation

- **Root / Orchestrator:** Use `gemini-3.1-pro-high` to ensure tasks are decomposed cleanly without context fragmentation.
- **Worker:** Use `gemini-3.1-pro-high` for tricky logic or `gemini-3.8-flash-high` for routine implementations.
- **Explorer & Researcher:** Use `gemini-3.8-flash-high` for fast indexing and web searches.
- **Reviewer:** Use `gemini-3.1-pro-high` or `claude-sonnet-4-6` to catch subtle logic bugs, race conditions, and security issues.
