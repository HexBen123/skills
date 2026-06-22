# Gotchas — fast-context + codegraph

Verified pitfalls of the two tools. Each passed the recording threshold (repeatable + costly + not obvious from a tool's own docs) and is *activated* — referenced from a workflow's completion checklist, not just stored here.

Format: **Symptom / Cause / Fix / Prevent**. `[topic]` tags cluster related entries.

---

<a id="dynamic-dispatch-callers"></a>
## **[dynamic-dispatch]** codegraph shows "No callers" for dynamically-invoked methods

**Symptom:** `codegraph_callers(X)` returns "No callers found" (or only import sites), yet X is clearly invoked at runtime — it's an event handler, callback, listener, or reflectively-called method.

**Cause:** codegraph's graph records **static** call edges. An invocation through an event bus, reflection, an annotation dispatcher (`@SubscribeEvent`, `@EventHandler`), or a registered functional callback has no static edge from caller to callee, so the inbound edge is missing. Outbound edges from the same method resolve fine — the blind spot is specifically **dynamic INBOUND**.

**Fix:** treat the empty result as a hypothesis. Find the *trigger* instead of the *caller*: hand to fast-context — "where is `<EventType>` posted / fired / dispatched" — or grep the event/symbol name. The real invoker is the post/dispatch site, not a static caller.

**Prevent:** `workflows/recon-playbook.md` §C classifies the symbol as static-vs-dynamic before trusting an empty result, and mandates the fast-context cross-check.

**Verified (NeoForge):**
- `codegraph_callers builtinMobSpawnBlocker` → **No callers found** — it's a live `@SubscribeEvent` handler.
- `codegraph_callees builtinMobSpawnBlocker` → **4 found** (outbound resolves).
- `codegraph_callers wasReleaseHandled` → **1 found** `getReleaseResult` (a normal static call resolves).

---

<a id="index-scope"></a>
## **[index]** codegraph only sees what it indexed — off-index code is invisible

**Symptom:** A symbol/caller/definition you *know* exists doesn't appear in any codegraph result, even with the right name.

**Cause:** codegraph answers only from its `.codegraph/` index (a fixed set of source files — e.g. on NeoForge, ~1517 `.java` plus a few yaml/xml/properties). Anything outside that set — patch/diff files, generated sources, vendored dependencies, build outputs, other languages — was never indexed and cannot appear.

**Fix:** for anything that might live off-index, use fast-context (live filesystem search) or grep. Run `codegraph_status` if unsure what's even indexed.

**Prevent:** `rules/using-the-tools.md` lists "answer may live outside the index" as a fast-context trigger; `workflows/recon-playbook.md` §B step 4 recovers off-index hops.

**Verified (NeoForge):** `codegraph_callers EntityJoinLevelEvent` found handlers + imports but **not** the event's fire site — it lives in `patches/net/minecraft/server/level/ServerLevel.java.patch`, an unindexed patch file. fast-context's query "where is EntityJoinLevelEvent posted" returned exactly those `.patch` fire sites.

---

<a id="no-trace-tool"></a>
## **[api]** there is no `codegraph_trace` — use `codegraph_explore` for paths

**Symptom:** You reach for a "trace" tool to get an A→B path and there isn't one. (The older fast-context/codegraph prompt referenced `trace`; it never existed.)

**Cause:** the codegraph tool set is exactly: `explore`, `search`, `node`, `callers`, `callees`, `impact`, `files`, `status`. Path/flow questions are answered by `explore`, not a dedicated trace call.

**Fix:** call `codegraph_explore(query="<symbol A> <symbol B> <symbols between>")` — it returns the relationship graph and verbatim source spanning those symbols, surfacing the path (including some dynamic hops) among them.

**Prevent:** `workflows/recon-playbook.md` §B is built on `explore`-with-spanning-names and states the no-trace fact up front.

---

<a id="fast-context-noise"></a>
## **[noise]** fast-context grep-expansion adds noise; `tree_depth` auto-downgrades on big repos

**Symptom:** fast-context returns some off-target files; and the map it reasons over is shallower than you asked for on a large repo.

**Cause:** results are two kinds — genuine **AI-search hits** and **grep keyword-expansion** hits (tagged `[grep expanded]` / `(grep match)`). Expansion catches anything matching a keyword (random files with "event" in the name, `.md`/`.lang`/`.json` docs). Separately, `tree_depth` is auto-capped when the repo map would be too large.

**Fix:** trust AI-search hits over `[grep expanded]` ones; pass `exclude_paths=['**/*.lang','**/*.json','**/*.properties','**/assets/**','**/*.md']` to cut resource/translation/doc noise. Read the `[config]` line to see the *actual* params used.

**Prevent:** `workflows/recon-playbook.md` §A step 1 sets lightweight mode + exclude_paths and reads hits by tag.

**Verified (NeoForge):** querying the 1529-file repo, `[config]` reported `tree_depth=1` despite the default request of 3 (auto-downgrade); and "grep expanded" hits included an off-target `docs/TESTFRAMEWORK.md`. On big repos, compensate with a more specific query or higher `max_turns` — not by cranking `tree_depth` (it'll be capped anyway).

---

<a id="concept-vs-naming"></a>
## **[naming]** codegraph `explore` drifts when the concept ≠ the symbol naming

**Symptom:** `codegraph_explore`/`search` returns plausible-looking but wrong symbols — same name, unrelated meaning (e.g. asking about GUI scaling and getting pulled toward `GenLayer*Zoom`).

**Cause:** codegraph matches on names/structure. When the concept you're chasing isn't expressed in the symbol names, structural matching latches onto same-named-but-unrelated code.

**Fix:** when concept ≠ naming, lead with **fast-context** (semantic) to find the real symbols, *then* hand the confirmed names back to codegraph. The reverse case — concept = naming (e.g. `fellowship invite` → `LOTRPacketFellowshipInvitePlayer`) — is exactly where codegraph `explore` shines; lead with it there.

**Prevent:** `rules/using-the-tools.md` "one-line decision" keys the lead tool on concept↔naming alignment; `workflows/recon-playbook.md` §A step 4 routes back to fast-context on drift.
