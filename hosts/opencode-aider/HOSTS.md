# Host recipe — **opencode / Aider / Windsurf / Zed / JetBrains**

Grouped because the mechanism is the same: an instruction file plus one chat context. None of them
needs anything special from this repository beyond that file and a readable copy of `SKILL.md`.

| Host | Instruction file | Notes |
|---|---|---|
| **opencode** | `AGENTS.md` (project root), plus `.opencode/` config | supports custom agents/prompts in newer builds — if it can run two agents, use them as A and B |
| **Aider** | `CONVENTIONS.md` (`aider --read CONVENTIONS.md`) | CLI, one model per run → two runs make two isolated debaters |
| **Windsurf** | `.windsurf/rules/*.md` or `.windsurfrules` | Cascade may act autonomously — set write permissions off |
| **Zed** | `AGENTS.md` / `.rules` | agent panel; one context |
| **JetBrains AI / Junie** | project instructions file per the plugin docs | same shape |

## 1. Load the protocol

```bash
# Aider example
curl -fsSL https://raw.githubusercontent.com/superj0107/dual-flagship-debate/main/hosts/rules-snippets/CONVENTIONS.md \
  -o CONVENTIONS.md
# generic AGENTS.md (opencode / Zed / others)
curl -fsSL https://raw.githubusercontent.com/superj0107/dual-flagship-debate/main/hosts/rules-snippets/AGENTS.md \
  -o AGENTS.md
```

Keep `skills/dual-flagship-debate/` in the repo (or clone it under `tools/`) so the agent can read the
protocol when the rule fires.

## 2. Dispatch

- **Aider / any CLI**: two runs *are* two isolated debaters. This is the cleanest Tier 1 route —
  `aider --read CONVENTIONS.md -m "<round 1 brief>"` twice, or with different `--model` values.
- **Windsurf / Zed / JetBrains**: one context, so run Round 1 in one session per debater, and Round 2
  as a replay with both transcripts pasted in. Do not let one session see the other until Round 2.

## 3. Read-only

- Aider: run with `--read` files and no `--yes`-style auto-apply during debate rounds; or run it in a
  throwaway worktree.
- Windsurf / Zed / JetBrains: turn off auto-apply / terminal auto-run; verify with
  `git status --porcelain` afterwards.

## 4. Model pairing

CLI hosts make Tier 1 trivial (`--model` per run). IDE-only hosts usually give Tier 2; if the picker
offers a second vendor at flagship tier, use it and you are back at Tier 1.
