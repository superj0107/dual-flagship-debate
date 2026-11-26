**A worked case, and one-command install for ~80 agents.**

```bash
npx skills add superj0107/dual-flagship-debate -g -y -a claude-code
npx skills add superj0107/dual-flagship-debate -g -y -a '*'    # every agent it detects
```

## What's new in 1.1.0

### A real decision, recorded end to end

[`examples/case-install-sync.md`](https://github.com/superj0107/dual-flagship-debate/blob/main/examples/case-install-sync.md) — should three hosts keep *copies* of this skill, or link them to one source?

- Round 1 blind: A argued "link it", B argued "keep copies" and **corrected a wrong fact in the host's own baseline**.
- Round 2: **both** sides moved. A flipped to B on new evidence; B invented a third option (link a *release worktree*, not the working copy).
- Host fact-check: four claims tested by running commands; two premises turned out false.
- Verdict: five parts, including the fork it explicitly left to the operator.

The surviving answer was neither side's opening proposal. That is what the protocol is for.

### Ecosystem install

The skills CLI recognises this repository (`Found 1 skill`), installs to `.agents/skills`, then links each
agent you name — verified with `claude-code` and `codex`. Agent names come from that CLI's own list
(~80: `claude-code`, `codex`, `cursor`, `gemini-cli`, `github-copilot`, `cline`, `roo`, `opencode`,
`windsurf`, `zed`, `warp`, `goose`, `junie`, `kiro-cli`, `qwen-code`, `openhands`, `continue`, `amp`, …).
Mind the flag: it is `claude-code`, not `claude`.

### Facts verified on hardware, not assumed

| Claim | Result |
|---|---|
| `mklink /J` needs elevation | no — worked from a non-admin shell |
| `mklink /D` needs elevation | **also worked** on that machine; the common premise did not hold |
| hosts follow a junction to `SKILL.md` | yes — Claude Code lists it in init `slash_commands`, Codex reports it present, Node resolves the link via `realpathSync` |
| host notes can live inside the repo | no — `validate_privacy()` rejects absolute home paths, so they stay outside |

## Still true, still your job

- **Read-only is only as hard as your CLI's flag**: `-s read-only`, `--permission-mode plan`, or your host's equivalent. The runner cannot verify it for you.
- **Two flagships or nothing**: single flagship → two isolated sessions labelled `模式：同旗舰双隔离`; never a mini/flash/haiku/lite stand-in, never both sides in one context.
- **Installing is not adapting**: the per-host pages in [`hosts/`](https://github.com/superj0107/dual-flagship-debate/tree/main/hosts) exist because no install format encodes read-only enforcement or two-debater dispatch.

MIT.
