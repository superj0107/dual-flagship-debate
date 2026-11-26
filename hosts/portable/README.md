# Portable runner — any two CLI agents, any OS

`run_debate.py` is the host-neutral dispatcher. It does not know or care which vendor's CLI it drives:
you give it two commands, it runs the protocol's two rounds and writes the transcripts.

Requirements: Python 3.9+, and two CLI agents on `PATH` (or full paths in the config).

## Quick start

```bash
cp hosts/portable/debate.config.example.json debate.config.json   # edit the two cmd arrays
python3 hosts/portable/run_debate.py \
  --config debate.config.json \
  --topic my-topic.md \
  --rounds 2
```

Output directory (default `debate-<timestamp>/`):

```
r1-A.out.md   r1-B.out.md     Round 1 answers (verbatim)
r1-A.prompt.md r1-B.prompt.md the exact briefs sent
r1-A.log.txt  r1-B.log.txt    child stderr (progress, errors)
r2-*.md                        Round 2, only with --rounds 2
RUN-META.json                  pair, timing, exit codes, char counts
WORKSPACE-DIFF-WARNING.txt     only if the workspace changed during the run
```

## Config

```json
{
  "debaters": {
    "A": { "name": "codex-cli", "cmd": ["codex", "exec", "--skip-git-repo-check",
                                          "-s", "read-only", "--ephemeral", "-o", "{out}"] },
    "B": { "name": "claude-code", "cmd": ["claude", "-p", "--output-format", "text"] }
  },
  "timeout_sec": 900,
  "workdir": "."
}
```

- `cmd` — argv list (or a shell string). The **brief is always fed on stdin**.
- `{out}` — if present in any argument, it is replaced with the answer-file path, and the runner reads
  that file afterwards instead of stdout. Use it for CLIs that write their final message to a file.
- `{prompt}` — replaced with the brief's temp path, for CLIs that take a file instead of stdin.
- `{workdir}` — replaced with the resolved workdir.
- `"A": "claude-code"` — a plain string picks a preset. `--list-presets` prints them all:
  `codex-cli`, `claude-code`, `gemini-cli`, `aider`.

## What the runner does *not* do

- **It does not make a CLI read-only.** Read-only comes from the flags in your `cmd`
  (`-s read-only`, `--permission-mode plan`, tool allow-lists, auto-approve off). The runner only
  snapshots `git status --porcelain` and warns if the tree changed.
- **It does not fact-check.** Step 3 of the protocol — verifying the debaters' new claims — is the
  host agent's job.
- **It does not pick models.** Parity is your decision: two flagship tier models at max reasoning, or
  a documented single-flagship fallback labelled `模式：同旗舰双隔离`. The runner cannot see your
  model catalog.

## Notes per platform

- **Windows**: commands are spawned directly (no shell), so quoting behaves; PowerShell is fine as the
  parent. `run-debate.ps1` in `hosts/windows-cli/` is the same protocol with native PS ergonomics.
- **macOS / Linux**: run as-is; wrap with `caffeinate`/`timeout` if you need OS-level keep-awake.
- **Long runs**: two flagship calls per round, 30–90 s each typically; a full two-round debate is
  four calls. Set `timeout_sec` generously (the default 900 is per process, not total).
