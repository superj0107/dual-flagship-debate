# Changelog

All notable changes to this project. Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
versions use [Semantic Versioning](https://semver.org/).

## [2.0.0] — 2026-11-27

### Breaking

- **R1 vocabulary**: debaters now open with `INDEPENDENT` plus confidence; `CONVERGED` /
  `SHIFTED` / `MAINTAINING_DISSENT` are Round 2 only. Transcripts produced against the 1.x text do
  not satisfy the contract. Matching opening conclusions no longer justify stopping after Round 1.
- **Runner config**: a custom `cmd` now requires a `read_only` declaration
  (`external-sandbox` or `tool-allowlist`) with verification evidence; the `gemini-cli` and
  `aider` presets were removed in favour of verified custom adapters.
- **Runner location**: the canonical runner lives inside the skill directory
  (`skills/dual-flagship-debate/scripts/run_debate.py`); `hosts/portable/run_debate.py` is a
  compatibility shim.

### Added

- `tools/verify_install.py`: verifies that every installed copy is readable (catches broken
  junctions, which still report as existing on Windows), complete (including `scripts/`),
  self-consistent, and — with `--tag` — byte-identical to a released tag. Line endings are
  normalised before hashing, so a CRLF checkout is not mistaken for drift.
- `tests/test_verify_install.py`: eight cases covering consistency, missing files, divergent
  copies, frontmatter/directory mismatch, unreleased content against a tag, and unresolvable tags.### Changed

- R1 now declares `INDEPENDENT` plus confidence. R2 alone declares `CONVERGED`, `SHIFTED`, or
  `MAINTAINING_DISSENT`; matching opening conclusions do not justify early termination.
- Evidence-based agreement is valid. Questions and rebuttals have no conflict quota. Parallel
  isolation is preferred, with explicitly labelled sequential isolation for hosts without concurrency;
  completion events, blocking waits and bounded status checks are valid host primitives.
- Model selection records live capability, accepted effort semantics, isolation and effective tool
  permissions. Names alone do not establish capability. Workspace diffs are observations and
  worktrees limit local losses; neither establishes a read-only execution boundary.
- Original cross-feed is treated as untrusted data, with source, hash, integrity, sharing-scope and
  context-budget checks. The active host retains Step 0 selection and Step 3 fact-checking.
- Installation now includes the canonical `scripts/run_debate.py`, its example config and the
  self-contained `references/hosts.md` inside the skill directory. The outer portable path is a
  compatibility entry point. Minimum Python is 3.10, with Windows/macOS/Linux execution instructions.
- Runtime records use round/role keys, preserve command/cwd and hash metadata, require fresh output
  directories, validate R1 before R2, reject command strings in favor of argv arrays, and expose
  per-process, whole-run and prompt-character budgets. Custom adapters declare read-only evidence.
- Read-only presets constrain tool/integration surfaces; Gemini and Aider use verified custom
  adapters. Native subagent capabilities and official references were refreshed for Codex, Cursor,
  Copilot/VS Code, Gemini and OpenCode.

### Evidence and scope corrections

- Repair validation on 2026-11-27: Windows/Python 3.12 ran 39 tests (38 passed, one POSIX-only
  skip); WSL Linux/Python 3.12 ran 39 tests (32 passed, seven Windows-only skips). A restricted
  Codex CLI + Claude Code two-round smoke run completed on Windows. Native macOS execution
  remains pending; the CI matrix includes macOS alongside Windows and Linux.
- Regression coverage includes same-name role isolation, verbatim BOM/newline preservation,
  failed-round gating, fresh output directories, explicit cwd, bounded capability probes,
  blocked stdin, process-group/Job cleanup, cancellation, content audits, and standalone installs.
- Host pages distinguish vendor documentation recipes from version-specific end-to-end tests.
  Codex native subagents inherit parent sandbox constraints; context isolation alone is insufficient.
- The 2026-11-27 review records a Windows Codex CLI 0.170.0 debate and synthetic runtime probes;
  Claude Code 2.1.327 help and vendor documentation were inspected. This does not certify every host,
  current version, or live macOS model run. The CI matrix targets Windows/macOS/Linux on Python
  3.10 and 3.13 using synthetic processes, separately from live vendor acceptance.
- Historical release notes and the worked transcript below describe the earlier implementation;
  current permissions, status labels and host capabilities are defined by the current skill and
  references, rather than those historical statements.

## [1.1.0] — 2026-11-26

### Added

- `examples/case-install-sync.md`: a full worked case — one real decision, two rounds, both debaters
  changing position, four host-side fact-checks, five-part verdict.
- README "What it looks like" section quoting Round 2 verbatim, in both languages.
- Ecosystem install path: `npx skills add superj0107/dual-flagship-debate -g -y -a <agent>`, verified
  end to end (the CLI reports `Found 1 skill`, installs to `.agents/skills`, then links into the named
  agents), with the current agent-name list documented in both READMEs and `hosts/README.md`.

### Verified

- Directory junctions (`mklink /J`) need no elevation on the tested machine, and all three hosts follow
  them when reading `SKILL.md`: Claude Code lists the skill in the init `slash_commands`, Codex reports
  it present, and Node (the runtime under dsh/Codex) resolves `fs.statSync`/`realpathSync` through the
  link.
- `mklink /D` (directory symlink) also succeeded without elevation on that machine — the "symlinks need
  admin" premise did not hold there.
- `validate_privacy()` does reject host-specific notes placed inside the repository (absolute home
  paths), which is why such notes stay outside it.
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
