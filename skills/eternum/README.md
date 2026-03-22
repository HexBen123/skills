# Eternum 技能索引

这个目录用于收集 Eternum 相关的技能。

当前重点是围绕 Ren'Py 存档的读取、修改、验签和脚本化处理，后续如果增加更多 Eternum 主题技能，也继续在这里维护索引。

## 当前技能

- [eternum-renpy-save-editing](./eternum-renpy-save-editing/SKILL.md)
  用于修改、验证和重新签名 Eternum / Ren'Py `.save` 存档。

## 适用场景

- 想修改玩家名称、姓氏、金币等字段
- 修改后游戏提示“这个存档是在另一台设备上创建”
- 改了 `json` 但实际读档没有变化
- 需要复用脚本批量或稳定地修改存档

## 目录说明

- `eternum-renpy-save-editing/SKILL.md`
  技能主入口，说明何时使用、如何排查、怎样按正确流程处理存档。

- `eternum-renpy-save-editing/references/renpy-save-reference.md`
  更细的参考资料，包含已验证路径、关键字段、签名规则和常见错误。

- `eternum-renpy-save-editing/scripts/patch_and_resign_save.py`
  配套脚本，用于直接修改 `log` 中的字段并重写 `signatures`。

## 维护说明

- 新增 Eternum 相关技能时，请同步更新本索引
- 如果某个技能带有参考文档或脚本，建议在本页补一句用途说明，方便后续快速检索
