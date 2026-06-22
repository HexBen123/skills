# Install — code-recon

A portable, cross-project skill: the fast-context + codegraph combined code-intelligence workflow. Pick the harness(es) you use. Paths inside the shells assume `skills/code-recon/` resolves from the agent's working dir — see **Path note** for a global Claude Code install.

After any install, verify: `bash skills/code-recon/scripts/smoke-test.sh`

## Claude Code — global (recommended for a cross-project tool skill)

Claude Code auto-discovers `~/.claude/skills/*/SKILL.md` by its `description`, so a global copy activates everywhere from the trigger phrases alone.

```bash
cp -R skills/code-recon ~/.claude/skills/code-recon

# (Optional but recommended) re-inject the router on clear/compact:
mkdir -p ~/.claude/hooks
cp ~/.claude/skills/code-recon/hooks/session-start ~/.claude/hooks/session-start
chmod +x ~/.claude/hooks/session-start
# Then merge hooks/hooks.json's top-level "hooks" object into ~/.claude/settings.json,
# changing the command to: bash ~/.claude/hooks/session-start
```

The hook auto-detects `~/.claude/skills/code-recon/SKILL.md`. To also keep the inlined routing table alive in long sessions, paste the body of `shells/CLAUDE.md` into your global `~/.claude/CLAUDE.md` and rewrite its `skills/code-recon/...` paths to `~/.claude/skills/code-recon/...` (see Path note).

## Claude Code — per-project

```bash
cp -R skills/code-recon <project>/skills/code-recon
cp skills/code-recon/shells/CLAUDE.md <project>/CLAUDE.md        # or merge into an existing one
mkdir -p <project>/.claude/hooks
cp skills/code-recon/hooks/session-start <project>/.claude/hooks/ && chmod +x <project>/.claude/hooks/session-start
cp skills/code-recon/hooks/hooks.json <project>/.claude/settings.json   # or merge the "hooks" object
```

## Cursor — per-project

```bash
cp -R skills/code-recon <project>/skills/code-recon
cp -R skills/code-recon/shells/.cursor <project>/.cursor          # rule + registration entry
# (Optional) re-injection hook:
mkdir -p <project>/.cursor/hooks
cp skills/code-recon/hooks/session-start <project>/.cursor/hooks/ && chmod +x <project>/.cursor/hooks/session-start
cp skills/code-recon/hooks/hooks-cursor.json <project>/.cursor/hooks.json
```

The Cursor registration entry (`.cursor/skills/code-recon/SKILL.md`) carries a `description` byte-identical to the main SKILL.md — smoke-test enforces this. Don't edit one without the other.

## Codex / Gemini — per-project

```bash
cp -R skills/code-recon <project>/skills/code-recon
cp skills/code-recon/shells/CODEX.md  <project>/CODEX.md          # Codex
cp skills/code-recon/shells/AGENTS.md <project>/AGENTS.md         # Codex (and other AGENTS.md-aware tools)
cp skills/code-recon/shells/GEMINI.md <project>/GEMINI.md         # Gemini
```

## Path note (global installs)

The shells use project-relative paths (`skills/code-recon/...`). For a global Claude Code install, either (a) keep the skill per-project so those paths resolve, or (b) when pasting a shell into `~/.claude/CLAUDE.md`, rewrite the paths to `~/.claude/skills/code-recon/...`. The SessionStart hook already checks all three locations, so re-injection works without edits.

## Preconditions & graceful degradation

- **codegraph** needs the target repo indexed (`.codegraph/` present). If a call errors or is empty, run `codegraph_status`; if unindexed, the skill falls back to fast-context + grep (documented in `rules/using-the-tools.md`).
- **fast-context** needs network + remote quota. If unavailable, codegraph + grep still answer structural questions.
- Only one of the two tools available? The skill still helps — it just runs the degraded single-tool path and says so.

## Hook caveats (from the upstream 踩坑清单)

- This skill ships **only a SessionStart hook** (re-injection). The schema in `hooks.json` is the nested `hooks:[{type,command}]` form required by Claude Code CLI v2.1+.
- Verify a hook actually fires in a **real interactive** Claude Code/Cursor session — subagent/headless sessions may not trigger hooks.
- Hooks help low- and mid-tier models less; on weak models the description + inlined shell routing carry more of the load. Prefer Sonnet-class or above for the combo to fire reliably.
