# Model Pairing & Host Dispatch Reference

Last Verified: 2026-11-26

> [!WARNING]
> **Non-Normative Point-in-Time Snapshot (`2026-11-26`)**: Treat all model identifiers below as dated examples only. Model releases, aliases, and availability change frequently — **always inspect your host's live model catalog before dispatching** and never skip live discovery to copy retired model IDs blindly.

## 1. Flagship Parity Selection Criteria

Before starting Round 1, verify that `Debater A` and `Debater B` satisfy all three parity rules:

1. **Equal Flagship Tier**: Both debaters must belong to the same top-capability flagship tier. Cross-vendor pairs maximize prior diversity; sibling flagships from the same vendor work well when only one subscription is active.
2. **Matched Top Reasoning Effort**: Enable the highest reasoning/thinking setting on both sides (for example `max` or `thought_level: high`). Never pit a `high`/`max` flagship against a default-low or unreasoned run.
3. **Strict Anti-Downgrade Gate (Hard Block)**:
   - If only **one** flagship model is available, auto-fallback to **two isolated read-only sessions of that same flagship** with orthogonal review lenses, and state `模式：同旗舰双隔离` on line 1 of the final verdict.
   - **Hard Block (fail loudly, never silently degrade)**: Stop and report the gap if the host cannot launch isolated read-only sub-sessions, only small/budget models (`mini`, `flash`, `haiku`, `lite`, etc.) are exposed, or symmetric top reasoning effort cannot be set. Never replace a missing peer with single-context self-roleplay.

---

## 2. Verified Flagship Pairing Examples (`2026-11-26` Snapshot)

*Rankings and capability groupings below reflect ModelDial's verified catalog snapshot as of `2026-11-26` and live provider tiers; re-check your host's current list at runtime.*

| Scenario | Debater A | Debater B | Notes |
|---|---|---|---|
| **Cross-Vendor Top Tier (Recommended)** | `gpt-6.1-sol` or `gpt-6.2-sol` (`max` / `high`) | `claude-opus-5-5` (`max`) | Strongest prior diversity across vendors |
| **Origin Default (Antigravity / Gemini)** | `gemini-4-neon` (`thought_level: high`) | `gemini-4-carbon` (`thought_level: high`) | Original namesake pairing of `dual-flagship-debate` |
| **OpenAI-Only Subscription** | `gpt-6.1-sol` (`max`) | `gpt-6.2-sol` (`high`), or `gpt-6.2-astra` vs `gpt-6-astra` | Two sibling OpenAI flagships in separate sessions |
| **Claude-Only Subscription** | `claude-opus-5-5` (`max`) | `claude-fable-5-1` (`max`), or second isolated `claude-opus-5-5` (`max`) | Dual isolated `claude-opus-5-5` triggers `模式：同旗舰双隔离` |
| **Multi-Model / Open-Ecosystem** | `qwen4-max` (`high` / top reasoning) | `k3.1-pro` or `grok-4.7` (top reasoning) | Evenly matched alternative flagship pair |

---

## 3. Three Host Execution Patterns

`SKILL.md` intentionally uses host-neutral primitives so the same protocol runs across stateful orchestrators, stateless subagent hosts, and ephemeral CLIs without editing skill files.

### Pattern A: Stateful Multi-Thread Hosts (Verified Example: T3 Code / Antigravity)
1. **Discover live models**: Call `orchestrator_capabilities` (with `search` if needed) to inspect live providers, model slugs, and effort options.
2. **Round 1 (Parallel Async)**: Launch two parallel read-only `delegate_task(..., role="general", mode="async")` calls targeting `Debater A` and `Debater B` (each scoped to read-only exploration and analysis).
3. **Round 2 (Original-Thread Continuation)**: Read both full Round 1 outputs, then call `t3_thread_send(mode="auto", threadId=<debater_r1_thread_id>)` in parallel for both debaters, embedding the opponent's unredacted Round 1 verbatim text.
4. **Completion**: End turn after dispatching and wait for asynchronous completion events; never poll `task_status`.

