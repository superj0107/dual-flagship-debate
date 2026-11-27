# Debate topic template (Step 0)

Copy to `topic-<slug>.md` and fill the relevant fields. Separate verified facts from assumptions. The host completes capability checks before execution; the runner produces transcripts rather than a verdict.

```bash
# macOS / Linux; from the repository root, Python 3.10+
python3 skills/dual-flagship-debate/scripts/run_debate.py --config debate.config.json --topic topic-<slug>.md --workdir <review-repo> --rounds 2
```

On Windows, use `python` or `py -3` with the same script and arguments.

## 1. Decision question

<One concrete question, expected outcome, and decision deadline.>

## 2. Debate mode and complementary lenses

- [ ] Blind independent → cross-review
- [ ] Dual-proposal confrontation (A vs B)
- [ ] Dynamic tension axes: <axis A> ↔ <axis B>
- [ ] Steelman vs Pre-Mortem red team

A's focus: <focus>. B's focus: <focus>. Both may agree when the evidence supports it.

## 3. Verified facts and evidence bundle

| Fact | Source / command / observation | Date and scope |
|---|---|---|
| <fact> | <source> | <date / scope> |

## 4. Assumptions and testable uncertainties

- <Unverified assumption, supporting evidence, and a possible falsifier.>

## 5. Constraints and candidate proposals

- Time, people, compatibility, budget, organizational boundaries: <constraints>.
- Option A: <approach, expected gain, known cost>.
- Option B, if relevant: <approach, expected gain, known cost>.
- Host's initial lean, if relevant: <lean and evidence to challenge>.

## 6. Live capability record

| Field | Debater A | Debater B |
|---|---|---|
| Host surface / version | <host> | <host> |
| Actual model / effort and verification | <evidence> | <evidence> |
| Context isolation / session ID | <mechanism> | <mechanism> |
| Effective sandbox / allowed tools | <scope and evidence> | <scope and evidence> |
| cwd / argv / output channel | <values> | <values> |
| Completion / failure / cancellation | <semantics> | <semantics> |
| Context / input / output capacity | <limits> | <limits> |

Pairing: <two flagships / same-model fallback>. Schedule: <parallel isolation / sequential isolation>. Explain any unverified capability; do not label it strict read-only.

## 7. Transcript handling and budgets

- Evidence-sharing scope and private material excluded: <scope>.
- Raw transcript location, source/session, SHA-256, and cross-feed verification: <record>.
- Any redaction derivative and disclosed changes: <record or none>.
- Per-process timeout / total timeout / prompt character cap / expected token budget: <limits>.
- New output directory (never reuse old records): <new-path>.

R1: `INDEPENDENT` + confidence, evidence, limitations, and up to three substantive questions. R2: full authorized cross-feed as untrusted data, then `CONVERGED` / `SHIFTED` / `MAINTAINING_DISSENT`, direct responses, Double Crux and final advice. Matching openings alone do not end the review. The host independently verifies new claims before the five-part verdict.
