# dual-flagship-debate

[English](README.md)

[![Validate Skill](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml/badge.svg)](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/superj0107/dual-flagship-debate?color=blue)](https://github.com/superj0107/dual-flagship-debate/releases)

一个**双旗舰对抗辩论**的 Agent Skill（`SKILL.md`）。不让单个模型去附和已有草稿、也不让它和稀泥出一个"综合都对"的中间结论：由当前对话的主控 Agent 主持，调度两款**同档顶配旗舰模型**在完全隔离的只读会话中打最多两轮，原文无损交叉转交，主控自己做事实核验，最后给出五栏决策简报。


## 它解决什么

- **结构上反谄媚**：Round 1 完全隔离盲发，双方必须标注 `CONVERGED` / `SHIFTED` / `MAINTAINING_DISSENT`，没有新证据或反例不许改口。
- **同档门禁 + 硬阻断**：只接受两款顶配旗舰开最高推理档；只暴露一款时退化为「同旗舰双隔离」并在裁决首行标注；只剩 `mini` / `flash` / `haiku` / `lite` 或无法开隔离只读会话时**直接报缺口停止**，不许单上下文精分两方。
- **Steelman + 原子化反驳 + Pre-Mortem**：反驳前先用 1–2 句准确还原对方最强论点，再按 `主张 → 缺陷类型 → 反证/替代路径` 打，缺陷限选五类。
- **双态 Round 2**：有状态宿主直接原文回灌原线程；无状态宿主新开隔离会话，注入 `[Step 0 基线 + 本方 R1 + 对手 R1]`。
- **强制事实核验闸门**：裁决前主控亲自只读验证辩手新引用的路径、配置、指标、外部规则，误报当场纠偏。

**适用**：架构与重构取舍、安全/性能边界、数据口径、产品策略、定价 vs 信任、UI 方向、待拍板方案的 Sign-off。
**不适用**：简单事实问答、单文件琐碎修复、已经拍完的机械执行。

## 它跑起来是什么样

[`examples/case-install-sync.md`](examples/case-install-sync.md) 是一个真实决策的完整实录（三处技能安装
要复制副本还是链接到单一真源）：两轮盲发双方结论相反，Round 2 **两边都动了**，主控亲手跑命令证伪了两条
前提，最后是五栏裁决。活下来的答案不是任何一方开局的提案——这正是重点。

Round 2 原文摘录：

> **A：** 对手最强的论点是：A 会让未提交的工作副本即时影响三个宿主；且把 `HOSTS.local.md` 放进仓库会触发
> 隐私检查……`rglob` 检查和隐私文件问题是新证据，足以动摇我原先的 A。
>
> **B：** A′，即链接到专用的发布 worktree（`git worktree add` 检出发布 tag），不链接开发副本，这样 P1 就消失了。

实录保持中文，协议本身不要求任何语言。

## 安装

技能就是一个目录：`SKILL.md` + `references/`。把 `skills/dual-flagship-debate/` 整个复制到宿主的技能根：

| 宿主 | 技能根 | 触发方式 |
|---|---|---|
| **dsh**（DeepSeek Harness） | `~/.agents/skills/` | 在消息里点名，宿主加载 |
| **Codex CLI** | `~/.codex/skills/` | `用 dual-flagship-debate skill：…` |
| **Claude Code** | `~/.claude/skills/` | `/dual-flagship-debate <议题>` |
| Cursor / OpenCode 等 | 宿主扫描 `SKILL.md` 的位置 | 消息里点名 |

```bash
git clone https://github.com/superj0107/dual-flagship-debate.git
cp -r dual-flagship-debate/skills/dual-flagship-debate ~/.claude/skills/
```

或者用生态 CLI：它会把技能装到 `.agents/skills`，再用链接挂进你点名的每个 agent（已实测：先报
`Found 1 skill`，再在 `~/.claude/skills` 下建 junction）：

```bash
npx skills add superj0107/dual-flagship-debate -g -y -a claude-code
npx skills add superj0107/dual-flagship-debate -g -y -a codex -a cursor -a windsurf
npx skills add superj0107/dual-flagship-debate -g -y -a '*'     # 它检测到的所有 agent
```

agent 名字取自那个 CLI 自己的清单：`claude-code`、`codex`、`cursor`、`gemini-cli`、`github-copilot`、
`cline`、`roo`、`opencode`、`windsurf`、`zed`、`warp`、`goose`、`junie`、`kiro-cli`、`qwen-code` 等等，
还有几十个；写错一个名字它会打印当前全量清单。注意是 `claude-code` 不是 `claude`。

若你的宿主会记录技能哈希，**不要就地改已安装的 `SKILL.md`**，把本机默认值写进 `AGENTS.md` / `CLAUDE.md`。

## 选模：三级门禁

1. **Tier 1 双旗舰顶配**（优先跨厂商异构），双方都开最高推理档。规则与配对示例见
   [`references/models-and-hosts.md`](skills/dual-flagship-debate/references/models-and-hosts.md)。
2. **Tier 2 单旗舰双隔离**：只有一款旗舰时，开两个完全隔离的只读会话、派正交视角，裁决首行标 `模式：同旗舰双隔离`。
3. **Tier 3 硬阻断**：只剩轻量模型、无法发起隔离只读会话、或推理档对不齐 → 报缺口停止。

型号会漂移：**永远先看宿主实时目录**，别照抄文档里带日期的示例。

## 适配的宿主

协议本身宿主中立；每个宿主不同的只有三件事：怎么加载协议、有没有隔离只读子会话、只读怎么强制。
完整清单（Claude Code、Codex CLI、Gemini CLI、Cursor、GitHub Copilot、Cline / Roo Code、opencode、
Aider、Windsurf、Zed、JetBrains，以及任何带 CLI 的宿主）见 [`hosts/README.md`](hosts/README.md)。

| 宿主 | 配方 |
|---|---|
| Claude Code | [hosts/claude-code](hosts/claude-code/HOSTS.md) — 原生技能、Task 子会话、`--permission-mode plan` |
| Codex CLI | [hosts/codex](hosts/codex/HOSTS.md) — `codex exec -s read-only --ephemeral` |
| Gemini CLI | [hosts/gemini-cli](hosts/gemini-cli/HOSTS.md) — `GEMINI.md` + CLI 子进程 |
| Cursor | [hosts/cursor](hosts/cursor/HOSTS.md) — `.cursor/rules`，两个聊天或 Background Agents |
| GitHub Copilot（VS Code） | [hosts/copilot-vscode](hosts/copilot-vscode/HOSTS.md) — `.github/copilot-instructions.md` |
| Cline / Roo Code | [hosts/cline-roo](hosts/cline-roo/HOSTS.md) — `.clinerules` / `.roo/rules`，关自动批准 |
| opencode / Aider / Windsurf / Zed / JetBrains | [hosts/opencode-aider](hosts/opencode-aider/HOSTS.md) — `AGENTS.md`、`CONVENTIONS.md`、`.windsurfrules` |
| dsh（DeepSeek Harness） | [hosts/dsh](hosts/dsh/HOSTS.md) — 无旗舰子 Agent，改驱动 CLI |
| 任何 rules 型宿主 | [hosts/rules-snippets](hosts/rules-snippets/README.md) — 一份复制即用的规则块 |

两个运行器，同一套两轮协议：

- [`hosts/portable/run_debate.py`](hosts/portable/README.md) —— **任意两个 CLI、任意系统**，配置驱动
- [`hosts/windows-cli/run-debate.ps1`](hosts/windows-cli/run-debate.ps1) —— 同一协议，原生 PowerShell

```bash
# 便携版（Linux / macOS / Windows 通用）
python3 hosts/portable/run_debate.py --config debate.config.json --topic my-topic.md --rounds 2
```

```powershell
# Windows 原生
powershell -ExecutionPolicy Bypass -File hosts\windows-cli\run-debate.ps1 -TopicFile .\my-topic.md -Rounds 2
```

两条真正决定成败的实践规则：

- **只读必须由派发方强制**，不能靠嘴求。用宿主自己的硬开关（`-s read-only`、`--permission-mode plan`、限制工具白名单）。默认全权限的 CLI 会老老实实给你写文件。
- **无状态宿主的 Round 2 必须新进程**，把双方 R1 原文都贴进去。绝不允许把两个辩手塞进一个上下文。

## 钉住默认 pair

写进 `AGENTS.md` / `CLAUDE.md`（不动技能文件）：

```markdown
- Default `dual-flagship-debate` pair: Debater A = `<flagship-a>` (`<top-effort>`), Debater B = `<flagship-b>` (`<top-effort>`).
- Fall back to dual isolated `<flagship-a>` sessions only if the peer model is unavailable; never downgrade to mini/flash/haiku/lite.
```

## 目录

```
skills/dual-flagship-debate/SKILL.md      协议本体（宿主加载这个）
skills/dual-flagship-debate/references/   选模规则 + 宿主任务范式
hosts/README.md                           宿主矩阵：怎么加载、只读靠什么保证
hosts/<host>/HOSTS.md                     每类宿主一份配方
hosts/rules-snippets/                     rules 型宿主的复制即用规则块
hosts/portable/run_debate.py              便携运行器：任意两个 CLI、任意系统
hosts/windows-cli/run-debate.ps1          Windows 原生运行器
examples/topic-template.md                Step 0 客观基线模板
tests/validate_skill.py                   结构 / 契约 / 隐私检查
```

## 自检

```bash
python3 tests/validate_skill.py
```

## 许可

MIT，见 [LICENSE](LICENSE)。
