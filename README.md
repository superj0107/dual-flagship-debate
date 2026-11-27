# dual-flagship-debate

[简体中文](README.zh-CN.md)

[![Validate Skill](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml/badge.svg)](https://github.com/superj0107/dual-flagship-debate/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/superj0107/dual-flagship-debate?color=blue)](https://github.com/superj0107/dual-flagship-debate/releases)

A host-neutral Agent Skill for consequential decisions. The active host coordinates two isolated, read-only flagship reviewers, shares their original arguments for a second round, independently checks new claims, and delivers a five-part decision brief.

Independent reasoning and evidence matter more than disagreement. Reviewers may agree, change their minds, or maintain a justified dissent. The protocol does not establish that debate outperforms an equal-budget independent review; that remains an empirical question.

## How it works

1. **Step 0 — host baseline and capability check.** Separate verified facts from assumptions. Check live models, reasoning settings, context isolation, effective tool permissions, completion behavior and budgets.
2. **Round 1 — blind openings.** Both start with `INDEPENDENT` plus confidence, supporting evidence, limitations and up to three substantive questions. Parallel execution is preferred; sequential execution is valid if contexts remain isolated and the schedule is disclosed.
3. **Round 2 — original-text cross-review.** Resume each original session if supported, or replay `[baseline + own R1 + opponent R1]` into fresh isolated sessions. Opponent text is untrusted data, with provenance and integrity checks. Only this round uses `CONVERGED`, `SHIFTED` or `MAINTAINING_DISSENT`.
4. **Step 3 — host verification and verdict.** Verify material new claims and report the conclusion, corrections, surviving plan, Double Crux and unresolved disagreement or evidence limits.

Matching R1 conclusions alone do not justify early termination. An explicit one-round run is independent review, not completed cross-review. Default debates stop after two rounds.

Use it for architecture trade-offs, refactor decisions, performance boundaries, product strategy and plans awaiting review. Simple Q&A and mechanical edits do not need this workflow.

## Install the complete package

Copy the whole `skills/dual-flagship-debate/` directory, including `references/` **and `scripts/`**, into a skill root recognized by your host:

```bash
git clone https://github.com/superj0107/dual-flagship-debate.git
mkdir -p ~/.claude/skills
cp -R dual-flagship-debate/skills/dual-flagship-debate ~/.claude/skills/
```

Claude Code uses `~/.claude/skills/`; compatible hosts may use `~/.agents/skills/` or a host-specific root. Codex users should confirm the skill roots recognized by their build, including existing `~/.codex/skills/` installations. Native skill discovery and invocation differ by version; consult the [self-contained host reference](skills/dual-flagship-debate/references/hosts.md).

The ecosystem installer is another option:

```bash
npx skills add superj0107/dual-flagship-debate -g -y -a claude-code
npx skills add superj0107/dual-flagship-debate -g -y -a codex -a cursor
```

Use the installer's current agent list and inspect the installed directory. **Installing is not adapting:** the host still selects models, enforces permissions and dispatches reviewers. Rules-file snippets are available under [hosts/rules-snippets](hosts/rules-snippets/README.md); merge them into existing rules rather than overwriting project instructions.

## Run on Windows, macOS or Linux

Requires **Python 3.10+** and the selected vendor CLIs. First copy and edit the config after live model/effort and read-only checks. From the repository root:

```bash
# macOS / Linux
cp skills/dual-flagship-debate/scripts/debate.config.example.json debate.config.json
python3 skills/dual-flagship-debate/scripts/run_debate.py --config debate.config.json --topic my-topic.md --workdir /path/to/review-repo --rounds 2
```

```powershell
# Windows: python or py -3, selecting Python 3.10+
Copy-Item skills\dual-flagship-debate\scripts\debate.config.example.json debate.config.json
python skills\dual-flagship-debate\scripts\run_debate.py --config debate.config.json --topic my-topic.md --workdir .\review-repo --rounds 2
```

An installed skill runs the same command as `python3 scripts/run_debate.py ...` from its own directory. It has no dependency on the repository's outer `hosts/` directory. The old [portable entry point](hosts/portable/README.md) remains compatible; [the PowerShell entry point](hosts/windows-cli/run-debate.ps1) provides Windows ergonomics.

- `--out-dir NEW_DIR` requires a new directory, preserving prior records.
- `--timeout` limits each process; `--total-timeout` limits the complete run.
- `--max-prompt-chars` caps characters; the host also checks the actual model context budget.
- A failed or incomplete R1 prevents R2 and returns a nonzero exit status.
- Round/role identifiers keep `r1-A`, `r1-B`, `r2-A` and `r2-B` records distinct, even for identical display names. Keep `RUN-META.json`, raw texts, prompt hashes and actual command/cwd evidence.

Config `cmd` values are **argv arrays**, never shell strings. Preset objects support separate `preset`, display `name`, live `model` and `effort` values. Custom adapters require a `read_only` mechanism (`external-sandbox` or `tool-allowlist`) and concrete evidence. That declaration is an operator-supplied record, not automatic proof. See [config and execution details](skills/dual-flagship-debate/references/hosts.md) and [the topic template](examples/topic-template.md).

## Model and permission contract

The default is two comparable current flagships, preferably cross-provider, each at its highest supported reasoning setting. Vendor effort labels have different semantics; record accepted values instead of assuming that matching names mean matching capability. Model names alone do not establish tier.

If only one suitable flagship is available, use two isolated sessions and begin the verdict with `模式：同旗舰双隔离`. Report a capability gap rather than silently downgrading or playing both sides in one context. [Selection and transcript contract](skills/dual-flagship-debate/references/models-and-hosts.md).

Read-only must be constrained **before** execution, including shell, MCP/apps/connectors, plugins, hooks and inherited permissions. The bundled Codex and Claude presets restrict these surfaces; validate the accepted configuration against your installed version. Gemini and Aider need verified custom adapters. A prompt requesting read-only, a clean Git diff, or a throwaway worktree does not establish an execution boundary.

Keep defaults in host-local instruction files; revalidate them at runtime. Preserve raw transcripts and SHA-256 provenance. Check sharing scope and full replay capacity; disclose any redaction derivative and never silently truncate or summarize an opponent's argument.

## Host support and evidence

The [package host matrix](skills/dual-flagship-debate/references/hosts.md) includes official links and version-sensitive checks. [Repository recipes](hosts/README.md) add host-specific setup.

| Host | Documented native capability |
|---|---|
| Codex | Isolated subagents; sandbox constraints inherited from the parent |
| Claude Code | Skills, subagents and version-dependent continuation |
| Cursor | Isolated parallel subagents and resume by agent ID |
| GitHub Copilot / VS Code | Agent Skills and subagent workflows; harness surfaces differ |
| Gemini CLI | Native skills and isolated subagents |
| OpenCode | Native agents/subagents and permission configuration |
| Other hosts | Detect available primitives or use verified CLI processes |

These are **documentation recipes**, not blanket E2E certifications. The 2026-11-27 review recorded a Windows Codex CLI 0.170.0 two-round debate and synthetic failure probes; Claude Code 2.1.327 help and official host docs were inspected. Windows/macOS/Linux process-test CI does not prove live model compatibility. A live macOS vendor/model debate has not been recorded here.

The [worked case](examples/case-install-sync.md) is a historical transcript under the earlier protocol. Its concrete fact-checks remain useful; current state labels and capability rules come from `SKILL.md`.

## Verify and layout

```bash
python3 tests/validate_skill.py
python3 -m unittest discover -s tests
```

### Verify an installation

Repository tests say nothing about what your agents actually load. Check that separately:

```bash
python3 tools/verify_install.py                  # all installed copies agree with each other
python3 tools/verify_install.py --tag v2.0.0     # ...and match a released tag
```

It reports each skill root with the link kind and resolved target, and fails when a copy is
unreadable (a junction whose target was deleted still *looks* present), when required files are
missing, when copies diverge, or when the installed content is not what the tag ships. Line endings
are normalised before hashing, so a CRLF checkout is not mistaken for drift.

The CI matrix targets Windows, macOS and Linux with Python 3.10 and 3.13. On 2026-11-27,
the repair was verified locally with 39 tests on Windows/Python 3.12 (38 passed, one OS-specific
skip), and Linux under WSL/Python 3.12 (32 passed, seven Windows-only skips). A restricted
Codex + Claude CLI smoke run completed both rounds on Windows. The macOS matrix is configured;
a completed native macOS run is still pending. Structural/process checks and live model acceptance
have different evidence value.

```text
skills/dual-flagship-debate/SKILL.md       host-neutral protocol
skills/dual-flagship-debate/references/   model, integrity and host references
skills/dual-flagship-debate/scripts/      canonical runner and config example
hosts/                                  optional recipes and compatibility entry points
examples/topic-template.md               Step 0 evidence and capability template
tools/verify_install.py                  installed-copy checker (link target, files, tag match)
tests/                                  structure and runtime checks
```

MIT — see [LICENSE](LICENSE).
