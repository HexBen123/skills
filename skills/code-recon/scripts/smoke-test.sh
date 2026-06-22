#!/usr/bin/env bash
# smoke-test.sh — automated structural self-check for the code-recon skill.
# Usage: bash <skill-dir>/scripts/smoke-test.sh
# Single source of truth = SKILL.md (no routing.yaml). Exit 0 = pass, 1 = failures.
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SKILL_DIR"

PASS=0; FAIL=0; WARN=0
ok()   { PASS=$((PASS+1)); }
fail() { FAIL=$((FAIL+1)); printf '  ✗ %s\n' "$1"; }
warn() { WARN=$((WARN+1)); printf '  ! %s\n' "$1"; }

echo "== code-recon smoke-test =="
echo "skill dir: $SKILL_DIR"

# ── 1. Structural: required files exist ────────────────────────────────
echo "[1] structure"
REQUIRED=(
  SKILL.md INSTALL.md README.md
  rules/using-the-tools.md
  workflows/recon-playbook.md
  references/gotchas.md references/tool-reference.md references/worked-example.md
  shells/CLAUDE.md shells/AGENTS.md shells/CODEX.md shells/GEMINI.md
  shells/.cursor/rules/code-recon.mdc
  shells/.cursor/skills/code-recon/SKILL.md
  hooks/session-start hooks/hooks.json hooks/hooks-cursor.json
  scripts/smoke-test.sh
)
for f in "${REQUIRED[@]}"; do
  [[ -f "$f" ]] && ok || fail "missing file: $f"
done

# ── 2. Placeholder residue (this is a produced skill, not a template) ──
echo "[2] no placeholder residue"
RESIDUE=$(grep -rIl -e '{{NAME}}' -e '{{SUMMARY}}' -e 'FILL:' . 2>/dev/null | grep -v 'scripts/smoke-test.sh' || true)
if [[ -n "$RESIDUE" ]]; then
  while read -r r; do [[ -n "$r" ]] && fail "placeholder residue in: $r"; done <<< "$RESIDUE"
else ok; fi

# ── 3. SKILL.md dual budget: description ≤25, body ≤90 ─────────────────
echo "[3] SKILL.md line budgets"
DESC_LINES=$(awk 'BEGIN{f=0} /^description:/{f=1} f && /^[^[:space:]]/ && !/^description:/{exit} f{c++} END{print c+0}' SKILL.md)
BODY_LINES=$(awk 'BEGIN{d=0} /^---[[:space:]]*$/{d++; next} d>=2{c++} END{print c+0}' SKILL.md)
[[ "${DESC_LINES:-0}" -le 25 ]] && ok || fail "SKILL.md description $DESC_LINES lines (>25)"
[[ "${BODY_LINES:-0}" -le 90 ]] && ok || warn "SKILL.md body $BODY_LINES lines (>90)"

# ── 4. Shell budgets ≤60 lines; gotchas ≤400 ──────────────────────────
echo "[4] shell + gotchas budgets"
for s in shells/CLAUDE.md shells/AGENTS.md shells/CODEX.md shells/GEMINI.md shells/.cursor/rules/code-recon.mdc; do
  n=$(wc -l < "$s" 2>/dev/null | tr -d ' ')
  [[ "${n:-0}" -le 60 ]] && ok || fail "$s is $n lines (>60)"
done
g=$(wc -l < references/gotchas.md | tr -d ' ')
[[ "${g:-0}" -le 400 ]] && ok || fail "gotchas.md is $g lines (>400)"

# ── 5. Description quality: ≥40 CJK chars or ≥20 words; ≥2 quoted phrases
echo "[5] description quality"
DESC=$(awk 'BEGIN{f=0} /^description:/{f=1; next} f && /^[^[:space:]]/{f=0} f{print}' SKILL.md)
CJK=$(printf '%s' "$DESC" | grep -oE '[一-龥]' 2>/dev/null | wc -l | tr -d ' ')
WORDS=$(printf '%s' "$DESC" | wc -w | tr -d ' ')
{ [[ "${CJK:-0}" -ge 40 ]] || [[ "${WORDS:-0}" -ge 20 ]]; } && ok || fail "description too short (cjk=$CJK words=$WORDS)"
QUOTES=$(printf '%s' "$DESC" | grep -oE '"[^"]+"' 2>/dev/null | wc -l | tr -d ' ')
[[ "${QUOTES:-0}" -ge 2 ]] && ok || fail "description has $QUOTES quoted trigger phrases (<2)"
[[ "${QUOTES:-0}" -le 14 ]] && ok || warn "description has $QUOTES quoted phrases (>14: keyword-stuffing risk)"

