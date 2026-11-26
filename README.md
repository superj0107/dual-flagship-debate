# dual-flagship-debate

[简体中文](README.zh-CN.md)

[![Validate Skill](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml/badge.svg)](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml)

A **two-flagship adversarial debate Agent Skill** (`SKILL.md`). Instead of letting one LLM agree with
a draft or settle on lukewarm consensus, the active host agent runs up to two isolated read-only
rounds between two **evenly matched flagship models**, cross-feeds unredacted responses, fact-checks
new claims itself, and delivers a five-part decision brief.


## Why bother

- **Anti-sycophancy by structure** — Round 1 runs in complete isolation; debaters must tag
  `CONVERGED` / `SHIFTED` / `MAINTAINING_DISSENT` and cannot abandon a stance without citing new
  evidence or a counter-example.
- **Parity gate with a hard block** — two flagships at top reasoning effort, or a documented
  single-flagship fallback (`模式：同旗舰双隔离`). It refuses to silently degrade to `mini` / `flash` /
  `haiku` / `lite`, or to one model role-playing both sides.
- **Steelman + atomic rebuttals + Pre-Mortem** — every counter first restates the opponent's
  strongest premise, then attacks via `Claim → Flaw Type → Counter` across five flaw classes.
- **Dual-mode Round 2** — continue the original thread on stateful hosts, or replay
  `[Step 0 baseline + own R1 + opponent R1]` into fresh isolated sessions on stateless hosts.
- **Mandatory fact-check gate** — the host verifies newly asserted paths, configs, metrics or rules
  before the verdict, and overrides false claims.

Use it for architecture trade-offs, refactor-vs-patch decisions, security/perf boundaries,
product strategy, pricing-vs-trust, and any plan awaiting sign-off. Do not use it for factual Q&A,
one-line fixes, or mechanical execution already decided.

## Install

The skill is a directory with `SKILL.md` plus `references/`. Copy
`skills/dual-flagship-debate/` into your host's skill root:

| Host | Skill root | Then invoke with |
|---|---|---|
| **dsh** (DeepSeek Harness) | `~/.agents/skills/` | name it in the prompt; the host loads it |
| **Codex CLI** | `~/.codex/skills/` | `use the dual-flagship-debate skill: ...` |
| **Claude Code** | `~/.claude/skills/` | `/dual-flagship-debate <topic>` |
| Cursor / OpenCode / others | wherever the host scans `SKILL.md` | name it in the prompt |

```bash
git clone https://github.com/superj0107/dual-flagship-debate.git
cp -r dual-flagship-debate/skills/dual-flagship-debate ~/.claude/skills/
```

Do **not** edit the installed `SKILL.md` if your host tracks skill hashes; put local defaults in
`AGENTS.md` / `CLAUDE.md` instead (see [Pinning a default pair](#pinning-a-default-pair)).

## Model pairing

Pick two models in this order:

1. **Tier 1 — two flagships at max reasoning** (cross-vendor preferred). Example pairs and rules:
   [`references/models-and-hosts.md`](skills/dual-flagship-debate/references/models-and-hosts.md).
2. **Tier 2 — single flagship, two isolated sessions** with orthogonal lenses; label line 1 of the
   verdict `模式：同旗舰双隔离`.
3. **Tier 3 — hard block.** Only small/budget models available, or no isolated read-only sessions,
   or asymmetric reasoning effort → stop and report the gap. Never fake a debate in one context.

Model IDs change constantly: inspect your host's **live** catalog, never copy a dated example.

## Host dispatch

Three patterns are documented in the reference: stateful multi-thread hosts, stateless subagent
hosts, and CLI-ephemeral hosts. Concrete recipes per host live in [`hosts/`](hosts):

- [`hosts/dsh/HOSTS.md`](hosts/dsh/HOSTS.md) — orchestrator has no flagship subagents → drive the CLIs
- [`hosts/codex/HOSTS.md`](hosts/codex/HOSTS.md) — `codex exec -s read-only --ephemeral`
- [`hosts/claude-code/HOSTS.md`](hosts/claude-code/HOSTS.md) — `claude -p` or native subagents
- [`hosts/windows-cli/run-debate.ps1`](hosts/windows-cli/run-debate.ps1) — Round 1 parallel blind
  dispatch → Round 2 stateless replay, with a read-only guard

```powershell
# fill examples/topic-template.md first, then:
powershell -ExecutionPolicy Bypass -File hosts\windows-cli\run-debate.ps1 `
  -TopicFile .\my-topic.md -Mode cross-vendor -Rounds 2
```

Two rules that actually matter in practice:

- **Read-only must be enforced by the dispatcher**, not requested politely. Pass the host's
  read-only switch (`-s read-only`, `--permission-mode plan`, restricted tool list). A CLI whose
  config defaults to full access will happily write files otherwise.
- **Round 2 on stateless CLIs needs a fresh process** with both Round 1 transcripts pasted in. Never
  collapse two debaters into one context.

## Pinning a default pair

Add to your `AGENTS.md` / `CLAUDE.md` (no skill files touched):

```markdown
- Default `dual-flagship-debate` pair: Debater A = `<flagship-a>` (`<top-effort>`), Debater B = `<flagship-b>` (`<top-effort>`).
- Fall back to dual isolated `<flagship-a>` sessions only if the peer model is unavailable; never downgrade to mini/flash/haiku/lite.
```

## Layout

```
skills/dual-flagship-debate/SKILL.md      the protocol (load this)
skills/dual-flagship-debate/references/   model pairing + host patterns
hosts/                                    per-host dispatch recipes + Windows runner
examples/topic-template.md                Step 0 baseline template
tests/validate_skill.py                   structure / contract / privacy checks
```

## Verify

```bash
python3 tests/validate_skill.py
```

## License

MIT — see [LICENSE](LICENSE).
