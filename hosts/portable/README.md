# Portable runner — macOS, Linux and Windows

Python 3.10+ and two compatible model CLIs are required. The complete implementation ships
inside the skill at `skills/dual-flagship-debate/scripts/`. This directory retains a compatibility
entry point, so existing repository command paths still work.

## macOS and Linux

```sh
cp hosts/portable/debate.config.example.json debate.config.json
# Verify live models/effort in your host; add model/effort fields or verify the CLI defaults.
python3 hosts/portable/run_debate.py --config debate.config.json \
  --topic my-topic.md --workdir /path/to/repo --rounds 2
```

Use `python3 --version` to check the runtime. On macOS the command works in zsh and bash,
without PowerShell, GNU timeout, extra pip packages, or OS-specific installation scripts.
An installed skill can be run directly with `python3 SKILL_DIR/scripts/run_debate.py`.

## Windows

```powershell
Copy-Item hosts/portable/debate.config.example.json debate.config.json
python hosts/portable/run_debate.py --config debate.config.json --topic my-topic.md --workdir . --rounds 2
```

`py -3` also works. The optional `hosts/windows-cli/run-debate.ps1` translates PowerShell
parameters and delegates to this same engine, preserving exit codes.

## Configuration

```json
{
  "debaters": {
    "A": {"preset": "codex-cli", "name": "Reviewer"},
    "B": {"preset": "codex-cli", "name": "Reviewer"}
  },
  "timeout_sec": 900,
  "total_timeout_sec": 1800,
  "workdir": "."
}
```

Identical presets and names are supported: the role ID A/B and unique run directory identify artifacts.
The host still owns Step 0 model discovery/parity and Step 3 fact-checking. Optional `model` and
`effort` fields pin each preset after live discovery. A `cli_version` and requested settings appear
in metadata; inspect the CLI's runtime log to confirm the model actually used.

Built-in presets restrict model tools:

- `codex-cli`: explicit read-only sandbox, noninteractive approvals, ephemeral sessions; disables
  apps, plugins, hooks and skill-driven MCP installation. Preflight reads the MCP catalog and
  disables every configured server separately; an empty MCP table would merge existing entries.
- `claude-code`: requires `--safe-mode`, `--tools Read,Grep,Glob`, plan permissions,
  strict MCP configuration and no session persistence. Unsupported flags produce a preflight error.

Runtime storage such as CLI authentication/cache bookkeeping is owned by the CLI. Permission
controls apply to the debaters' model tools and reviewed workspace. Native CLI hooks and plugins
have different semantics across versions; retest restrictions when upgrading.

For other CLIs, supply a **verified custom adapter**:

```json
{
  "name": "Custom reviewer",
  "cmd": ["MY_READONLY_CLI", "--prompt-file", "{prompt}"],
  "read_only": {
    "mechanism": "external-sandbox",
    "evidence": "Describe the isolation/tool configuration and the write-blocking check actually performed"
  }
}
```

Allowed mechanisms are `external-sandbox` and `tool-allowlist`. This is the host's attestation,
not an automatic proof of arbitrary command behavior. Prompt-only promises and Git status are
insufficient. Gemini/Aider recipes require a verified custom adapter instead of the former
unrestricted presets. Review arbitrary commands before running them.

`cmd` accepts argv arrays only. The prompt is UTF-8 stdin. Literal tokens `{out}`, `{prompt}`,
and `{workdir}` expand to absolute paths; other JSON/TOML braces remain literal. An `{out}`
adapter must create its answer file; otherwise stdout is the answer. A missing file never falls
back to progress/error text. Native executables and npm's known Node entry points preserve argv.
Other Windows batch shims reject shell metacharacters; use the native executable for such arguments.

Paths in the CLI and config resolve against the invocation's working directory. Optional per-role
`cwd` values are resolved explicitly and included in the audit.

## Outputs and failure handling

`--out-dir` must be a new directory. By default a timestamp and random run ID prevent collisions.

```text
r1-A.out.md, r1-B.out.md          Complete Round 1 answers
r2-A.out.md, r2-B.out.md          Complete Round 2 answers, if requested
r1-A.prompt.md, ...              Exact UTF-8 prompts
r1-A.log.txt, ...                Child stderr
r1-A.stdout.txt, ...             Child stdout, separate from answer files
RUN-META.json                   Roles, versions, argv, cwd, hashes, timing, status
WORKSPACE-DIFF-WARNING.txt       Content changes or Git status changes, if observed
```

A nonzero child exit, empty/missing/invalid UTF-8 answer or oversized result fails the round.
R1 failures stop the run before R2. No transcript truncation is applied to satisfy budgets.
The runner supports per-process and whole-run deadlines; timeout, cancellation and normal
completion clean up managed children. POSIX uses a separate process group; Windows uses a
kill-on-close Job Object assigned before the child runs. POSIX adapters must keep descendants
in that group (no daemonizing/setsid); a process group does not contain deliberately detached
processes. Use an external OS sandbox/service supervisor for adapters with detached workers.

Exit codes: **0** transcripts complete; **2** configuration/preflight error; **3** failed round or
deadline; **4** workspace changed/audit failed; **130** user cancellation.

The content audit hashes regular files, including dirty and ignored files, in every reviewed cwd.
It excludes Git internals and the run directory and records symlinks without following their targets.
Changes that are made and reverted between snapshots, external writes and CLI runtime storage
are outside this audit. Restrict tools/sandboxing before dispatch; hashes are post-run observations.

Budget settings (config; the first three also have CLI overrides):

| Setting | Default | Purpose |
|---|---:|---|
| `timeout_sec` / `--timeout` | 900 | Per child process, seconds |
| `total_timeout_sec` / `--total-timeout` | 1800 | Whole invocation, seconds |
| `max_prompt_chars` / `--max-prompt-chars` | 120000 | Full input per round/role |
| `max_output_bytes` | 2000000 | Maximum accepted answer file size |
| `max_audit_files` | 50000 | Maximum files hashed per cwd |
| `max_audit_bytes` | 536870912 | Maximum content bytes hashed per cwd |

The whole-run deadline also covers capability probes and initial auditing. File auditing checks
the deadline between entries/chunks; an OS-level blocked filesystem operation may finish later.
After failure or cancellation, final verification gets at most five additional seconds. A successful
run's final audit stays within the whole-run budget; incomplete verification is recorded as an error.

Choose a focused repository/directory or explicitly adjust audit limits for large projects.
The output character request controls presentation; it does not cap model thinking or API billing.
Use vendor budget controls where available.

## Verification

```sh
python3 tests/validate_skill.py
python3 -m unittest discover -s tests -v
```

GitHub Actions defines Windows, macOS and Ubuntu jobs on Python 3.10 and 3.13. Synthetic CLI
tests exercise actual subprocesses without paid model calls. A matrix definition is distinct
from a completed CI run; consult its results for the platform/version you intend to deploy.
