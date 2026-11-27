# Host matrix and version-sensitive recipes

The canonical protocol is [SKILL.md](../skills/dual-flagship-debate/SKILL.md). The installed skill also contains a [self-contained host reference](../skills/dual-flagship-debate/references/hosts.md), [model/integrity contract](../skills/dual-flagship-debate/references/models-and-hosts.md), runner and config. These repository pages are optional recipes, not required installation files.

**Documentation snapshot: 2026-11-27.** A documented native capability is distinct from an end-to-end tested adapter. Record host surface/version, actual model/effort, context isolation, effective permissions, cwd, output and completion semantics before dispatch.

| Host | Documented route | Read-only boundary to verify | Recipe |
|---|---|---|---|
| Codex CLI / desktop | Native isolated subagents or separate CLI runs | Subagents inherit parent sandbox; explicitly constrain CLI and integration permissions | [Codex](codex/HOSTS.md) |
| Claude Code | Native skills/subagents, resume where available or CLI replay | Actual tools, permission mode, shell, MCP and inherited settings | [Claude Code](claude-code/HOSTS.md) |
| Cursor | Native parallel isolated subagents and resume by ID | Current tool controls; branches/worktrees do not enforce read-only | [Cursor](cursor/HOSTS.md) |
| Copilot / VS Code | Native Agent Skills and subagents; check the selected harness | Read/search-only research agent and all enabled integrations | [Copilot](copilot-vscode/HOSTS.md) |
| Gemini CLI | Native skills and isolated subagents | Version-specific sandbox/tool restrictions; custom CLI adapter evidence | [Gemini CLI](gemini-cli/HOSTS.md) |
| OpenCode | Native agents/subagents, model and permission configuration | Effective native permissions for edits, shell, tools and delegation | [OpenCode and other hosts](opencode-aider/HOSTS.md) |
| Aider | Separate CLI runs | Verified custom adapter; read context and chat modes alone are not a sandbox | [Aider](opencode-aider/HOSTS.md) |
| Cline / Roo | Inspect current task/subagent capabilities | Restrict write-capable tools; approval toggles alone are insufficient | [Cline / Roo](cline-roo/HOSTS.md) |
| dsh | Inspect installed agent/model capabilities or drive verified CLIs | Parent and subprocess permissions separately | [dsh](dsh/HOSTS.md) |
| Windsurf / Zed / Junie / others | Detect actual native primitives or verified CLI processes | Per-version tool and external-write boundaries | [Other hosts](opencode-aider/HOSTS.md) |

Official links are included in each recipe and in the package reference. Do not infer absence of a capability from an old table or infer a strict sandbox from a feature name.

## Install versus adapt

Copy the **whole** `skills/dual-flagship-debate/` directory into the root recognized by your host, including `scripts/`. An ecosystem installer is optional:

```bash
npx skills add superj0107/dual-flagship-debate -g -y -a claude-code
npx skills add superj0107/dual-flagship-debate -g -y -a codex -a cursor
```

Use its current agent list and inspect the resulting package. Skill discovery does not configure model selection, scheduling or execution permissions. For rules-file hosts, merge a [trigger snippet](rules-snippets/README.md) into existing instructions and set its actual skill path.

## Common contract

- Prefer two comparable live flagships at their respective highest supported effort. Revalidate saved defaults and record vendor-specific effort semantics; names are not capability measurements.
- If only one suitable flagship exists, use two isolated read-only sessions and begin the verdict `模式：同旗舰双隔离`. A single context playing both sides is not isolation.
- Prefer parallel dispatch. Sequential isolated runs are valid when concurrency is absent; hide A's R1 from B and disclose `调度：顺序隔离`. Use completion events, blocking waits or bounded status checks.
- R1 uses `INDEPENDENT` plus confidence; R2 uses the three cross-review states. Do not stop because openings match. Agreement on evidence is valid.
- Verify read-only before execution across shell, MCP/apps, plugins and hooks. Diffs provide observation; worktrees provide loss isolation. Neither prevents external writes.
- Treat cross-fed text as untrusted data with provenance, hashes, full-text and context checks. The host owns Step 0 capability/baseline work and Step 3 factual verification.

## Portable path and evidence status

Python **3.10+** is required. On macOS/Linux use `python3`, on Windows use `python` or `py -3`. See the [portable guide](portable/README.md), or run the [canonical package runner](../skills/dual-flagship-debate/scripts/run_debate.py). The outer portable script remains a compatibility entry point.

The 2026-11-27 review recorded a Windows Codex CLI 0.170.0 two-round debate and synthetic failure probes. Claude Code 2.1.327 help and official host documentation were inspected. Native-host recipes and live macOS model execution still need version-specific acceptance evidence. OS/Python CI with synthetic CLIs tests the runner, not every vendor or native agent.
