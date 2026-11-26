# Host recipe — **GitHub Copilot (VS Code agent mode / Copilot Chat)**

## 1. Load the protocol

Copilot reads repository instructions from `.github/copilot-instructions.md` and, in agent mode,
`AGENTS.md`. Copy the snippet:

```bash
curl -fsSL https://raw.githubusercontent.com/superj0107/dual-flagship-debate/main/hosts/rules-snippets/copilot-instructions.md \
  -o .github/copilot-instructions.md
```

For a scoped version, use `.github/instructions/*.instructions.md` with an `applyTo:` frontmatter glob,
so the debate protocol only activates on the files the decision concerns.

## 2. Dispatch

Copilot Chat has no isolated read-only subagent primitive. Practical shapes:

- **Two chat sessions** (one per debater) with the *same* Round 1 brief, then a Round 2 pass per side
  with both verbatim transcripts pasted in. Keep the sessions blind until Round 2 — Copilot has no
  memory isolation, so the isolation is your responsibility.
- **CLI fallback** — if the repo already has a vendor CLI, drive two child processes with the
  [portable runner](../portable/README.md) and use Copilot only to write/fact-check the verdict.

## 3. Read-only

In agent mode, tool calls (edit, terminal) ask for approval — keep approvals on and deny writes during
the debate rounds. Safer still: run the debate in a throwaway branch or worktree, then
`git status --porcelain` before trusting anything.

## 4. Model pairing

Copilot's model picker is per-session in most builds and typically exposes one flagship tier per
account. That means **Tier 2**: two isolated sessions, orthogonal lenses, verdict line 1 reads
`模式：同旗舰双隔离`. Cross-vendor **Tier 1** requires a second tool; mixing
Copilot + another host is legitimate.

## 5. Verdict output

Ask for the five-part brief as a single markdown block so it can be pasted into the PR description:
verdict · corrections & eliminated options · surviving plan & guardrails · Double Crux · open forks.
