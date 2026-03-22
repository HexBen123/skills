# 技能仓库

这是一个用于整理和沉淀可复用技能的仓库，主要存放技能目录、说明文档以及配套脚本。

当前内容以中文导航为主，便于后续持续扩展更多分类和技能。

## 仓库用途

- 集中管理可复用的技能
- 给每个技能保留清晰的入口、参考文档和脚本资源
- 通过分类目录组织不同主题下的技能

## 仓库结构

```text
skills/
  eternum/
    README.md
    eternum-renpy-save-editing/
      SKILL.md
      references/
      scripts/
```

## 分类索引

- [eternum](./skills/eternum/README.md)
  Eternum 相关技能分类，主要收录存档修改、验证、脚本化处理等技能。

## 技能索引

- [eternum-renpy-save-editing](./skills/eternum/eternum-renpy-save-editing/SKILL.md)
  用于修改、验证和重新签名 Eternum / Ren'Py `.save` 存档，适合处理字段不在 `json`、修改后提示“另一台设备创建”、以及需要脚本化改写 `log` 和 `signatures` 的场景。

## 使用建议

- 进入具体技能时，优先阅读对应目录下的 `SKILL.md`
- 如果技能目录中包含 `references/`，说明那里有更详细的背景知识或排障说明
- 如果技能目录中包含 `scripts/`，优先复用现成脚本，而不是每次重新手写逻辑

## 维护约定

- 根目录 `README.md` 负责提供全仓库导航
- 每个分类目录建议有自己的 `README.md`，负责本分类索引
- 每个技能目录至少包含 `SKILL.md`
- 只有确实需要时，才为技能增加 `references/`、`scripts/` 等附属资源
