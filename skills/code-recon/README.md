# code-recon

**The fast-context + codegraph combined code-intelligence skill.** It exists to fix one observed problem: in real sessions agents rarely reach for these two MCP tools, and almost never combine them — they default to Grep/Glob/Read or stop after a single tool call. This skill makes the combo the routed default for any "where / how / who / impact" question on a codebase.

- **fast-context** (`mcp__fast-context__fast_context_search`) — semantic net: natural-language → file paths + line ranges + grep keywords; sees the whole filesystem (incl. off-index files).
- **codegraph** (`mcp__codegraph__codegraph_*`) — structural authority: exact location/source/edges/impact from a pre-built index; instant, offline, zero quota, but only static edges over indexed files.

They are complementary. Most non-trivial questions need a handoff between them.

## What's here

```
code-recon/
├── SKILL.md                     router: description (trigger) + Always Read + Common Tasks + gotchas + principles
├── rules/
│   └── using-the-tools.md       selection matrix + combine discipline + handoff + when NOT to tool (Always Read)
├── workflows/
│   └── recon-playbook.md        one flow (recon→precision→cross-check), 4 sections §A–§D each with a checklist
├── references/
│   ├── gotchas.md                5 VERIFIED pitfalls (Symptom/Cause/Fix/Prevent + NeoForge evidence)
│   ├── tool-reference.md         exact params + observed output shapes of both tools
│   └── worked-example.md         real end-to-end NeoForge run (the evidence behind the gotchas)
├── shells/                      thin shells: CLAUDE/AGENTS/CODEX/GEMINI + .cursor (rule + registration)
├── hooks/                       SessionStart re-injection (Claude Code + Cursor)
├── scripts/smoke-test.sh        automated structural self-check
└── INSTALL.md                   per-harness install (global + per-project)
```

## How it maps to the skill-based-architecture tutorial

- **结构服务于内容** (ch.1–2): this is a focused single-domain tool skill, so the project-skill scaffolding (`fix-bug`, `agent-behavior.md`, etc.) was *dropped*, not copied. Only the parts that carry content for *this* domain remain.
- **Description = trigger** (ch.4–5): the `description` is the load-bearing piece — broad code-understanding intent phrases in EN + ZH, WHEN only (no workflow HOW that would suppress the body).
- **薄壳 + 内联路由表** (ch.6): each harness shell inlines the 4-route table + Auto-Triggers + Red Flags so they survive context compression. The Red Flags are re-targeted at *this* skill's failure ("about to Grep instead of routing"; "about to trust a 'No callers'").
- **SessionStart hook** (ch.7): re-injects SKILL.md on clear/compact.
- **激活优于存储** (ch.10): every gotcha appears on a task path — one-liner in SKILL.md Known Gotchas + a workflow completion-checklist item — not just stored in `references/`.
- **内容禁止预制 / gotchas 来自真实运行** (ch.10, 15): every gotcha and the worked example come from a **real run against NeoForge**, not invention. The old prompt's non-existent `codegraph_trace` was corrected against the real tool schemas.
- **Harness 做质检** (ch.4, 16): `smoke-test.sh` checks structure, budgets, placeholder residue, routing/​anchor resolution, description consistency, and shell routing — the 80% of failures that are "forgetting", not "misunderstanding".

## Maintenance

- **Add a gotcha** only after a real run surfaces it and it passes 2/3 (repeatable + costly + not obvious): add the Symptom/Cause/Fix/Prevent block to `references/gotchas.md`, a one-liner + anchor to SKILL.md Known Gotchas, and a checklist line to the relevant workflow. Storing without activating doesn't count.
- **After editing SKILL.md, a shell, or the description** → run `bash scripts/smoke-test.sh`.
- **Don't** turn `references/` into a session log — generalized, reusable lessons only (tutorial ch.17).
