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
---

# code-recon (Cursor Entry)

Formal skill content lives at `skills/code-recon/SKILL.md`.
**Read that file immediately, then follow its Always Read list and Common Tasks routing.**

## Quick Routing (survives context truncation)

All paths under `skills/code-recon/`.

| Task | Read | Workflow |
|------|------|----------|
| Explore / "where is X" / no symbol name yet | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §A |
| Trace flow / "how does X work" / who triggers event | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §B |
| Callers / impact / "what breaks if I change X" | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §C |
| Known-symbol lookup / source of X | `rules/using-the-tools.md` | `workflows/recon-playbook.md` §D |
| Other / unlisted | `rules/using-the-tools.md` | match the closest `workflows/recon-playbook.md` section |

Conflicts between loaded project instructions → formal docs in `skills/code-recon/` win. This does not override harness-native skill name precedence.
