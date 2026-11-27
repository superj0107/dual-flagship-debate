# Host capabilities and the self-contained runner

Documentation snapshot: 2026-11-27. Native capability documented by a vendor is a **recipe**, not evidence that this package completed an end-to-end debate on that host/version. Verify the installed surface, account, model and permission configuration before use.

## Install the whole skill directory

Copy the directory containing `SKILL.md`, `references/`, and `scripts/` into a skill root recognized by the host. Examples include `~/.claude/skills/`, the Codex skill roots recognized by the installed build, and `~/.agents/skills/` for compatible hosts. Use the host's current skills documentation to confirm its lookup path. A rules file can instead point at a readable installed `SKILL.md`.

The installed directory is self-contained. The runner is [`../scripts/run_debate.py`](../scripts/run_debate.py) and its config template is [`../scripts/debate.config.example.json`](../scripts/debate.config.example.json). Repository-level `hosts/` recipes are optional reading, not installation dependencies. Loading the skill alone does not configure dispatch or permissions.

## Portable CLI route: Windows, macOS and Linux

Requires **Python 3.10+** and the chosen vendor CLIs on `PATH`. From the installed skill directory:

```bash
# macOS / Linux
cp scripts/debate.config.example.json debate.config.json
# Edit the copy after live model/effort and permission checks.
python3 scripts/run_debate.py --config debate.config.json --topic /path/to/topic.md --workdir /path/to/repo --rounds 2
```

```powershell
# Windows
Copy-Item scripts\debate.config.example.json debate.config.json
python scripts\run_debate.py --config debate.config.json --topic .\topic.md --workdir .\review-repo --rounds 2
# py -3 can replace python if that launcher selects Python 3.10+.
```

Run from the repository root by prefixing the script with `skills/dual-flagship-debate/`. The old `hosts/portable/run_debate.py` is a compatibility entry point. This implementation targets all three operating systems; a CI matrix or synthetic-process test is distinct from a live vendor/model end-to-end test. There is no macOS live-model acceptance claim in this documentation.

Additional controls:

| Argument | Meaning |
|---|---|
| `--out-dir NEW_DIR` | New run directory; existing directories are rejected to preserve old records |
| `--timeout SECONDS` | Per-process timeout |
| `--total-timeout SECONDS` | Whole-run timeout, including both rounds |
| `--max-prompt-chars COUNT` | Input character cap; the host still checks model token capacity |
| `--rounds 1` | Independent openings only; not a completed cross-review |

Both R1 outputs must succeed and be complete before R2. Failures return a nonzero exit status. Artifacts use distinct round/role keys (`r1-A`, `r1-B`, `r2-A`, `r2-B`), even for identical display names. Preserve `RUN-META.json`, raw transcripts, prompts, command/cwd records, and hashes for the host's checks.

## Config and read-only evidence

Each debater can be a preset string or an object with live model/effort overrides, for example:

```json
{
  "debaters": {
    "A": {"preset": "codex-cli", "name": "reviewer", "model": "<live-model-id>", "effort": "<actual-top-effort>"},
    "B": {"preset": "codex-cli", "name": "reviewer", "model": "<live-model-id>", "effort": "<actual-top-effort>"}
  }
}
```

The example demonstrates the same-model fallback, not model discovery. The host validates live IDs and effort values before running. Record requested and observed values separately. A string such as `"codex-cli"` uses that preset's CLI configuration; it does not certify model capability.

Custom `cmd` accepts an **argv array only**, with supported placeholders such as `{out}`, `{prompt}`, and `{workdir}`. A shell command string is a configuration error. Every custom adapter must declare its actual read-only mechanism and concrete verification evidence:

```json
{
  "name": "custom-reviewer",
  "cmd": ["<cli>", "<verified-read-only-flag>"],
  "read_only": {
    "mechanism": "tool-allowlist",
    "evidence": "<host/version, effective tool list, and observed write-block result>"
  }
}
```

`external-sandbox` is the other supported mechanism. A declaration is an audit record supplied by the operator, not an independently verified sandbox. Replace placeholders with evidence before use. Gemini and Aider require a verified custom adapter; there is no unrestricted preset for either.

