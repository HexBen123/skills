# Tool Reference — exact signatures & output shapes

The real MCP signatures, parameters, and what each call actually returns (observed, not guessed). Use this when you need a parameter name or want to predict an output shape. The combine *strategy* is in `rules/`; this is the raw API.

## fast-context — `mcp__fast-context__fast_context_search`

Semantic search via Windsurf Devstral over a repo map + greps. Live filesystem (sees off-index files). Costs remote API quota.

| Param | Default | Notes |
|---|---|---|
| `project_path` | — (required) | **Absolute** path to repo root. |
| `query` | — (required) | Natural-language intent. |
| `max_turns` | 3 | Search rounds. `1` quick · `2` focused · `4–5` end-to-end trace. More = slower + more quota. |
| `include_code_snippets` | `false` | `false` → paths + line ranges + grep keywords (~2–5KB). `true` → full snippets (~45KB). |
| `max_results` | 10 | `3–5` focused · `15–30` broad. Cap 30. |
| `tree_depth` | 3 | Initial map depth. **Auto-capped on large repos** (observed: requested 3 → used 1 on a 1529-file repo). `0` = auto. |
| `exclude_paths` | `[]` | e.g. `['**/*.lang','**/*.json','**/*.properties','**/assets/**','**/*.md']`. |

**Output shape (lightweight):**
- `Found N relevant files (A from AI search, B from grep keyword expansion).`
- Per hit: `--- [i/N] <abs path> (Lx-Ly) ---`, tagged `(grep match) [grep expanded]` when it came from keyword expansion (weaker signal).
- `grep keywords: ...` — reusable for follow-up grep/queries.
- `[config] project_path=..., tree_depth=..., max_turns=..., max_results=..., grep_expanded=...` — the **actual** params used (read this to see auto-downgrades).

## codegraph — `mcp__codegraph__codegraph_*`

Pre-built SQLite graph of indexed source. Exact, instant, offline, reproducible, zero quota. Only static edges, only indexed files. Every call accepts `projectPath` (absolute; required when the target isn't the current project).

| Tool | Key params | Returns |
|---|---|---|
| `codegraph_explore` | `query`, `maxFiles` (12) | **PRIMARY.** Relationships (extends/references/imports/calls) + **verbatim line-numbered source** grouped by file/symbol. NL question or bag of names. |
| `codegraph_search` | `query`, `kind`, `limit` | Symbol locations only (no code). |
| `codegraph_node` | `symbol`, `includeCode` (false), `file`, `line` | One symbol: location, signature, edge trail, body (`includeCode:true`). Same-named → returns every match unless pinned by `file`/`line`. |
| `codegraph_callers` | `symbol`, `limit` (20) | Static inbound call edges. Aggregates same-named symbols (notes "Aggregated results across N symbols"). |
| `codegraph_callees` | `symbol`, `limit` (20) | Static outbound call edges. |
| `codegraph_impact` | `symbol`, `depth` (2) | Symbols affected by changing one — refactor blast radius. |
| `codegraph_files` | `path`, `pattern`, `format` | Indexed file tree + language/symbol counts. |
| `codegraph_status` | — | Index health: files/nodes/edges/languages. Run if unsure a repo is indexed. |

**There is no `codegraph_trace`.** Paths/flows → `codegraph_explore` with spanning symbol names.

**Output notes:**
- `explore` source blocks are **Read-equivalent** ("verbatim, current on-disk source… do not Read a file shown here").
- `callers`/`callees` list `name (kind) - path:line`. Empty → `No callers/callees found for "X"` (see `gotchas.md#dynamic-dispatch-callers` before trusting it).
- A codegraph call against an unindexed path returns empty/errors — confirm with `codegraph_status`.

## Quick mapping: question → first call

- "where is …" / no symbol name → `fast_context_search` (lightweight)
- "show me the body of <known symbol>" → `codegraph_node(includeCode:true)`
- "how does <area> work" → `codegraph_explore` (names or NL)
- "who calls / what breaks if I change <symbol>" → `codegraph_callers` / `codegraph_impact` (+ dynamic cross-check)
- "the path from A to B" → `codegraph_explore("A B …")`
- "where is <event> fired / registered" → `fast_context_search` (codegraph is blind here)
