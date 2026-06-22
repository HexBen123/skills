# Using the Tools — selection + combination

How to drive fast-context + codegraph: which tool for which question, how to hand off between them, and when not to tool at all. Tool names/params below are the real MCP signatures — use them verbatim. The two tools are complementary; most non-trivial questions touch both.

## fast-context — the semantic net (`mcp__fast-context__fast_context_search`)

An AI (Windsurf Devstral) reads a repo map + greps, returning **file paths + line ranges + reusable grep keywords**. Live filesystem — it sees *everything on disk*, including off-index files.

Lead with it when:
- **Natural-language intent but no symbol name** ("where is auth handled", "怎么做存档同步").
- The concept is **diffuse** / doesn't line up with one symbol name.
- The target is **dynamic-dispatch glue** — callbacks, events, `@SubscribeEvent`, `onMessage`, `new Thread`, reflection (the wiring codegraph's static graph can't follow).
- You need a **"where do I even look" map**, or a precise slice deep in a large file.
- The answer may live **outside codegraph's index** — patch files, generated code, configs, vendored deps.

Params: `project_path` (absolute, required) · `query` · `max_turns` (1 quick / 2 focused / 4–5 end-to-end) · `include_code_snippets` (false = paths+keywords ~2–5KB, default; true = full snippets ~45KB) · `max_results` · `exclude_paths` (e.g. `['**/*.lang','**/*.json','**/*.properties','**/assets/**','**/*.md']`).

## codegraph — the structural authority (`mcp__codegraph__codegraph_*`)

Pre-built SQLite graph of indexed source. Exact-to-the-line, zero-noise, instant, offline, reproducible, no quota. But only **static** edges over **indexed** files.

Lead with it when:
- You **already have a symbol name** → its location / signature / verbatim source / edges.
- You need **callers / callees / impact** (refactor blast radius) — for *static* edges.
- You want the **flow/path among several known symbols**.
- The **concept matches the naming** (`fellowship invite` → `LOTRPacketFellowshipInvitePlayer`) — explore lands directly.
- You need an answer **now, offline, reproducibly**, no quota.

Tool map (these are all of them): `codegraph_explore` (**PRIMARY** — NL question or bag of names → relationship graph + verbatim source) · `codegraph_search` (locate by name) · `codegraph_node` (one symbol full; `file`/`line` disambiguates overloads) · `codegraph_callers` / `codegraph_callees` (static edges) · `codegraph_impact` (`depth` default 2) · `codegraph_files` · `codegraph_status`. All take `projectPath` (pass the target repo's absolute path when it isn't the current project).
**There is no `codegraph_trace`** — for "the path from X to Y", call `codegraph_explore` with the spanning symbol names (it surfaces the path, including some dynamic hops). The old prompt's "trace" was wrong; this is the fix.

## The one-line decision

> **No name / callback-event-dynamic glue / maybe off-index → fast-context first. Have the name and concept matches it → codegraph first. Then hand off to the other for the half it does better.**

## The combine discipline (the point of this skill)

The common failure is not *misusing* the tools — it's **not reaching for them, or stopping after one**:
- **Default-to-Grep.** The reflex for "where is X" is Grep/Glob + open files. Fine on tiny repos; silently wasteful on large ones, and blind to semantic matches and dynamic glue.
- **Stop-after-one.** codegraph's own description says "usually the only call you need"; fast-context returns a tidy list. Either *feels* complete, so the agent answers from half the picture.
- **Trust-the-null.** A tool returns empty and the agent reports it as fact — when it's a known blind spot (`references/gotchas.md`).

**Handoff contract** (neither tool finishes alone on a non-trivial question):
1. **fast-context → codegraph**: the moment fast-context surfaces a symbol name, hand off for exact source/edges. *Reuse its returned grep keywords.*
2. **codegraph → fast-context**: codegraph empty/negative, or you need where a thing is *fired/registered/configured* (dynamic or off-index), or explore drifted to same-named-but-unrelated symbols → hand back with a natural-language query.
3. **Done** only when you can state the answer *and* name which tool established each half.

## Negative-result cross-check (non-negotiable)

Before reporting "X has no callers / isn't called / no handler for Y / X doesn't exist":
- From **codegraph** → re-ask with **fast-context** or grep (blind to dynamic-dispatch inbound edges + off-index files).
- From **fast-context** → try a different phrasing or a known symbol in **codegraph**.

## When NOT to tool

Skip the combo and just Read/Grep only when **all** hold: the target is **one known file** you can open directly, AND the question is **local** (no callers/flow), AND the repo is **small** or you know the exact location. If any fails, route through the combo. When unsure, lead with fast-context (cheap in lightweight mode), not a blind Grep.

## Efficiency guards

- **Don't re-Read printed source.** `codegraph_explore` and fast-context (`include_code_snippets:true`) return verbatim, line-numbered source — treat as Reads already done.
- **Lightweight first** (`include_code_snippets:false`); set `true` only for a specific deep slice.
- **Narrow then widen** — start `max_turns:1–2`, escalate to `4–5` only for an unresolved end-to-end trace.

✓ Check: state which tool you led with and *why the question's shape* chose it; and point to the two outputs that together justify the answer. Used only one tool on a non-trivial question? Say why the other half was genuinely unnecessary — don't just skip it.
