# Changelog

All notable changes to this project. Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
versions use [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-11-26

First public release.

### Protocol (`skills/dual-flagship-debate/`)

- Two-flagship adversarial debate protocol as a host-neutral `SKILL.md` (63 lines, no vendor names,
  no model IDs, no CLI verbs — enforced by the validator).
- Three-tier model parity gate: two flagships at max reasoning → single flagship in two isolated
  sessions labelled `模式：同旗舰双隔离` → hard block when neither is possible.
- Anti-sycophancy contract: isolated Round 1, `CONVERGED` / `SHIFTED` / `MAINTAINING_DISSENT` stance
  tags, no stance change without new evidence, Steelman-before-rebuttal, atomic rebuttals across five
  flaw classes, Pre-Mortem + inversion, Double Crux extraction, two-round cap.
- Four selectable debate modes: blind independent → cross-attack, dual-proposal confrontation,
  dynamic tension axes, advocate vs Pre-Mortem red team.
- Four-step orchestration ending in a five-part decision brief, with a mandatory host-side fact-check
  gate before the verdict.
- `references/models-and-hosts.md`: parity criteria, dated (non-normative) pairing examples, three
  host dispatch patterns, and zero-mutation persistence rules.

### Host adapters (`hosts/`)

- Host matrix answering, per host, how the protocol is loaded, whether isolated read-only subagents
  exist, and how read-only is enforced.
- Recipes for Claude Code, Codex CLI, Gemini CLI, Cursor, GitHub Copilot (VS Code), Cline / Roo Code,
  opencode / Aider / Windsurf / Zed / JetBrains, and dsh (DeepSeek Harness).
- `hosts/rules-snippets/`: one canonical trigger block plus drop-in files for `AGENTS.md`,
  `.cursor/rules/*.mdc`, `.github/copilot-instructions.md`, `.clinerules`, `.windsurfrules`,
  `CONVENTIONS.md` — so rules-file hosts work without native skill support.
- `hosts/portable/run_debate.py`: config-driven runner for any two CLIs on any OS (stdin briefs,
  `{out}` / `{prompt}` / `{workdir}` substitution, Windows `.cmd` shim handling, parallel rounds,
  `git status` read-only guard, presets for codex / claude / gemini / aider).
- `hosts/windows-cli/run-debate.ps1`: the same two rounds with native PowerShell ergonomics.

### Examples & tooling

- `examples/topic-template.md`: Step 0 baseline template separating verified facts from unverified
  assumptions, with the four modes and a "host's own lean" slot.
- `tests/validate_skill.py`: asserts the skill name and directory agree, the frontmatter contract,
  model/host agnosticism of `SKILL.md`, required protocol markers, reference-file freshness, repository
  layout, license completeness, and privacy hygiene (no home paths, private IPs, personal emails or
  token prefixes).
- GitHub Actions workflow running the validator on every push and pull request.

### Verified environments

- Windows 11 + PowerShell 5.1, Codex CLI 0.170.0, Claude Code 2.1.327.
- Round 1 parallel dispatch measured at 29–80 s for two flagship CLIs; a full two-round debate is four
  flagship calls.

### Known limitations

- The Claude Code adapter cannot enforce read-only at the host level; it relies on permission modes or
  a tool allow-list, plus a post-run diff check.
- Rules-file hosts (Cursor, Copilot, Cline, Windsurf, Zed, JetBrains) have no isolated subagent
  primitive in most builds; two chats/tasks are only as blind as the operator keeps them.
- A CLI whose own config defaults to full filesystem access is only read-only if your `cmd` passes its
  read-only flag — the runner cannot verify that.
