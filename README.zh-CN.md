# dual-flagship-debate

[English](README.md)

[![Validate Skill](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml/badge.svg)](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml)

一个**双旗舰对抗辩论**的 Agent Skill（`SKILL.md`）。不让单个模型去附和已有草稿、也不让它和稀泥出一个"综合都对"的中间结论：由当前对话的主控 Agent 主持，调度两款**同档顶配旗舰模型**在完全隔离的只读会话中打最多两轮，原文无损交叉转交，主控自己做事实核验，最后给出五栏决策简报。


## 它解决什么

- **结构上反谄媚**：Round 1 完全隔离盲发，双方必须标注 `CONVERGED` / `SHIFTED` / `MAINTAINING_DISSENT`，没有新证据或反例不许改口。
- **同档门禁 + 硬阻断**：只接受两款顶配旗舰开最高推理档；只暴露一款时退化为「同旗舰双隔离」并在裁决首行标注；只剩 `mini` / `flash` / `haiku` / `lite` 或无法开隔离只读会话时**直接报缺口停止**，不许单上下文精分两方。
- **Steelman + 原子化反驳 + Pre-Mortem**：反驳前先用 1–2 句准确还原对方最强论点，再按 `主张 → 缺陷类型 → 反证/替代路径` 打，缺陷限选五类。
- **双态 Round 2**：有状态宿主直接原文回灌原线程；无状态宿主新开隔离会话，注入 `[Step 0 基线 + 本方 R1 + 对手 R1]`。
- **强制事实核验闸门**：裁决前主控亲自只读验证辩手新引用的路径、配置、指标、外部规则，误报当场纠偏。

**适用**：架构与重构取舍、安全/性能边界、数据口径、产品策略、定价 vs 信任、UI 方向、待拍板方案的 Sign-off。
**不适用**：简单事实问答、单文件琐碎修复、已经拍完的机械执行。

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

若你的宿主会记录技能哈希，**不要就地改已安装的 `SKILL.md`**，把本机默认值写进 `AGENTS.md` / `CLAUDE.md`（见下）。

## 选模：三级门禁

1. **Tier 1 双旗舰顶配**（优先跨厂商异构），双方都开最高推理档。规则与配对示例见
   [`references/models-and-hosts.md`](skills/dual-flagship-debate/references/models-and-hosts.md)。
2. **Tier 2 单旗舰双隔离**：只有一款旗舰时，开两个完全隔离的只读会话、派正交视角，裁决首行标 `模式：同旗舰双隔离`。
3. **Tier 3 硬阻断**：只剩轻量模型、无法发起隔离只读会话、或推理档对不齐 → 报缺口停止。

型号会漂移：**永远先看宿主实时目录**，别照抄文档里带日期的示例。

## 宿主派发

协议用宿主中立的原语写成，三种派发范式（有状态多线程 / 无状态子 Agent / CLI 一次性）见 reference。具体到本机怎么发，见 [`hosts/`](hosts)：

- [`hosts/dsh/HOSTS.md`](hosts/dsh/HOSTS.md)：宿主内部没有旗舰子 Agent 时，改由主控驱动 CLI 进程
- [`hosts/codex/HOSTS.md`](hosts/codex/HOSTS.md)：`codex exec -s read-only --ephemeral`
- [`hosts/claude-code/HOSTS.md`](hosts/claude-code/HOSTS.md)：`claude -p` 或原生子 Agent
- [`hosts/windows-cli/run-debate.ps1`](hosts/windows-cli/run-debate.ps1)：Round 1 并行盲发 → Round 2 无状态重放，带只读守卫

```powershell
# 先把 examples/topic-template.md 填成你的议题文件，然后：
powershell -ExecutionPolicy Bypass -File hosts\windows-cli\run-debate.ps1 `
  -TopicFile .\my-topic.md -Mode cross-vendor -Rounds 2
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
hosts/                                    各宿主派发配方 + Windows 运行器
examples/topic-template.md                Step 0 客观基线模板
tests/validate_skill.py                   结构 / 契约 / 隐私检查
```

## 自检

```bash
python3 tests/validate_skill.py
```

## 许可

MIT，见 [LICENSE](LICENSE)。
