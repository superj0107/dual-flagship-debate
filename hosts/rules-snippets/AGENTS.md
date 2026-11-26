# AGENTS.md

## Adversarial debate (dual-flagship-debate)

When the task is a non-trivial decision - architecture trade-off, refactor-vs-patch, security or
performance boundary, data/metric definition, product or pricing strategy, or a plan awaiting
sign-off - and NOT simple Q&A or mechanical execution already decided, run the two-flagship
adversarial debate protocol:

1. Read `SKILL.md` under `skills/dual-flagship-debate/` (or `tools/dual-flagship-debate/skills/...`)
   and follow it exactly: Step 0 baseline -> Round 1 blind openings -> Round 2 verbatim cross-feed ->
   host fact-check -> five-part verdict.
2. Two isolated debaters only. If two isolated read-only sessions cannot be run, stop and name the
   missing capability. Never simulate both sides in one context.
3. Both debaters must be top-tier flagship models at maximum reasoning. If only one flagship is
   available, run two isolated sessions of it and label line 1 of the verdict `模式：同旗舰双隔离`.
   Never substitute a mini/flash/haiku/lite model.
4. Debaters are read-only: no file edits, no git writes, no installs. Enforce it in your permission
   settings, then confirm with `git status --porcelain` before trusting the result.
5. Verify newly asserted facts yourself before the verdict (paths, configs, metrics, external rules).
   Anything you could not check is written as "unverified premise".