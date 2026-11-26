# Debate topic template (Step 0)

> Copy to `topic-<slug>.md`, fill every section, then run:
> `powershell -ExecutionPolicy Bypass -File hosts\windows-cli\run-debate.ps1 -TopicFile .\topic-<slug>.md -Rounds 2`
>
> Anything you cannot substantiate goes under **unverified assumptions** — never invent facts.
> Round 1 quality is a direct function of this baseline.

## 1. Decision question (one sentence, falsifiable)

<e.g. Should the order service be split into three independently deployed units in Q1?>

## 2. Debate mode (pick exactly one, delete the rest)

- [ ] **Blind independent → cross-attack** — open problem, no preset proposal
- [ ] **Dual-proposal confrontation (A vs B)** — two candidates, pick one
- [ ] **Dynamic tension axes** — open trade-off; host names the axis
- [ ] **Steelman vs Pre-Mortem red team** — a drafted plan awaiting sign-off

Tension axis (mode 3 only): <axis A> ↔ <axis B>

## 3. Verified facts (each must point at a file, command output, or data source)

-
-
-

## 4. Unverified assumptions (debaters must attack or confirm these)

-
-

## 5. Hard constraints (non-negotiable)

- Time: <deadline / freeze window>
- People: <headcount, skills>
- Compatibility: <interfaces, parameters, data formats that cannot change>
- Cost: <budget cap>
- Organisation: <team boundaries, approval chain>

## 6. Candidate proposals (modes 2 and 4)

**Option A**: <approach + expected gain + known cost>
**Option B**: <approach + expected gain + known cost>

## 7. Host's own lean (optional but valuable)

<I lean toward X because Y. Attack that reason specifically; do not agree with me to be agreeable.>
