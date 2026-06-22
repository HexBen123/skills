# CLAUDE.md

Formal docs live under `skills/`. Before any task that involves **locating, tracing, or understanding code**, read `skills/code-recon/SKILL.md` — it is the router for the fast-context + codegraph combo. Reach for these MCP tools instead of hand-searching with Grep/Glob.

<!-- The <always-applicable> and <task-routing> XML tags below are load-bearing:
     XML-tag blocks survive context compression better than plain headings. -->

<always-applicable>

**Always Read (every code-understanding task)**
- `skills/code-recon/rules/using-the-tools.md`

</always-applicable>

<task-routing>

## Quick Routing (survives context truncation)

All paths under `skills/code-recon/`.

| Task | Read | Workflow |
|------|------|----------|
| Explore / "where is X" / no symbol name yet (探索/在哪) | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §A |
| Trace flow / "how does X work" / who triggers event (追流程/谁触发) | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §B |
| Callers / impact / "what breaks if I change X" (谁调用/影响面) | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §C |
| Known-symbol lookup / source of X (已知符号取源码) | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §D |
| Other / unlisted | `rules/using-the-tools.md` | match the closest `workflows/recon-playbook.md` section |

</task-routing>

## Auto-Triggers

- **About to Grep / Glob / open files at random to find "where" or "how"** in a non-trivial codebase → STOP, route through the combo (fast-context → codegraph). That reflex is the exact thing this skill replaces.
- **New code-understanding task in same session** → re-match the route above; "where is X" and "what breaks if I change X" are different routes. Re-read the rule only if the route changed or context was compacted.
- **Both tools available + non-trivial question** → expect to use both; one tool rarely finishes a where/how/who/impact question.

## Red Flags — STOP

- About to report **"X has no callers" / "isn't called" / "no handler for Y" / "X doesn't exist"** from one tool → STOP. codegraph is blind to dynamic dispatch (`@SubscribeEvent`/callbacks/reflection) and off-index files; cross-check with fast-context/grep. See `skills/code-recon/references/gotchas.md`.
- Used **one** tool and about to answer a non-trivial where/how/who/impact question → STOP. State why the other half was genuinely unnecessary, or run it.
- Reaching for a **`codegraph_trace`** tool → it doesn't exist; use `codegraph_explore` with spanning symbol names.

Conflicts between loaded project instructions → formal docs in `skills/code-recon/` win. This does not override harness-native skill name precedence.
