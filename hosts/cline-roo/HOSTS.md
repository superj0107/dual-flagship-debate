# Host recipe — **Cline / Roo Code**

Both are VS Code agent extensions with explicit per-tool auto-approve switches, which makes them the
easiest rules-file host to keep read-only.

## 1. Load the protocol

| Extension | Instruction file |
|---|---|
| Cline | `.clinerules` (file or directory) |
| Roo Code | `.roo/rules/*.md` or project `.roo/rules-<mode>/` |

```bash
curl -fsSL https://raw.githubusercontent.com/superj0107/dual-flagship-debate/main/hosts/rules-snippets/clinerules.md \
  -o .clinerules
```

Install the skill directory next to it (e.g. `tools/dual-flagship-debate/skills/...`) so the agent can
read `SKILL.md` when the protocol triggers.

## 2. Read-only (the good part)

Both extensions expose explicit toggles. Before Round 1:

- **Auto-approve OFF** for *Edit files*, *Execute commands*, *Browser actions*.
- Leave **Read files** on — debaters must read the repo to fact-check their own claims.
- After each round, check the workspace diff; a written file means the toggle drifted, so re-run.

## 3. Dispatch

No isolated subagent primitive. Two shapes:

- Two extension tasks (or two windows) with the same Round 1 brief; Round 2 per side with both
  verbatim transcripts pasted in. Blindness is your responsibility.
- Better for parity: one side in Cline, the other via a CLI (`codex exec -s read-only`,
  `claude -p`) using the [portable runner](../portable/README.md). Cross-tool pairs are allowed and
  often stronger than two sessions of the same model.

## 4. Model pairing

Each extension has its own provider/model picker, so you can genuinely reach **Tier 1** cross-vendor
parity here: e.g. one side pointed at one vendor's flagship, the other at a different vendor's
flagship, both at max reasoning. Verify the live model list in the extension settings rather than
trusting any dated table.
