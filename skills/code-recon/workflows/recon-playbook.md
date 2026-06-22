# Recon Playbook

Four variants of one flow — **recon → precision → cross-check**. Pick the section matching your question. All assume `rules/using-the-tools.md` is read. Pass the target repo's absolute path to every tool call.

**Pre-step (every section):** re-match the route (a "where is X" and a "what breaks if I change X" are different sections). Re-read `rules/using-the-tools.md` only if the route changed or context was compacted.

---

## §A — Explore unknown code

*For: natural-language intent, no symbol name yet — "where is X", "这个功能在哪里", orienting in an unfamiliar/large repo.*

1. **Cast the net — fast-context, lightweight.** `fast_context_search(project_path=<abs>, query="<intent>", max_turns=2, include_code_snippets=false, max_results=8)`; on noisy repos add `exclude_paths=['**/*.lang','**/*.json','**/*.properties','**/assets/**']`. Read **AI-search hits = signal**, `[grep expanded]` = weaker; keep the returned grep keywords.
2. **Lock onto a symbol.** Pick the hit matching the intent. Nothing matches? Re-query with a returned keyword or rephrase — don't fall back to blind Grep.
3. **Hand off — codegraph.** `codegraph_explore(query="<symbols found>")` for area+relationships, or `codegraph_node(symbol=..., includeCode=true)` for one full body.
4. **Confirm or widen.** Drifted to same-named-but-unrelated symbols (concept ≠ naming)? Back to fast-context. Need callers/impact → §C. Need end-to-end flow → §B.

Checklist: [ ] fast-context ran lightweight first · [ ] ≥1 codegraph call confirmed structure · [ ] empty/negative cross-checked · [ ] no re-Read of printed source · [ ] answer names which tool gave "where" vs "what/how".

---

## §B — Trace a flow

*For: "how does X work", "这个流程怎么走的", "how does X reach Y", "who triggers this event/callback".*

**No `codegraph_trace` exists** — trace with `codegraph_explore` named with the spanning symbols (`gotchas.md#no-trace-tool`).

1. **Get endpoints.** Know the spanning symbols? skip to 2. Else fast-context net (`max_turns=2`) for the flow's entry/exit symbol names.
2. **Trace structurally.** `codegraph_explore(query="EntrySymbol MidSymbol ExitSymbol")` — read the **Relationships** block for the static path, **Source** for bodies; `codegraph_node(includeCode=true)` for one hop's full body.
3. **Step direction-correctly.** `codegraph_callees` = forward (what it calls); `codegraph_callers` = backward — but see step 4 for the backward blind spot.
4. **Recover dynamic hops (common break).** Chain dead-ends at an event post / callback / registration / `@SubscribeEvent`? Hand to fast-context: "where is `<EventType>` posted / fired / dispatched" (`gotchas.md#dynamic-dispatch-callers`, `#index-scope`).
5. **Assemble.** Write the chain hop-by-hop, marking each static (codegraph) or dynamic (fast-context). An unexplained gap at an event/callback = incomplete.

Checklist: [ ] explore-with-spanning-names (not a trace tool) · [ ] each hop attributed to a tool · [ ] dynamic gaps recovered, not left as "no caller" · [ ] no re-Read of printed source.

---

## §C — Find callers / impact

*For: "who calls this", "谁调用了这个方法", "what breaks if I change X", refactor blast-radius.*

**Strength + trap:** codegraph is authoritative for *static* edges/impact but **blind to dynamic-dispatch inbound edges** — an event/callback/reflection-invoked method shows "No callers" while live. So this section always cross-checks.

1. **Ask codegraph.** `codegraph_callers(symbol=...)` / `codegraph_callees(symbol=...)` / `codegraph_impact(symbol=..., depth=2)`. Overloaded name → `codegraph_node(symbol=..., file=..., line=...)`.
2. **Classify before trusting empty.** Event handler / callback / listener / reflectively-invoked / annotated entry (`@SubscribeEvent`, DI-wired)? Then "No callers" is *expected and wrong* — the real invoker is dynamic.
3. **Cross-check (mandatory when empty/negative or symbol is dynamic).** fast-context: "where is `<symbol or its event type>` called / fired / registered". codegraph also can't see callers in off-index files (patches/generated/vendored).
4. **Reconcile.** Final set = codegraph's static edges **+** dynamic/off-index invokers fast-context found; report both, labeled.

**Verified (NeoForge):** `callers(builtinMobSpawnBlocker)` → **No callers** (live `@SubscribeEvent`); `callees(builtinMobSpawnBlocker)` → 4 (outbound resolves); `callers(wasReleaseHandled)` → 1 (static resolves). Blind spot = dynamic *inbound* only. See `gotchas.md#dynamic-dispatch-callers`.

Checklist: [ ] codegraph callers/callees/impact ran with correct projectPath · [ ] symbol classified static vs dynamic before trusting empty · [ ] empty/dynamic results cross-checked with fast-context · [ ] answer separates static (codegraph) from dynamic/off-index (fast-context).

---

## §D — Known-symbol lookup

*For: you already have an exact name and want its source/signature — "show me `FooService.handle`", "这个类怎么实现的".*

1. **Straight to codegraph.** One symbol full body: `codegraph_node(symbol=..., includeCode=true)` (overloaded → pin `file`/`line`). Neighborhood: `codegraph_explore(query="<symbol> <related>")`. Just location: `codegraph_search`.
2. **Treat output as a Read** — don't re-`Read` files it printed.
3. **Fall back only if needed.** `search` finds nothing but you're sure of the name → likely **off-index** (generated/patch/vendored) → fast-context. Huge file, specific deep region → fast-context `include_code_snippets=true`.
4. **Guessed the name?** You're in the wrong section → §A (fast-context first).

Checklist: [ ] codegraph led · [ ] overloads disambiguated via `file`/`line` · [ ] no re-Read of printed source · [ ] off-index/huge-file cases fell back to fast-context, not guessing.
