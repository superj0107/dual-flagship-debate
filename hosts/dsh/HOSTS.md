# Host recipe — dsh (DeepSeek Harness)

Status: version-sensitive recipe based on a historical local setup; detect the actual installed host's capabilities before choosing the route.

## Load and inspect

Install the complete `dual-flagship-debate` directory, including scripts and references, into the skill root recognized by that build (the historical setup used `~/.agents/skills/`). Confirm discovery, available models/effort values, isolated task primitives, permissions and continuation behavior.

Do not generalize one local provider list into a claim that every dsh build lacks flagship subagents. If current native agents provide the required isolated read-only contexts and model settings, use them. Otherwise keep dsh as host and drive verified CLI processes.

## Self-contained CLI route

From the installed skill directory, with Python 3.10+:

```bash
# macOS / Linux; use python or py -3 on Windows
python3 scripts/run_debate.py --config debate.config.json --topic topic.md --workdir /path/to/repo --rounds 2
```

Copy/edit the [bundled config and runner](../../skills/dual-flagship-debate/references/hosts.md) after live capability checks. The repository's optional PowerShell entry point is another Windows route; installed skills need no outer repository files.

## Execution contract

Prefer two concurrent isolated sessions. On a sequential-only surface keep R1 blind and label `调度：顺序隔离`. Wait with the host's completion events, blocking waits or bounded status checks.

Verify read-only separately for the host and each child CLI, including shell, MCP/apps, hooks/plugins and inherited settings. Git checks observe changes; worktrees isolate some local losses. Neither creates a permission boundary.

Two suitable live flagships are the default. One flagship in isolated sessions uses `模式：同旗舰双隔离`; a missing native model can be supplied by another verified CLI rather than simulated in the host context. Preserve original R1 texts, source/session/hash metadata and context budget, then perform host Step 3 fact-checking before the verdict.
