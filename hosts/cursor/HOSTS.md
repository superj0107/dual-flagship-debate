# Host recipe — **Cursor**

## 1. Load the protocol

Cursor reads project rules from `.cursor/rules/*.mdc` (and increasingly `AGENTS.md`). Copy the
ready-made file and adjust:

```bash
mkdir -p .cursor/rules
curl -fsSL https://raw.githubusercontent.com/superj0107/dual-flagship-debate/main/hosts/rules-snippets/cursor.mdc \
  -o .cursor/rules/dual-flagship-debate.mdc
```

The rule tells the agent: when the task matches, read
`skills/dual-flagship-debate/SKILL.md` (clone this repo into the project, e.g. under `tools/`) and
follow the four-step protocol.

## 2. Dispatch

Cursor gives you one chat context plus **Background Agents** (separate tasks that can run on their
own branch). Two workable shapes:

- **Two chats, sequential** — Debater A in chat 1 with the Round 1 brief; new chat for Debater B with
  the same brief; then a third pass per side with both Round 1 texts pasted in (Round 2 replay).
  Cheap, no setup, but you must police the isolation yourself: never let chat 1 see chat 2's answer.
- **Background Agents ×2** — same brief, two agents, orthogonal lenses. Each returns a diff/transcript;
  treat them as the two debaters. Read-only is only as good as the agent's tool permissions.

Round 2 always uses the **stateless replay** form:
`[Step 0 baseline + own R1 verbatim + opponent R1 verbatim]`.

## 3. Read-only

Cursor's agent can edit files. Enforce read-only by one of:

- launch the debate in a **throwaway worktree** or a copy of the repo (safest, no config needed),
- switch to a read-only/ask-style mode if your build offers one,
- afterwards run `git status --porcelain` and diff before trusting the verdict.

Do not rely on "please don't modify" alone.

## 4. Model pairing

The model picker is per-chat in most builds. If only one flagship tier is selectable, run **Tier 2**:
two isolated sessions of the same flagship with orthogonal lenses, and label the verdict
`模式：同旗舰双隔离`. For **Tier 1** cross-vendor parity, run the second debater in another tool (or
via the [portable runner](../portable/README.md)) — transcripts are plain text, mixing hosts is fine.
