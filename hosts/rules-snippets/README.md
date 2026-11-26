# Rules snippets — one block, every rules-file host

Hosts without native `SKILL.md` support still follow the protocol reliably: give them a rule that
(a) tells them when to fire and (b) points at the protocol file. Below is the canonical block; the
per-host files in this directory wrap it in the right filename and frontmatter.

| File | Drop-in target |
|---|---|
| [`AGENTS.md`](AGENTS.md) | repo root — opencode, Zed, Codex, dsh projects, generic |
| [`cursor.mdc`](cursor.mdc) | `.cursor/rules/dual-flagship-debate.mdc` |
| [`copilot-instructions.md`](copilot-instructions.md) | `.github/copilot-instructions.md` |
| [`clinerules.md`](clinerules.md) | `.clinerules` (Cline) or `.roo/rules/dual-flagship-debate.md` |
| [`windsurfrules.md`](windsurfrules.md) | `.windsurf/rules/dual-flagship-debate.md` |
| [`CONVENTIONS.md`](CONVENTIONS.md) | Aider (`aider --read CONVENTIONS.md`) |

## Canonical block

```markdown
## Adversarial debate (dual-flagship-debate)

When the task is a non-trivial decision — architecture trade-off, refactor-vs-patch, security or
performance boundary, data/metric definition, product or pricing strategy, or a plan awaiting
sign-off — and NOT simple Q&A or mechanical execution already decided, run the two-flagship
adversarial debate protocol:

1. Read `SKILL.md` under `skills/dual-flagship-debate/` (or `tools/dual-flagship-debate/skills/...`)
   and follow it exactly: Step 0 baseline → Round 1 blind openings → Round 2 verbatim cross-feed →
   host fact-check → five-part verdict.
2. Two isolated debaters only. If two isolated read-only sessions cannot be run, stop and name the
   missing capability. Never simulate both sides in one context.
3. Both debaters must be top-tier flagship models at maximum reasoning. If only one flagship is
   available, run two isolated sessions of it and label line 1 of the verdict `模式：同旗舰双隔离`.
   Never substitute a mini/flash/haiku/lite model.
4. Debaters are read-only: no file edits, no git writes, no installs. Enforce it in your permission
   settings, then confirm with `git status --porcelain` before trusting the result.
5. Verify newly asserted facts yourself before the verdict (paths, configs, metrics, external rules).
   Anything you could not check is written as "unverified premise".
```

## Adjusting it

- **Path**: if the skill lives elsewhere, edit the path in clause 1 only. Keep the rest intact.
- **Scope**: on hosts that support glob-scoped rules (Cursor `globs:`, Copilot `applyTo:`), scope the
  rule to the areas under decision so it does not fire on every prompt.
- **Language**: keep the clause about `模式：同旗舰双隔离` — it is a machine-checked label in the
  protocol; translating it breaks the contract.