The bundled Codex preset explicitly selects read-only and disables MCP/apps/hooks/plugins. The Claude preset uses safe mode, a read-only builtin tool set and disabled MCP; inspect the accepted flags in the installed CLI version. In particular, a permission approval bypass or `--allowedTools` alone is not a complete tool restriction. Any inherited shell or external write capability invalidates a strict read-only claim until constrained. Workspace diffs and throwaway worktrees provide observation and loss isolation only.

## Native-host matrix and official sources

All rows below are **documentation recipes** unless a version-specific execution record says otherwise. Check versions, API/tool availability, permission inheritance, resume semantics and model settings at runtime.

| Host surface | Native route and R2 | Permission check | Official documentation |
|---|---|---|---|
| Codex CLI / desktop | Native isolated subagents exist; resume when supported, otherwise fresh CLI replay | Subagents inherit parent sandbox constraints; a separate context alone does not create a new read-only boundary | [Subagents](https://developers.openai.com/codex/subagents), [Security](https://developers.openai.com/codex/security), [Skills](https://developers.openai.com/codex/skills) |
| Claude Code | Native skills and subagents; resume a preserved agent ID or replay | Verify subagent tool list, permission mode, shell and MCP; CLI presets must be accepted by that version | [Skills](https://code.claude.com/docs/en/skills), [Subagents](https://code.claude.com/docs/en/sub-agents), [CLI](https://code.claude.com/docs/en/cli-reference) |
| Cursor | Native isolated subagents support parallel execution and resume by agent ID; replay only where resume is absent | Inspect current agent/tool permission controls; a branch/worktree is not read-only | [Subagents](https://cursor.com/docs/subagents), [Rules](https://cursor.com/docs/context/rules) |
| GitHub Copilot / VS Code | Agent Skills and native subagent workflows exist; distinguish VS Code, CLI and cloud harnesses | Use a research agent with read/search tools; verify all enabled tools and per-surface behavior | [Skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills), [VS Code subagents](https://code.visualstudio.com/docs/agents/run/subagents) |
| Gemini CLI | Native skills and isolated subagents exist; use available resume or fresh replay | Verify version-specific tool restrictions and sandbox settings; custom CLI adapter needs evidence | [Skills](https://geminicli.com/docs/cli/skills/), [Subagents](https://geminicli.com/docs/core/subagents/) |
| OpenCode | Native custom agents/subagents with model and permission configuration | Configure native permissions for edit, shell, external tools and delegation; verify effective scope | [Agents](https://opencode.ai/docs/agents/), [Permissions](https://opencode.ai/docs/permissions/), [Skills](https://opencode.ai/docs/skills/) |
| Aider | Separate CLI runs; ask/read modes may help construct an adapter | `--read` protects supplied context, not every available capability; avoid automatic edit approval, verify a custom boundary | [Chat modes](https://aider.chat/docs/usage/modes.html) |
| Cline / Roo / Windsurf / Zed / Junie / dsh | Detect actual skill, task and context-isolation primitives; otherwise use separate verified CLI processes | Auto-approval off is a prompt gate, not an execution sandbox; scope or remove write-capable tools | Consult the installed host's official version documentation |

Prefer parallel isolated A/B runs. Sequential isolated runs are valid when concurrency is absent; hide A's R1 from B and label the schedule. Wait through completion events, blocking waits or bounded status checks as provided by the host.

Historical evidence: a Windows Codex CLI 0.170.0 two-round run was recorded in the 2026-11-27 review; Claude Code 2.1.327 help and vendor docs were inspected. Those observations do not establish current-version compatibility, a live macOS run, or E2E acceptance of every native-host recipe. Step 0 and Step 3 always remain with the active host.

Repair verification on the same date ran 39 tests on Windows/Python 3.12 (38 passed, one POSIX-only
skip) and WSL Linux/Python 3.12 (32 passed, seven Windows-only skips). A restricted Codex CLI +
Claude Code smoke test completed both rounds on Windows. The configured CI matrix includes
macOS/Python 3.10 and 3.13; native macOS execution remains pending. POSIX cleanup covers children
that remain in the managed process group; adapters must not daemonize or detach workers. CLI
runtime storage is outside the reviewed-workspace audit. Failure/cancellation cleanup includes a
separately bounded final audit, documented in the portable runner guide.
