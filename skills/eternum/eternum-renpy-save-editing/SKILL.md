---
name: eternum-renpy-save-editing
description: Use when editing, verifying, or re-signing Eternum or other Ren'Py .save archives, especially when values live in log instead of json, the game says the save was created on another device, or modified saves do not load because the wrong file path or signature logic was used.
---

# Eternum Ren'Py Save Editing

## Overview

Use this skill to inspect, modify, and re-sign Ren'Py `.save` archives for Eternum.
Prioritize the real save file, patch values in `log`, and re-sign with Ren'Py's default signature flow before assuming the game or the archive is broken.

## Quick Triage

Follow this order before making changes:

1. Confirm the target file is the game's real save under `game\saves`, not a copied backup elsewhere.
2. Close the game completely so it cannot overwrite the edited archive.
3. Confirm the requested value is likely stored in `log`, not in `json`.
4. Confirm `ecdsa` is available and the signing key file exists at `AppData\Roaming\RenPy\tokens\security_keys.txt`.
5. Make a backup before writing anything.

## Workflow

### 1. Confirm The Real Save Path

For the validated local Eternum setup in this workspace, use the live `game\saves` directory documented in `references/renpy-save-reference.md`.

If the user points at a copied `.save` in another directory, treat it as a working copy only. Do not claim success unless that file is copied back or the actual live save target is modified.

### 2. Inspect The Archive Structure

Treat the `.save` file as a ZIP archive.
Expect these entries:

- `log`: authoritative game state, stored as pickle opcodes
- `signatures`: signature metadata the game checks on load
- `json`: lightweight metadata, not the primary place for money, player name, or similar gameplay state

If a request is about values like player name or money, start by inspecting `log`.

### 3. Patch `log`, Not `json`

When editing values:

- Look up the key inside the pickle opcode stream in `log`
- Skip `*INPUT` opcodes after the key until the actual value opcode
- Patch string values by rewriting the relevant unicode opcode payload
- Patch integer values by rewriting the integer opcode payload
- Rebuild the opcode list after each mutation before applying the next one

Common validated fields from this guide:

- `store.mc`
- `store.money`
- `store.nickname`
- `store.lastname`

Use the bundled script for normal edits:

```powershell
python .\scripts\patch_and_resign_save.py `
  --save '<live-save-path>\24-3-LT1.save' `
  --backup `
  --set-string store.mc=Miaaa `
  --set-int store.money=10000
```

### 4. Re-Sign With Ren'Py Default Logic

Use Ren'Py's default signing flow after any `log` change:

```python
sig = sk.sign(log_data)
ok = vk.verify(sig, log_data)
```

Do not switch to a custom digest-based signing variant just because it looks more explicit. In this validated setup, that causes the classic "save was created on another device" failure.

Write `signatures` back in this format:

```text
signature <public-key-base64> <signature-base64>
```

### 5. Verify Before Declaring Success

At minimum, verify all of these:

- The edited file is the one the game actually loads
- The requested keys now resolve to the expected values in `log`
- The signature verifies against the modified `log`
- The game was not still running during the write

Use the bundled script in inspection mode when you need a quick readback:

```powershell
python .\scripts\patch_and_resign_save.py `
  --save '<live-save-path>\24-3-LT1.save' `
  --show store.mc `
  --show store.money `
  --verify-only
```

## Failure Modes

If the game says the save was created on another device, check these first:

- The archive was modified but not re-signed
- The wrong signing algorithm was used
- The wrong file was edited
- The game was still running and rewrote the save

If the user says "I changed `json` and nothing happened", assume the real value is in `log` until proven otherwise.

If the user says "the script succeeded but the game still shows old values", verify the runtime path before touching the patching logic.

## Bundled Resources

- `references/renpy-save-reference.md`: detailed notes on paths, fields, archive structure, verified symptoms, and example validation outputs
- `scripts/patch_and_resign_save.py`: parameterized helper for backup, field inspection, patching, and re-signing

Load the reference file when you need the validated workspace-specific paths or the deeper troubleshooting checklist.
