**A stricter protocol, a self-contained package, and a tool that tells you whether what your agents load is what you released.**

## Breaking in 2.0.0

- **Round 1 vocabulary changed.** Debaters open with `INDEPENDENT` plus confidence and evidence;
  `CONVERGED` / `SHIFTED` / `MAINTAINING_DISSENT` now belong to Round 2 only. Transcripts produced
  against the 1.x text do not satisfy the contract, and matching opening conclusions no longer justify
  stopping after Round 1.
- **Custom CLI adapters must declare read-only.** A `cmd` entry now requires a `read_only` block
  (`external-sandbox` or `tool-allowlist`) with verification evidence, or preflight refuses to run. The
  `gemini-cli` and `aider` presets were removed in favour of verified custom adapters.
- **The runner moved into the skill.** The canonical entry is
  `skills/dual-flagship-debate/scripts/run_debate.py`; `hosts/portable/run_debate.py` remains as a
  compatibility shim.

## Protocol

Isolation, live capability and tool permissions are now gated **before** dispatch, and names alone
never count as capability evidence. Cross-fed opponent text is untrusted data with source, hash and
integrity checks; redaction must keep the original and disclose the derivative. Evidence-based
agreement is explicitly valid — there is no conflict quota, no minimum number of position changes, and
no reward for convergence.

## New: `tools/verify_install.py`

Repository tests say nothing about what your hosts actually load. This checks it:

```bash
python3 tools/verify_install.py --tag v2.0.0
```

Fails when a copy is unreadable (a junction whose target was deleted still reports as present on
Windows), when required files are missing, when copies diverge, or when installed content is not what
the tag ships. Line endings are normalised before hashing, so a CRLF checkout is not mistaken for
drift. Eight unit tests cover those paths.

## Verification

- 47 tests pass locally (Windows 11 / Python 3.12), one POSIX-signal case skipped as designed.
- CI matrix: Windows, macOS, Linux × Python 3.10 and 3.13.
- `python3 tests/validate_skill.py` clean.
- A real Codex + Claude CLI round-trip completes end to end on Windows.

## Still your job

- Read-only is a flag you pass (`-s read-only`, `--permission-mode plan`, tool allow-list), not a
  property of this package. The runner records what you declared; it cannot enforce it.
- Two flagships, or two isolated sessions of one flagship labelled `模式：同旗舰双隔离`. Never a
  mini/flash/haiku/lite stand-in, never both sides in one context.
- Installing is not adapting: the per-host pages in [`hosts/`](https://github.com/superj0107/dual-flagship-debate/tree/main/hosts) still own read-only enforcement and two-debater dispatch.

MIT.
