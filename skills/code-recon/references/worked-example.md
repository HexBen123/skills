# Worked Example — fast-context + codegraph on NeoForge

A real end-to-end run against `NeoForge` (a 1529-file Java/Minecraft modding framework, codegraph-indexed). Every output below is verbatim from an actual session — this is the evidence behind `references/gotchas.md`. It shows the combo *and* the recovery from codegraph's blind spots.

**Question:** "How are events fired on the event bus and dispatched to `@SubscribeEvent` handlers, and what triggers a given handler?"

## 1. Cast the net — fast-context (lightweight)

```
fast_context_search(project_path=.../NeoForge,
  query="how does the event bus post events and dispatch them to @SubscribeEvent listener methods",
  max_turns=2, include_code_snippets=false, max_results=8)
```
Returned `8 files (3 from AI search, 5 from grep keyword expansion)`. The **3 AI hits** were the signal:
`NeoForge.java`, `event/EventHooks.java`, `common/NeoForgeEventHandler.java`. The 5 `[grep expanded]` hits (`SelectMusicEvent`, `AddSectionGeometryEvent`, …) were keyword noise. It also returned reusable `grep keywords: SubscribeEvent, post.*event, event.*dispatch, …` and `[config] … tree_depth=1 …` — note the auto-downgrade from the default 3 (gotcha `#fast-context-noise`).

## 2. Confirm structure — codegraph_explore

```
codegraph_explore(query="event bus post @SubscribeEvent listener dispatch register", projectPath=.../NeoForge)
```
Returned `202 symbols across 68 files`: a Relationships graph (event class hierarchies `Post → PistonEvent`, etc.) **plus verbatim source**, including `NetworkInitialization.register` annotated `@SubscribeEvent` — the exact registration shape fast-context pointed at, now with authoritative source. (No need to `Read` those files — explore already printed them.)

## 3. Test "who triggers handler X" — the blind spot

Picked a uniquely-named live handler and asked codegraph for its callers:
```
codegraph_callers(builtinMobSpawnBlocker)        → "No callers found"
codegraph_callers(logTransformationsOnGameShutdown) → "No callers found"
```
Both are active `@SubscribeEvent` handlers. Contrast proves it's a *dynamic-inbound* blind spot, not a broken index:
```
codegraph_callees(builtinMobSpawnBlocker) → 4 found   (outbound static edges resolve)
codegraph_callers(wasReleaseHandled)      → 1 found    (getReleaseResult — a normal static call resolves)
```
→ gotcha `#dynamic-dispatch-callers`. **A "No callers" here is not "nothing calls it."**

## 4. Recover the trigger — back to fast-context

The handler fires when `EntityJoinLevelEvent` is posted. codegraph couldn't reach the fire site:
```
codegraph_callers(EntityJoinLevelEvent) → 5 results: handler methods + import namespaces, but NOT the fire site
```
fast-context found it immediately:
```
fast_context_search(query="where is EntityJoinLevelEvent posted or fired to the event bus")
  → patches/net/minecraft/server/level/ServerLevel.java.patch (L140-150)   ← the actual fire site
  → patches/net/minecraft/client/multiplayer/ClientLevel.java.patch
```
The fire site lives in a **patch file** outside codegraph's `.java` index → gotcha `#index-scope`. Only fast-context's live search reached it.

## The takeaway

Neither tool answered the whole question alone:
- **fast-context** found the entry files and (later) the off-index fire site — but no authoritative structure.
- **codegraph** gave exact source + static edges — but went silent at the dynamic dispatch and the patch file.

The answer required the **handoff in both directions** (fast-context → codegraph for structure, codegraph → fast-context to recover the dynamic/off-index hops). That is the entire point of this skill.