# ── 6. Description byte-equality: SKILL.md vs Cursor entry ─────────────
echo "[6] description consistency (SKILL.md == Cursor entry)"
norm() { awk 'BEGIN{f=0} /^description:/{f=1; next} f && /^[^[:space:]]/{f=0} f{print}' "$1" | sed 's/[[:space:]]*$//'; }
if diff <(norm SKILL.md) <(norm shells/.cursor/skills/code-recon/SKILL.md) >/dev/null 2>&1; then ok
else fail "Cursor entry description differs from SKILL.md (drift = randomized activation)"; fi

# ── 7. Routing completeness: every file referenced in SKILL.md exists ──
echo "[7] routing completeness (Common Tasks references resolve)"
REFS=$(grep -oE '(rules|workflows|references)/[A-Za-z0-9_-]+\.md' SKILL.md | sort -u || true)
while read -r ref; do
  [[ -z "$ref" ]] && continue
  [[ -f "$ref" ]] && ok || fail "SKILL.md references missing file: $ref"
done <<< "$REFS"

# ── 8. Gotcha anchors referenced in SKILL.md exist in gotchas.md ──────
echo "[8] gotcha anchors resolve"
ANCHORS=$(grep -oE 'gotchas\.md#[a-z-]+' SKILL.md | sed 's/.*#//' | sort -u || true)
while read -r a; do
  [[ -z "$a" ]] && continue
  grep -q "id=\"$a\"" references/gotchas.md && ok || fail "anchor #$a not found in gotchas.md"
done <<< "$ANCHORS"

# ── 9. Shell routing consistency: each shell points at the playbook ───
echo "[9] shell routing consistency"
for s in shells/CLAUDE.md shells/AGENTS.md shells/CODEX.md shells/GEMINI.md; do
  if grep -q 'workflows/recon-playbook.md' "$s"; then ok
  else fail "$s missing route workflows/recon-playbook.md"; fi
  grep -q 'rules/using-the-tools.md' "$s" && ok || fail "$s missing Always Read rules/using-the-tools.md"
done

# ── 10. Broken relative .md links across the skill ────────────────────
echo "[10] no broken relative markdown links"
BROKEN=0
while read -r md; do
  base=$(dirname "$md")
  while read -r link; do
    [[ -z "$link" ]] && continue
    target="${link%%#*}"; [[ -z "$target" ]] && continue
    case "$target" in http*|/*) continue;; esac
    [[ -f "$base/$target" ]] || { fail "broken link in $md -> $target"; BROKEN=1; }
  done < <(grep -oE '\]\([^)]+\.md[^)]*\)' "$md" | sed -E 's/^\]\(//; s/\)$//' || true)
done < <(find . -name '*.md' -not -path './scripts/*')
[[ "$BROKEN" -eq 0 ]] && ok

# ── 11. Legacy pre-merge files should be gone (advisory) ──────────────
echo "[11] no legacy pre-merge files"
LEGACY=(rules/tool-selection.md rules/combination-protocol.md \
        workflows/explore-unknown.md workflows/trace-flow.md \
        workflows/find-callers-impact.md workflows/known-symbol-lookup.md)
leg=0
for f in "${LEGACY[@]}"; do [[ -f "$f" ]] && { warn "legacy file still present (delete it): $f"; leg=1; }; done
[[ "$leg" -eq 0 ]] && ok

# ── Summary ───────────────────────────────────────────────────────────
echo "── summary: $PASS pass, $WARN warn, $FAIL fail ──"
[[ "$FAIL" -eq 0 ]] && { echo "OK"; exit 0; } || { echo "FAILURES PRESENT"; exit 1; }
