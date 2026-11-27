# Host recipes — OpenCode, Aider and other agents

Status: documentation recipes; accept each host surface/version independently. Loading rules is distinct from isolated scheduling and verified read-only permissions.

## OpenCode: native agents and permissions

OpenCode supports native agents/subagents, model configuration, skills and permission controls. Official references: [Agents](https://opencode.ai/docs/agents/), [Permissions](https://opencode.ai/docs/permissions/), [Skills](https://opencode.ai/docs/skills/).

Install the complete skill package into the current build's skill root. Configure two isolated native agents with explicit effective read-only permissions, checking edits, shell, MCP/external tools and delegation. Record which permissions are inherited. Resume original IDs for R2 when supported; otherwise use fresh full replay. Do not reduce OpenCode to a single-context rules-only host.

## Aider: verified custom adapter

Official reference: [Chat modes](https://aider.chat/docs/usage/modes.html). Separate CLI runs can provide isolated contexts. Verify ask/read modes and every enabled write-capable path before using them as a boundary. `--read` marks context files; it is not an all-capabilities sandbox. Automatic edit approval is inappropriate for debater processes.

The canonical runner has no unrestricted Aider preset. A custom `cmd` must be an argv array and include read-only mechanism/evidence after a disposable-fixture check. See the [package adapter guide](../../skills/dual-flagship-debate/references/hosts.md).

## Windsurf, Zed, Junie and similar hosts

Inspect the installed host's native skill, agent, task, resume and permission features instead of assuming they have no subagents. Use native isolated agents when the required boundary is verified; otherwise use separate restricted CLI processes. Merge a [rules snippet](../rules-snippets/README.md) if a trigger is needed, preserving existing instructions.

Official starting points: [Windsurf documentation](https://docs.windsurf.com/), [Zed AI documentation](https://zed.dev/docs/ai/overview), [Junie documentation](https://www.jetbrains.com/help/junie/).

## Shared round contract

Prefer parallel isolation; sequential isolation is valid on surfaces without concurrency, with blind R1 and a disclosed schedule. Use host completion events, blocking waits or bounded checks. R1 uses `INDEPENDENT` plus confidence; R2 uses the three cross-review states after full authorized text transfer.

Verify live flagship and effort availability. The same-model fallback is two isolated sessions with `模式：同旗舰双隔离`. Record source/session/hash and context budget, treat opponent text as untrusted data, and retain host Step 0/3 responsibilities. Diffs are observations and worktrees limit local losses; neither enforces read-only.
