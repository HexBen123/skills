# Ren'Py Save Reference

## Scope

This reference captures the validated behavior from `Eternum存档修改指南.md` for the local Eternum portable build in this workspace.

## Validated Paths

- Game directory: `G:\后端\新建文件夹 (2)\Eternum-0.9.5-pc`
- Live saves directory: `G:\后端\新建文件夹 (2)\Eternum-0.9.5-pc\game\saves`
- Ren'Py signing keys: `C:\Users\XHB\AppData\Roaming\RenPy\tokens\security_keys.txt`

## Core Facts

- `.save` files in this build are ZIP archives
- gameplay values like money and player name are stored in `log`
- `json` is only lightweight metadata for this scenario
- any `log` mutation must be followed by a new `signatures` entry

## Common Keys

- `store.mc`: player name
- `store.money`: money
- `store.nickname`: nickname
- `store.lastname`: surname or alternate name field

## Recommended Order

1. Exit the game completely.
2. Confirm the target file is under the live `game\saves` directory.
3. Create a `.bak` copy.
4. Read `log` from the ZIP archive.
5. Patch the required values in the pickle opcode stream.
6. Re-sign using Ren'Py default signing logic.
7. Rewrite `signatures`.
8. Replace the original archive atomically.
9. Verify values and signature again.

## Archive Entries

- `log`: authoritative game state
- `signatures`: signature record used by the game
- `json`: lightweight metadata, usually not the source of requested value changes

## Signing Rule

Use the verified default flow:

```python
sig = sk.sign(log_data)
ok = vk.verify(sig, log_data)
```

Do not replace this with a custom SHA-256 signing variant for this game build.

## Signature File Format

```text
signature <public-key-base64> <signature-base64>
```

## Verified Symptoms And Likely Causes

### Save was created on another device

- `log` changed but `signatures` was not updated
- wrong signature logic was used
- wrong save file was edited

### Values changed on disk but not in game

- game was still running and overwrote the archive
- edited file was a copied save, not the live one
- value was changed in `json` instead of `log`

### Script ran but values still look wrong

- patched the wrong key
- did not rebuild pickle opcodes between sequential edits
- edited a file outside the live save path

## Verified Historical Examples

- `24-3-LT1.save`: `store.mc` changed from `Xhb111` to `Miaaa`, `store.money` changed from `381` to `10000`, signature verification returned `True`
- `17-5-LT1.save`: `store.money` changed from `-44` to `10000`, signature verification returned `True`

## Suggested Commands

Install dependency:

```powershell
python -m pip install --user ecdsa
```

Patch name and money:

```powershell
python .\scripts\patch_and_resign_save.py `
  --save 'G:\后端\新建文件夹 (2)\Eternum-0.9.5-pc\game\saves\24-3-LT1.save' `
  --backup `
  --set-string store.mc=Miaaa `
  --set-int store.money=10000
```

Verify fields and signature without writing:

```powershell
python .\scripts\patch_and_resign_save.py `
  --save 'G:\后端\新建文件夹 (2)\Eternum-0.9.5-pc\game\saves\24-3-LT1.save' `
  --show store.mc `
  --show store.money `
  --verify-only
```