### Pattern B: Stateless Subagent Hosts (Capability Pattern: Claude Code / Cursor / OpenCode)
1. **Discover live models**: Check the host's configured agent/model selector or CLI profile catalog for two evenly matched flagships (or enable dual-isolated fallback with `模式：同旗舰双隔离`).
2. **Round 1**: Dispatch two parallel isolated read-only subagent tasks (`Debater A` and `Debater B`).
3. **Round 2 (Dual-Mode Contract)**:
   - If the host supports **resuming a specific subagent execution by ID** with intact context, send the opponent's verbatim Round 1 output via resume.
   - If subagent tasks are **stateless / one-shot** (no continuation handle), launch **two fresh isolated read-only subagents** and explicitly inject:
     ```text
     [Step 0 Shared Verified Fact Baseline]
     + [Your Own Verbatim Round 1 Output]
     + [Opponent's Unredacted Verbatim Round 1 Output]
     + [Round 2 Rules: Anti-Sycophancy, Steelman, Atomic Rebuttals, Double Crux]
     ```
   - Never collapse Round 2 into the host's single active conversation context.

### Pattern C: CLI Ephemeral Hosts (Verified Example: Codex CLI)
1. **Discover available models/profiles**: Inspect configured profiles and model availability through the CLI's native settings or help/model output before launching.
2. **Round 1**: Run two parallel read-only `codex exec --ephemeral` subprocesses with explicit read-only sandbox flags and model/effort configuration for `Debater A` and `Debater B`.
3. **Round 2**: Because `--ephemeral` runs are stateless, start two fresh parallel read-only `codex exec --ephemeral` runs injecting `[Step 0 Baseline + Own R1 Verbatim + Opponent R1 Verbatim]` cleanly from saved stdout/temp transcripts, then clean up temporary outputs.

---

## 4. Zero-Mutation Persistence & Privacy Rules

- **Never edit installed skill files**: Package managers such as `npx skills add` track folder hashes in `~/.agents/.skill-lock.json` (`skillFolderHash`), and manual installs symlink directly to the Git clone. Modifying `skills/dual-flagship-debate/SKILL.md` locally breaks lock hashes and causes `git pull` conflicts.
- **Never scan `.env` or secret stores**: Host orchestrators and discovery prompts must **not** read `.env`, credential files, or auth directories to infer API keys (which risks credential exposure and stale-key false positives). Inspect only the host's native live model catalog.
- **Pin defaults in host instruction files instead**: Add two lines to your user-level or project-level `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` (loaded automatically by the host with zero extra I/O):

```markdown
- Default `dual-flagship-debate` pair: Debater A = `<flagship-a>` (`<top-effort>`), Debater B = `<flagship-b>` (`<top-effort>`).
- Fall back to dual isolated `<flagship-a>` sessions only if the peer model is unavailable; never downgrade to mini/flash/haiku/lite.
```

---

## 5. Ready-Made Dispatch: Windows CLI Runner

`hosts/windows-cli/run-debate.ps1` implements Round 1 / Round 2 for CLI-ephemeral hosts in one
command. It is generic: no model IDs or endpoints baked in — model selection is left to each CLI's
own configuration, or passed via `-CodexModel` / `-ClaudeModel`.

```powershell
powershell -ExecutionPolicy Bypass -File hosts\windows-cli\run-debate.ps1 `
  -TopicFile .\topic.md -Mode cross-vendor -Rounds 2
```

| Flag | Meaning |
|---|---|
| `-Mode cross-vendor` | Debater A = Codex CLI, Debater B = Claude Code (cross-vendor pair) |
| `-Mode dual-codex` / `-Mode dual-claude` | Two isolated sessions of one flagship; the runner reminds you that the verdict line 1 must read `模式：同旗舰双隔离` |
| `-Rounds 1` | Blind opening only (cheap screening pass) |
| `-AppendSystemPrompt <file>` | Extra system prompt prepended / appended for the debaters |
| `-TimeoutSec 900` | Per-process cap |
| `-WorkDir <dir>` | Repo context the debaters may read |

Two behaviours worth knowing before you rely on it:

1. **Read-only is only as hard as the CLI's flag.** Codex gets a real `-s read-only` sandbox; Claude
   Code has none by default, so the runner snapshots `git status` before and after and writes
   `WORKSPACE-DIFF-WARNING.txt` if anything changed. Treat that file as a stop sign, not a receipt.
2. **The runner does not fact-check.** Verifying the debaters' new claims is the host agent's job
   (Step 3 gate); the runner only produces transcripts.
