# Host matrix — where mainstream agents run this skill

The protocol in `skills/dual-flagship-debate/SKILL.md` uses host-neutral primitives only. What
differs per host is **how a host is told to follow it**, **whether it can spawn isolated read-only
subagents**, and **how read-only is enforced**. This page is the chooser; each linked page has the
concrete recipe.

Legend: **native** = host loads `SKILL.md` itself · **rules** = paste the trigger block into the
host's instruction file · **cli** = drive two vendor CLIs from a shell (works everywhere).

## Fastest path: the ecosystem CLI

The skills CLI already knows most of the agents below, and installs into `.agents/skills` followed by a
link per agent — which is the single-source-of-truth layout this repository recommends:

```bash
npx skills add superj0107/dual-flagship-debate -g -y -a claude-code
npx skills add superj0107/dual-flagship-debate -g -y -a codex -a cursor -a windsurf -a gemini-cli
npx skills add superj0107/dual-flagship-debate -g -y -a '*'      # every agent it detects
npx skills add superj0107/dual-flagship-debate -l                # list what the repo offers, install nothing
```

If a name is rejected it prints the current full agent list (verified, ~80 names: `claude-code`, `codex`,
`cursor`, `gemini-cli`, `github-copilot`, `cline`, `roo`, `opencode`, `windsurf`, `zed`, `warp`, `goose`,
`junie`, `kiro-cli`, `qwen-code`, `openhands`, `continue`, `amp`, `trae`, `droid`, `crush`, `kilo`,
`openclaw`, `universal`, …). Two caveats:

- the flag is `claude-code`, not `claude`;
- installing is not adapting. The per-host pages below still matter, because **read-only enforcement and
  the two-debater dispatch are not part of any install format** — the host has to be told how to run the
  rounds.

| Host | How it picks up the protocol | Isolated read-only subagents | Read-only enforcement | Doc |
|---|---|---|---|---|
| **Claude Code** | native (skill root) | yes (Task/subagents) | `--permission-mode plan`, or restrict `--allowedTools` | [claude-code](claude-code/HOSTS.md) |
| **Codex CLI** | native (skill root) | no — spawn CLI runs | hard: `-s read-only` | [codex](codex/HOSTS.md) |
| **dsh / DeepSeek Harness** | native (skill root) | only via CLI children | per child CLI | [dsh](dsh/HOSTS.md) |
| **Gemini CLI** | rules + optional native | no | approval mode / sandbox flags — verify per version | [gemini-cli](gemini-cli/HOSTS.md) |
| **Cursor** | rules (`.cursor/rules/*.mdc`, `AGENTS.md`) | Background Agents (separate tasks) | ask/agent mode limits; check per build | [cursor](cursor/HOSTS.md) |
| **GitHub Copilot (VS Code)** | rules (`.github/copilot-instructions.md`, `AGENTS.md`) | chat sessions only | tool-approval prompts | [copilot-vscode](copilot-vscode/HOSTS.md) |
| **Cline / Roo Code** | rules (`.clinerules`, `.roo/rules`) | no | auto-approve settings must be off | [cline-roo](cline-roo/HOSTS.md) |
| **opencode / Aider / Windsurf / Zed / JetBrains** | rules (`AGENTS.md`, `CONVENTIONS.md`, `.windsurfrules`, …) | varies | varies | [rules-file hosts](opencode-aider/HOSTS.md) |
| **Anything with a CLI** | cli | two child processes | the CLI's own flag | [portable runner](portable/README.md) |

## Three rules that hold on every host

1. **Never let one context play both debaters.** If the host cannot produce two isolated sessions,
   drop to two child processes; if that is impossible too, stop and report the gap (Tier 3).
2. **Read-only is enforced by configuration, not by asking.** Use the host's own switch
   (permission mode, sandbox flag, tool allow-list, auto-approve off). Then diff the workspace.
3. **Parity is checked against the live model list.** Two flagship-tier models at max reasoning, or
   one flagship in two isolated sessions labelled `模式：同旗舰双隔离`. Never `mini`/`flash`/`haiku`/`lite`.

## Picking a pair on a rules-file host

Rules-file hosts (Cursor, Copilot, Cline, Windsurf, Zed, …) usually expose one model picker. You get
**Tier 2** there: same flagship, two separate chats/tasks with orthogonal lenses. To reach **Tier 1**
(cross-vendor), open the second debater in a different tool or drive a CLI — the transcripts are plain
text, so mixing hosts is fine and often the strongest setup.
