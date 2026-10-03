# Model Selection and Reasoning Effort

Antigravity (`agy`) provides a curated selection of `gemini-3.8-*` and `claude-*` models tailored for speed, reasoning depth, and token efficiency.

## Curated Model Catalog

| Identifier | Display Name | Best Suited For |
| :--- | :--- | :--- |
| `gemini-3.8-flash-high` | Gemini 3.8 Flash (High) | Fast exploration, tester runs, researchers, high-efficiency workers |
| `gemini-3.8-flash-medium` | Gemini 3.8 Flash (Medium) | Balanced speed and cost for routine subagent tasks |
| `gemini-3.8-flash-low` | Gemini 3.8 Flash (Low) | Minimal latency, simple lookups, and basic test execution |
| `claude-opus-5-5-high` | Claude Opus 5.5 (High) | Maximum reasoning depth for critical architectural design and audits |
| `claude-opus-5-5-medium` | Claude Opus 5.5 (Medium) | High-level synthesis with balanced thinking overhead |
| `claude-opus-5-5-low` | Claude Opus 5.5 (Low) | High-capacity reasoning with minimal latency |
| `claude-sonnet-5-5-high` | Claude Sonnet 5.5 (High) | Root orchestrator, critical workers, deep refactors, and security reviews |
| `claude-sonnet-5-5-medium` | Claude Sonnet 5.5 (Medium) | Balanced implementation and code analysis |
| `claude-sonnet-5-5-low` | Claude Sonnet 5.5 (Low) | Fast coding and code inspection |
| `custom` | Custom Model ID | Any custom model identifier supported by your environment |

## Reasoning Effort Levels

Antigravity CLI supports configuring reasoning effort via `--effort <level>`:
- `low`: Minimal thinking tokens; fastest response times.
- `medium`: Balanced reasoning for typical coding steps.
- `high`: Deep reasoning effort; ideal for complex algorithms, test design, and architecture.
- `xhigh`: Extended reasoning effort for edge-case resolution.
- `max`: Maximum reasoning effort for difficult mathematical or multi-system constraints.

## Best Practice Allocation

- **Root / Orchestrator:** Use `claude-sonnet-5-5-high` to ensure tasks are decomposed cleanly without context fragmentation.
- **Worker:** Use `claude-sonnet-5-5-high` for high-precision coding or `gemini-3.8-flash-high` for routine implementations.
- **Explorer & Researcher:** Use `gemini-3.8-flash-high` for fast indexing, read-only tracing, and web searches.
- **Tester:** Use `gemini-3.8-flash-high` for running test suites and reproducing issues quickly.
- **Reviewer:** Use `claude-sonnet-5-5-high` or `claude-opus-5-5-high` to catch subtle logic bugs, race conditions, and security issues.
