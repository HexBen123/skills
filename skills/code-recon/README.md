# code-recon

**融合 fast-context 与 codegraph 的代码智能技能**。本技能旨在解决一个实际观察到的问题：在真实会话中，智能体极少调用这两款 MCP 工具，且几乎不会组合使用——它们默认使用 Grep/Glob/Read 工具，或仅调用一次工具就停止。本技能将二者的组合调用设为代码库中所有「位置/实现方式/关联方/影响范围」类问题的默认路由方案。

- **fast-context** (`mcp__fast-context__fast_context_search`) —— 语义检索网络：输入自然语言，输出文件路径、行范围与 grep 关键词；可覆盖完整文件系统（含未纳入索引的文件）。
- **codegraph** (`mcp__codegraph__codegraph_*`) —— 结构权威数据源：基于预构建索引提供精确的位置、源码、关联边与影响范围；响应即时、离线可用、无配额限制，但仅支持索引文件内的静态关联边。

二者互为补充。绝大多数有复杂度的代码问题都需要在两者之间接力完成。

## 目录结构

```
code-recon/
├── SKILL.md                     路由配置：技能描述（触发条件）+ 必读规则 + 常见任务 + 常见问题 + 设计原则
├── rules/
│   └── using-the-tools.md       工具选择矩阵 + 组合使用规范 + 接力流程 + 无需调用工具的场景（必读规则）
├── workflows/
│   └── recon-playbook.md        单一流转流程（侦察→精准定位→交叉校验），含 A–D 共 4 个章节，每章附检查清单
├── references/
│   ├── gotchas.md                5 项已验证的踩坑点（现象/原因/修复方案/预防措施 + NeoForge 实证案例）
│   ├── tool-reference.md         两款工具的完整参数说明 + 实际输出格式
│   └── worked-example.md         NeoForge 项目完整端到端实操案例（踩坑点的实证来源）
├── shells/                      轻量适配壳：CLAUDE/AGENTS/CODEX/GEMINI 及 .cursor（规则 + 注册配置）
├── hooks/                       会话启动自动重注入机制（适配 Claude Code 与 Cursor）
├── scripts/smoke-test.sh        自动化结构自检脚本
└── INSTALL.md                   各运行环境安装指南（全局 + 单项目）
```

## 维护规范

- **新增踩坑点**：仅当真实运行中发现问题，且满足三项标准中的两项（可复现、影响成本高、问题不直观）时才可添加。需同步完成三处更新：在 `references/gotchas.md` 补充「现象/原因/修复/预防」完整模块；在 SKILL.md 的「已知问题」中添加一句话摘要与对应锚点；在相关工作流的检查清单中新增对应条目。仅存放而不嵌入执行路径视为无效。
- **编辑 SKILL.md、适配壳文件或技能描述后** → 执行 `bash scripts/smoke-test.sh`。
- **禁止**将 `references/` 目录当作会话日志——仅收录可通用、可复用的经验总结。
