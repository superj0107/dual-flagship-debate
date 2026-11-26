**Two-flagship adversarial debate as an Agent Skill** — two isolated read-only flagship debaters,
verbatim cross-feed, host-side fact-check, five-part decision brief.

```bash
git clone https://github.com/superj0107/dual-flagship-debate.git
cp -r dual-flagship-debate/skills/dual-flagship-debate ~/.claude/skills/   # or ~/.codex/skills, ~/.agents/skills
```

## What's in 1.0.0

**Protocol** — host-neutral `SKILL.md` (63 lines, zero vendor names or model IDs, enforced by CI):
isolated Round 1 → verbatim Round 2 → mandatory fact-check → five-part verdict. Three-tier parity
gate that hard-blocks silent downgrades, anti-sycophancy stance tags, Steelman + atomic rebuttals,
Pre-Mortem + inversion, Double Crux, four debate modes, two-round cap.

**Hosts** — one matrix plus recipes for everything mainstream:

| | |
|---|---|
| Native skill | Claude Code · Codex CLI · dsh (DeepSeek Harness) |
| Rules file | Cursor · GitHub Copilot (VS Code) · Cline / Roo Code · opencode · Aider · Windsurf · Zed · JetBrains |
| Any CLI | portable runner, config-driven, Windows / macOS / Linux |

`hosts/rules-snippets/` gives you drop-in files for `AGENTS.md`, `.cursor/rules/*.mdc`,
`.github/copilot-instructions.md`, `.clinerules`, `.windsurfrules`, `CONVENTIONS.md`.

**Runners** — two, same two rounds:

```bash
# any two CLIs, any OS
python3 hosts/portable/run_debate.py --config debate.config.json --topic my-topic.md --rounds 2
```
```powershell
# native Windows
powershell -ExecutionPolicy Bypass -File hosts\windows-cli\run-debate.ps1 -TopicFile .\my-topic.md -Rounds 2
```

Both feed briefs on stdin, run the two rounds in parallel, and snapshot `git status` so you can see
whether a debater wrote anything.

**Tooling** — `examples/topic-template.md` (Step 0 baseline: verified facts vs unverified assumptions),
`tests/validate_skill.py` (contract, agnosticism, layout, license, privacy), GitHub Actions on every push.

## Verified on

Windows 11 · PowerShell 5.1 · Codex CLI 0.170.0 · Claude Code 2.1.327. Round 1 parallel dispatch
measured at 29–80 s; a full two-round debate is four flagship calls.

## Read this before trusting it

- **Read-only is only as hard as your CLI's flag.** The runner cannot make a CLI read-only — pass
  `-s read-only` (Codex), `--permission-mode plan` (Claude Code), or your host's equivalent.
- **Rules-file hosts are blind only while you keep them blind.** Two chats/tasks have no isolation
  primitive; paste transcripts manually at Round 2.
- **Two flagships or nothing.** If only one flagship tier is available, run two isolated sessions of it
  and label the verdict `模式：同旗舰双隔离`. Never substitute a mini/flash/haiku/lite model, and never
  simulate both sides in one context.

Full detail: [CHANGELOG.md](https://github.com/superj0107/dual-flagship-debate/blob/main/CHANGELOG.md) ·
[hosts/README.md](https://github.com/superj0107/dual-flagship-debate/blob/main/hosts/README.md)

MIT.
