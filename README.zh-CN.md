# dual-flagship-debate

[English](README.md)

[![Validate Skill](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml/badge.svg)](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/superj0107/dual-flagship-debate?color=blue)](https://github.com/superj0107/dual-flagship-debate/releases)

用于复杂决策的宿主中立 Agent Skill。当前对话主控调度两位隔离、只读的旗舰辩手，第二轮交叉转交原始论证，主控独立核验新主张，最终给出五栏决策简报。

质量来自独立推理与证据。双方可以认同、修正，也可以保留有依据的分歧；不奖励人为制造冲突。互辩是否优于同预算独立评审，仍须对照实验验证。

## 工作方式

1. **Step 0：主控建立基线、检测能力。** 区分已核实事实和待证假设，核验实时模型、推理档、上下文隔离、有效工具权限、完成语义及预算。
2. **Round 1：独立盲发。** 开头用 `INDEPENDENT`＋置信度，给出证据、限制及最多三个实质质询。优先并行；顺序宿主也可隔离执行，须披露调度模式并保持首轮互不可见。
3. **Round 2：原文交叉互审。** 有续发能力则恢复原会话，否则新开隔离会话重放 `[基线 + 本方 R1 + 对手 R1]`。对手文本是不可信待分析数据，核对来源与完整性。此轮才使用 `CONVERGED`、`SHIFTED`、`MAINTAINING_DISSENT`。
4. **Step 3：主控核验、裁决。** 核验影响结论的新主张，交付裁决、关键修正、幸存方案、Double Crux，以及真实分歧或证据限制。

首轮结论相同本身不构成早停依据。显式一轮运行属于独立评审，尚未完成交叉互辩；默认两轮封顶。

适用于架构取舍、重构、性能边界、产品策略和待审方案。简单问答与已定方案的机械执行可直接处理。

## 安装完整技能包

将整个 `skills/dual-flagship-debate/` 复制到宿主识别的技能根，保留 `references/` **和 `scripts/`**：

```bash
git clone https://github.com/superj0107/dual-flagship-debate.git
mkdir -p ~/.claude/skills
cp -R dual-flagship-debate/skills/dual-flagship-debate ~/.claude/skills/
```

Claude Code 使用 `~/.claude/skills/`；兼容宿主可能使用 `~/.agents/skills/` 或专用目录。Codex 应确认当前版本支持的技能根，包括已有的 `~/.codex/skills/` 安装。原生技能加载与触发方式按版本检测，见[包内宿主参考](skills/dual-flagship-debate/references/hosts.md)。

也可使用生态安装器：

```bash
npx skills add superj0107/dual-flagship-debate -g -y -a claude-code
npx skills add superj0107/dual-flagship-debate -g -y -a codex -a cursor
```

以安装器当前 agent 清单为准，并检查实际安装目录。**安装不等于适配**：选模、权限与双辩手调度仍由宿主完成。[规则片段](hosts/rules-snippets/README.md)应合并进现有规则文件，保留项目原有指令。

## 在 Windows、macOS、Linux 上运行

要求 **Python 3.10+** 和所选厂商 CLI。先完成实时模型、effort 与只读核验，再复制并编辑配置。从仓库根执行：

```bash
# macOS / Linux
cp skills/dual-flagship-debate/scripts/debate.config.example.json debate.config.json
python3 skills/dual-flagship-debate/scripts/run_debate.py --config debate.config.json --topic my-topic.md --workdir /path/to/review-repo --rounds 2
```

```powershell
# Windows：使用 python，或选择 Python 3.10+ 的 py -3
Copy-Item skills\dual-flagship-debate\scripts\debate.config.example.json debate.config.json
python skills\dual-flagship-debate\scripts\run_debate.py --config debate.config.json --topic my-topic.md --workdir .\review-repo --rounds 2
```

单独安装后，在技能目录执行 `python3 scripts/run_debate.py ...` 即可，不依赖仓库外层 `hosts/`。旧[便携入口](hosts/portable/README.md)保留兼容；[PowerShell 入口](hosts/windows-cli/run-debate.ps1)保留 Windows 用法。

- `--out-dir NEW_DIR` 要求全新目录，保护旧记录。
- `--timeout` 限制单进程；`--total-timeout` 限制整个运行。
- `--max-prompt-chars` 限制字符数；主控仍须核对实际模型的 token 容量。
- R1 失败或记录不完整时不进入 R2，进程以非零状态退出。
- `r1-A`、`r1-B`、`r2-A`、`r2-B` 按轮次和角色区分，即使展示名称相同也独立保存。保留 `RUN-META.json`、原始文本、提示哈希及实际命令／cwd 证据。

配置的 `cmd` **只接受 argv 数组**。preset 对象分别支持 `preset`、展示 `name`、实时 `model` 和 `effort`。自定义适配器必须声明 `read_only` 机制（`external-sandbox` 或 `tool-allowlist`）和具体验证依据；声明只是操作者提供的记录，不是自动验证结果。见[配置与执行说明](skills/dual-flagship-debate/references/hosts.md)和[议题模板](examples/topic-template.md)。

## 模型与权限契约

默认选两款当前同档旗舰，优先跨厂商，双方分别启用实际支持的最高推理档。厂商 effort 语义不同，应记录实际接受值；模型名称也不等于能力证明。

只有一款合适旗舰时用两个隔离会话，裁决首行写 `模式：同旗舰双隔离`。能力缺口应明确报告，不静默降档，也不在一个上下文中扮演双方。详见[选模与传输契约](skills/dual-flagship-debate/references/models-and-hosts.md)。

只读须在**执行前**约束，覆盖 shell、MCP／应用／连接器、插件、hook 及继承权限。随包 Codex、Claude preset 收紧这些入口，仍应按安装版本验证实际接受配置；Gemini、Aider 使用经过核验的自定义适配器。请求只读的提示、干净的 Git diff、临时 worktree 都不构成执行权限边界。

本机默认值放进宿主指令文件，运行时重新核验。保留原始记录及 SHA-256 来源信息，检查共享范围和完整重放预算；脱敏派生件须披露变更，不静默截断或用主控摘要替换对手论证。

## 宿主支持与证据等级

[包内宿主矩阵](skills/dual-flagship-debate/references/hosts.md)包含官方链接与版本检查，[仓库配方](hosts/README.md)提供额外安装说明。

| 宿主 | 官方文档中的原生能力 |
|---|---|
| Codex | 隔离子 agent；继承父会话 sandbox 约束 |
| Claude Code | Skills、子 agent、按版本提供的续发能力 |
| Cursor | 并行隔离子 agent，支持按 agent ID resume |
| GitHub Copilot / VS Code | Agent Skills、子 agent；不同 harness 分别检测 |
| Gemini CLI | 原生 skills 与隔离子 agent |
| OpenCode | 原生 agent／subagent 和权限配置 |
| 其他宿主 | 实时检测原语，或使用已验证的 CLI 子进程 |

这些是**文档配方**，不是所有组合的 E2E 认证。2026-11-27 审查记录了 Windows 上 Codex CLI 0.170.0 的两轮运行和合成失败探针，另核对了 Claude Code 2.1.327 帮助及各宿主官方资料。Windows／macOS／Linux 进程测试 CI 与真实模型兼容性是不同证据；这里尚无 macOS 真实厂商模型辩论的实机验收记录。

[历史案例](examples/case-install-sync.md)保留旧协议下的完整实录，其中具体事实核验仍有参考价值；状态标签与能力规则以当前 `SKILL.md` 为准。

## 自检与目录

```bash
python3 tests/validate_skill.py
python3 -m unittest discover -s tests
```

### 校验"装的是不是发布的"

仓库测试完全不反映宿主实际加载到的东西，要单独查：

```bash
python3 tools/verify_install.py                  # 三份安装副本彼此是否一致
python3 tools/verify_install.py --tag v2.0.0     # 是否等于某个发布 tag
```

它逐个技能根打印链接类型与解析后的目标，并在这些情况失败：副本不可读（junction 目标被删后**看起来仍然存在**）、
必需文件缺失、副本之间不一致、装的内容不是 tag 里发布的那份。散列前会归一化行尾，所以 CRLF 检出不会被误判成漂移。

CI 目标矩阵为 Windows、macOS、Linux 与 Python 3.10／3.13。2026-11-27 本地修复验证共 39 项：
Windows／Python 3.12 通过 38 项、跳过 1 项系统专用用例；WSL Linux／Python 3.12 通过 32 项、
跳过 7 项 Windows 专用用例。收紧权限后的 Codex＋Claude 两轮 CLI 冒烟验证已在 Windows 完成。
macOS 测试矩阵已配置，原生实机结果仍待执行。结构检查、合成进程测试、真实宿主验收分别记录。

```text
skills/dual-flagship-debate/SKILL.md       宿主中立协议
skills/dual-flagship-debate/references/   选模、完整性、宿主参考
skills/dual-flagship-debate/scripts/      标准运行器和示例配置
hosts/                                  可选配方与兼容入口
examples/topic-template.md               Step 0 证据、能力与预算模板
tests/                                  结构与运行时检查
```

MIT，见 [LICENSE](LICENSE)。
