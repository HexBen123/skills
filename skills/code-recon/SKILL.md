---
name: code-recon
description: >
  This skill should be used whenever a task requires locating, tracing, or
  understanding code in an existing codebase before reading or editing it —
  any time the instinct is to Grep / Glob / open files at random to find
  "where" something is or "how" it flows. Trigger on requests like
  "这个功能在哪里实现的", "这段逻辑/这个流程是怎么走的", "谁调用了这个方法",
  "改这个函数会影响哪些地方", "这个事件/回调是谁触发的", "帮我理解这个项目",
  "where is X implemented", "how does X work", "what calls X / what breaks if
  I change X", or "find the code that handles X". Activate for any non-trivial
  or unfamiliar codebase where the fast-context (semantic) and/or codegraph
  (structural) MCP tools are available — this skill is when to reach for those
  MCP tools instead of hand-searching, and how to combine them.
primary: true
---

# code-recon

The fast-context (semantic) + codegraph (structural) combined code-intelligence workflow. Use the two MCP tools *together* to locate, trace, and understand code — instead of defaulting to Grep/Glob/Read-around or stopping after one tool.

<always-applicable>

## Always Read

Read this first — it applies to every code-understanding task:
1. `rules/using-the-tools.md` — which tool for which question, how to combine them, the handoff contract, and when NOT to tool at all

## Session Discipline

- **Re-match the route every task.** A new question in the same session may need a different route than the last one — a "where is X" lookup and a "what breaks if I change X" impact check are different routes.
- **Re-read the rule only when the route changed or context was compacted** (a fresh SKILL.md injection from the SessionStart hook is the signal). Otherwise it's still in context.
- **A single tool's empty/negative result is a hypothesis, not a verdict** — see Known Gotchas before concluding "X has no callers / doesn't exist."

</always-applicable>

<task-routing>

## Common Tasks

Every route reads the same one rule (`rules/using-the-tools.md`) and runs the matching section of one playbook:

| Task | Read | Workflow |
|------|------|----------|
| Explore unfamiliar code / "where is X" / natural-language intent, no symbol name yet (探索/这个功能在哪) | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §A |
| Trace a flow / "how does X work" / "who triggers this event/callback" (追流程/怎么跑的/谁触发) | `rules/using-the-tools.md`; ref `references/gotchas.md` | `workflows/recon-playbook.md` §B |
| Find callers / impact / "what breaks if I change X" (谁调用/改动影响面) | `rules/using-the-tools.md`; ref `references/gotchas.md` | `workflows/recon-playbook.md` §C |
| Known-symbol lookup / "get me the source/signature of X" (已知符号取源码/签名) | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §D |
| Other / unlisted (其他) | `rules/using-the-tools.md` | match the closest `workflows/recon-playbook.md` section; else follow the matrix in `rules/using-the-tools.md` |

</task-routing>

## Known Gotchas

One-liners; full detail + verified evidence in `references/gotchas.md`.

- codegraph misses **dynamic-dispatch inbound edges** — `@SubscribeEvent` / events / callbacks / reflection show "No callers" though live → `references/gotchas.md#dynamic-dispatch-callers`
- codegraph only sees its **index** — patch / generated / vendored / out-of-index code is invisible; fast-context covers it → `references/gotchas.md#index-scope`
- **There is no `codegraph_trace`** — for a flow/path, use `codegraph_explore` naming the spanning symbols → `references/gotchas.md#no-trace-tool`
- fast-context **grep-expansion adds noise** (`[grep expanded]` ≠ AI hit) and `tree_depth` auto-downgrades on big repos → `references/gotchas.md#fast-context-noise`
- codegraph **drifts when concept ≠ naming** (same-named-but-unrelated symbols) → `references/gotchas.md#concept-vs-naming`

## Core Principles

1. **Route understanding through the tools, not hand-search.** Any non-trivial "where/how/who/impact" question on an existing codebase goes through fast-context + codegraph first, not Grep/Glob/Read-around.
   ✓ Check: before answering, did you call at least one of the two MCP tools? Answering a where/how/who question from only Grep+Read means you skipped this skill.
2. **Recon before precision; both before answering.** Lead with fast-context when you lack exact symbol names; switch to codegraph the moment you have one. Most non-trivial questions need both halves.
   ✓ Check: can you name the symbol fast-context surfaced AND the codegraph call that confirmed its structure? Used only one? Justify why the other half was genuinely unnecessary — don't just skip it.
3. **A tool's "nothing found" is a hypothesis.** codegraph "No callers"/"not found" may be a dynamic-dispatch or out-of-index blind spot; cross-check before concluding.
   ✓ Check: when a tool returned empty/negative, did you verify with the other tool (or grep) before stating it as fact?
4. **Don't re-Read what a tool already printed.** `codegraph_explore` and fast-context (`include_code_snippets:true`) return verbatim source — treat them as Reads already done.
   ✓ Check: did you Read a file whose body a tool already returned this task? That Read was wasted.

## Rule Priority
1. `SKILL.md` (this file) → 2. `rules/` → 3. `workflows/` → 4. `references/` → 5. thin shells (`shells/*`, compatibility only)

## Scope
- **Owns:** when/how to drive fast-context + codegraph for code understanding; the combine discipline; the verified pitfalls of each tool.
- **Does NOT own:** the codebase's own rules/conventions (that's a project skill); writing/editing code; running builds/tests. This skill ends when you understand the code well enough to act.
