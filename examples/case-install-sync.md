# Case: one real decision, two rounds, five-part verdict

A worked example, kept because it shows what the protocol actually produces — including the parts
where the debaters disagreed with the host and were right.

**Decision at stake.** A machine has three agent hosts reading skill directories
(`~/.agents/skills`, `~/.codex/skills`, `~/.claude/skills`), each holding a *copy* of this skill. Should
those copies become directory links to a single source of truth, or stay copies plus a sync script?

**Setup.** Mode: dual-proposal confrontation (A vs B). Debater A = `codex-cli`, Debater B =
`claude-code`, both flagship tier, both read-only (`-s read-only` / prompt-level constraint), two rounds,
four CLI calls, 76 s wall clock. Topic file: the same seven-section Step 0 template shipped in
`examples/topic-template.md`. The host's stated lean was **B** (keep copies), and both debaters were
told to attack that lean.

---

## Round 1 — blind openings

**Debater A (codex) argued for A**, on the grounds that "failure is just re-running a script" ignores
the silent-staleness cost:

> 漏跑后副本持续过期的隐性成本被忽略。……链接兼容性可以先逐宿主验证，再切换并保留副本回滚。

**Debater B (claude) argued for B**, and corrected a fact in the host's own baseline:

> `validate_skill.py` 只校验仓库内 `SKILL_DIR`，不检查任何安装目录，所以"链接后测试仍通过"这条约束
> 对 A、B 都不构成区分，不能算 A 的加分项。

Its two load-bearing premises:

> P1：工作副本不等于发布版。链接之后，切分支、改到一半、`checkout` 旧 tag，都会立即在三个宿主上生效。
> P2：`validate_privacy()` 对 ROOT 执行 `rglob`，不跳过 `HOSTS.local.*`。这几份文件含本机绝对路径，
> 放进仓库会命中 `absolute_home_path`，测试失败。

Round 1 ended with A and B on opposite sides, each holding one premise the other had not addressed.

## Round 2 — verbatim cross-feed

**A flipped to B**, explicitly citing the new evidence:

> 对手最强的论点是：A 会让未提交的工作副本即时影响三个宿主；且把 `HOSTS.local.md` 放进仓库会触发隐私
> 检查，分散到宿主指令文件又新增同步点。`rglob` 检查和隐私文件问题是新证据，足以动摇我原先的 A。

**B moved to a conditional A′** — not a compromise, a third option it had not offered in Round 1:

> A′，即链接到专用的发布 worktree（`git worktree add` 检出发布 tag），不链接开发副本，这样 P1 就消失了。
> 升级是一条 `checkout <新tag>` 命令，回滚是 `checkout <旧tag>`。(a) 和 (b) 都实测通过才切换 A′。

Both then named the same two assumptions as decisive (Double Crux):

| Crux | Falsifier named by the debaters |
|---|---|
| (a) A junction needs no admin rights **and** all three hosts follow it to read `SKILL.md` | run one discovery check per host; any host that misses the skill falsifies it |
| (b) The host-specific notes can live outside the linked directory without adding sync points | a relative reference in `SKILL.md` would break once moved |

## Host fact-check (Step 3)

The protocol requires the host to verify, not to trust. Three checks, all run:

| Claim under test | Method | Result |
|---|---|---|
| junction needs no elevation | `mklink /J` in a scratch dir as a non-admin shell | **works** (non-admin confirmed: `IsInRole(Administrator)` = False) |
| dir symlink needs elevation here | `mklink /D` in a scratch dir | **also works** — this machine allows it; the debaters' premise was weaker than assumed |
| all three hosts follow a junction | junction placed in each skill root, then Claude Code `slash_commands` / Codex skill check / Node `fs.statSync` + `realpathSync` | **all three follow it**; Node resolved the junction to the worktree path |
| notes inside the repo would fail CI | read `validate_privacy()` and the notes' content | **confirmed** — absolute home paths trip `absolute_home_path` |

## Verdict

**① Decision.** Adopt **A′**: link each host's skill directory to a dedicated *release worktree* checked
out at a tag, and keep host-specific notes outside the repository. Implemented and verified on all three
hosts. Not "A" (linking the development copy) — that would leak half-finished edits into every agent.

**② Corrections and eliminated options.** The host's baseline was wrong in one place: the repository's own
validator says nothing about install directories, so "linked install still passes CI" was never an
argument for either side. Eliminated: linking the development working copy (P1), and copy-plus-sync-script
(when the link works, the script only maintains a problem that no longer exists — its one residual failure
mode, a forgotten sync, silently serves a stale skill).

**③ Surviving plan and guardrails.** Release worktree at a tag → junction per host. Guardrails: (i) after
every version bump, re-run the three discovery checks; (ii) host notes live outside the linked tree, in
one place per host; (iii) rollback is `git -C <worktree> checkout <previous-tag>` — no file copying, no
window where a skill is missing.

**④ Double Crux and minimum validation.** (a) was settled empirically in four minutes — worth doing before
any design debate, because both debaters were reasoning about it blind. (b) was settled by reading the
validator: put the notes outside the repo.

**⑤ Unresolved fork, left to the operator.** Codex's residual objection stands: A′ still needs release
discipline — someone must remember to `checkout` the new tag, and a forgotten checkout serves a stale
skill just like a forgotten sync. Claude's counter: the blast radius differs (stale-but-working vs
half-edited-live). Cheap mitigation nobody costed: a one-command `verify` script that asserts
`worktree HEAD == latest tag` and re-runs the discovery checks.

## What this case is worth

- The blind Round 1 produced two genuinely different designs, not two phrasings of one.
- Round 2 changed **both** sides, and the surviving answer was neither side's opening proposal.
- The host's own fact-check mattered more than either transcript: two premises ("symlinks need admin",
  "the validator covers installs") were false, and one was unfalsifiable without running a command.

## Reproduce it

```bash
python3 hosts/portable/run_debate.py --config debate.config.json \
  --topic examples/topic-template.md --rounds 2
```

Cost: four flagship calls. Keep Round 1 only (`--rounds 1`) when screening.
