#!/usr/bin/env python3
"""Portable dual-flagship debate runner.

Drives any two CLI agents through the protocol's two rounds:

    Round 1  two isolated read-only debaters, blind opening, in parallel
    Round 2  two FRESH processes, each fed [Step 0 baseline + own R1 + opponent R1]

Prompt text goes to the child on stdin; stdout becomes the answer. If an argument contains
``{out}``, the path of the answer file is substituted (use it for CLIs like ``codex exec -o FILE``
that write the final message to a file).

Usage:
    python3 run_debate.py --config debate.config.json --topic topic.md
    python3 run_debate.py --config debate.config.json --topic topic.md --rounds 1
    python3 run_debate.py --list-presets

Exit codes: 0 ok, 2 configuration problem, 3 a debater failed or timed out.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

RULES_R1 = """[READ-ONLY] This round is read-only analysis: do not create, modify or delete any file,
do not run git writes, do not install anything.
[LANGUAGE] Answer in the language of the Step 0 baseline; keep the section structure as given.
[ANTI-SYCOPHANCY] No polite compromise, no "everyone is partly right" mush. Never abandon a stance
without citing new evidence, a counter-example, or a causal argument.
[OUTPUT] <= 1200 characters, exactly four sections:
1. Stance status: CONVERGED / SHIFTED / MAINTAINING_DISSENT (+ calibration of the Step 0 baseline)
2. Core position and reasoning (name your load-bearing premises)
3. Three lethal questions aimed at the opponent's weakest load-bearing assumption or hidden cost
4. Evidence you actually verified (files read / commands run); write "unverified" if none
"""

RULES_R2 = """[READ-ONLY] Same as Round 1: read-only.
[ANTI-SYCOPHANCY] No mush consensus. If you shift, cite the specific new evidence that moved you.
[STEELMAN] Before rebutting, restate the opponent's strongest premise in 1-2 sentences. No strawmen.
[ATOMIC REBUTTALS] Format each: Claim -> Flaw type (fact/constraint violated | hidden assumption
failed | boundary or scale collapse | incentive or second-order backlash | logical leap) -> counter
or alternative path.
[OUTPUT] <= 1000 characters, exactly four sections:
1. New stance status and what you concede
2. Point-by-point answers to the opponent's three questions (concede blind spots explicitly)
3. Double Crux: 1-2 unproven assumptions that carry the decision, plus their falsifiers
4. Your converged recommendation
"""

PRESETS = {
    "codex-cli": {
        "name": "codex-cli",
        "cmd": ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "--ephemeral", "-o", "{out}"],
    },
    "claude-code": {
        "name": "claude-code",
        "cmd": ["claude", "-p", "--output-format", "text"],
    },
    "gemini-cli": {
        "name": "gemini-cli",
        "cmd": ["gemini", "-p"],
    },
    "aider": {
        "name": "aider",
        "cmd": ["aider", "--message-file", "{prompt}", "--no-auto-commits", "--yes-always"],
    },
}


def build_prompt(baseline: str, rules: str, side: str, own: str = "", opp: str = "", extra: str = "") -> str:
    parts: list[str] = []
    if extra:
        parts += [extra, "", "--- end of baseline, task brief follows ---", ""]
    parts += [f"# Adversarial debate - task brief ({side})", "", "## Topic and Step 0 verified baseline", baseline, ""]
    if own or opp:
        parts += [
            "## Your own Round 1 output - verbatim",
            own,
            "",
            "## Opponent Round 1 output - verbatim, not summarized",
            opp,
            "",
        ]
    parts += ["## Rules for this round", rules]
    return "\n".join(parts)


def resolve_cmd(spec: dict, out_file: Path, prompt_file: Path, workdir: Path) -> list[str]:
    raw = spec.get("cmd")
    if not raw:
        raise ValueError(f"debater {spec.get('name', '?')!r} has no 'cmd'")
    args = raw if isinstance(raw, list) else shlex.split(raw)
    subs = {"{out}": str(out_file), "{prompt}": str(prompt_file), "{workdir}": str(workdir)}
    argv = [arg.format(**{k.strip("{}"): v for k, v in subs.items()}) for arg in args]
    return _platform_argv(argv)


def _platform_argv(argv: list[str]) -> list[str]:
    """Resolve the executable and keep .cmd/.bat shims launchable on Windows.

    Many CLIs ship as ``codex.cmd``/``claude.cmd`` shims; CreateProcess cannot execute those
    directly, so route them through the command interpreter.
    """
    if os.name != "nt":
        return argv
    resolved = shutil.which(argv[0]) or argv[0]
    if resolved.lower().endswith((".cmd", ".bat")):
        return [os.environ.get("COMSPEC", "cmd.exe"), "/c", resolved, *argv[1:]]
    return [resolved, *argv[1:]]


def run_debater(spec: dict, prompt: str, outdir: Path, tag: str, timeout: int, workdir: Path) -> dict:
    name = spec.get("name") or tag
    prompt_file = outdir / f"{tag}-{name}.prompt.md"
    out_file = outdir / f"{tag}-{name}.out.md"
    log_file = outdir / f"{tag}-{name}.log.txt"
    prompt_file.write_text(prompt, encoding="utf-8")

    uses_out_placeholder = any("{out}" in str(a) for a in (spec.get("cmd") or []))
    cmd = resolve_cmd(spec, out_file, prompt_file, workdir)
    cwd = spec.get("cwd") or workdir

    print(f"  [{tag}/{name}] dispatch: {' '.join(cmd[:4])}...", file=sys.stderr)
    started = datetime.now(timezone.utc)
    with open(log_file, "wb") as log:
        try:
            proc = subprocess.run(
                cmd,
                input=prompt.encode("utf-8"),
                stdout=subprocess.DEVNULL if uses_out_placeholder else subprocess.PIPE,
                stderr=log,
                cwd=str(cwd),
                timeout=timeout,
            )
            code, stdout = proc.returncode, proc.stdout or b""
        except subprocess.TimeoutExpired:
            code, stdout = -1, b""
            log.write(f"\n[runner] timed out after {timeout}s\n".encode())
        except FileNotFoundError as exc:
            code, stdout = -2, b""
            log.write(f"\n[runner] command not found: {exc}\n".encode())

    if uses_out_placeholder and out_file.exists():
        answer = out_file.read_text(encoding="utf-8", errors="replace")
    else:
        answer = stdout.decode("utf-8", errors="replace")
        out_file.write_text(answer, encoding="utf-8")

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    print(f"  [{name}] done exit={code} chars={len(answer)} {elapsed:.0f}s", file=sys.stderr)
    return {"name": name, "exit": code, "answer": answer, "out": out_file, "seconds": elapsed}


def git_status(workdir: Path) -> str | None:
    if not (workdir / ".git").exists():
        return None
    try:
        proc = subprocess.run(["git", "-C", str(workdir), "status", "--porcelain"], capture_output=True, text=True)
        return proc.stdout
    except OSError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Portable two-round adversarial debate runner.")
    ap.add_argument("--config", help="JSON config with debaters A and B")
    ap.add_argument("--topic", help="topic file with the Step 0 baseline")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--rounds", type=int, choices=(1, 2), default=2)
    ap.add_argument("--timeout", type=int, default=None, help="per-process seconds (default: config or 900)")
    ap.add_argument("--workdir", default=None, help="repo context the debaters may read")
    ap.add_argument("--append-system-prompt", default=None, help="file prepended to every brief")
    ap.add_argument("--list-presets", action="store_true")
    args = ap.parse_args()

    if args.list_presets:
        print(json.dumps(PRESETS, indent=2, ensure_ascii=False))
        return 0

    if not args.config or not args.topic:
        ap.error("--config and --topic are required (or use --list-presets)")

    cfg_path = Path(args.config).expanduser().resolve()
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[runner] cannot read config: {exc}", file=sys.stderr)
        return 2

    debaters = cfg.get("debaters") or {}
    for key in ("A", "B"):
        if key not in debaters:
            print(f"[runner] config needs debaters.{key}", file=sys.stderr)
            return 2
        spec = debaters[key]
        if isinstance(spec, str):
            if spec not in PRESETS:
                print(f"[runner] unknown preset {spec!r}; try --list-presets", file=sys.stderr)
                return 2
            debaters[key] = dict(PRESETS[spec])

    workdir = Path(args.workdir or cfg.get("workdir") or ".").expanduser().resolve()
    timeout = args.timeout or int(cfg.get("timeout_sec") or 900)
    topic = Path(args.topic).expanduser().resolve().read_text(encoding="utf-8")

    extra = ""
    if args.append_system_prompt:
        extra = Path(args.append_system_prompt).expanduser().resolve().read_text(encoding="utf-8")

    outdir = Path(args.out_dir or f"debate-{datetime.now().strftime('%Y%m%d-%H%M%S')}").expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    before = git_status(workdir)

    print(f"=== Round 1: parallel blind opening (workdir={workdir}) ===", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            key: pool.submit(
                run_debater,
                debaters[key],
                build_prompt(topic, RULES_R1, f"Debater {key}", extra=extra),
                outdir,
                "r1",
                timeout,
                workdir,
            )
            for key in ("A", "B")
        }
        r1 = {key: fut.result() for key, fut in futures.items()}

    if args.rounds == 2:
        print("=== Round 2: stateless replay (own R1 + opponent R1 verbatim) ===", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {}
            for key, other in (("A", "B"), ("B", "A")):
                prompt = build_prompt(
                    topic, RULES_R2, f"Debater {key}", own=r1[key]["answer"], opp=r1[other]["answer"], extra=extra
                )
                futures[key] = pool.submit(run_debater, debaters[key], prompt, outdir, "r2", timeout, workdir)
            r2 = {key: fut.result() for key, fut in futures.items()}
    else:
        r2 = {}

    after = git_status(workdir)
    if before is not None and after is not None and before != after:
        warn = outdir / "WORKSPACE-DIFF-WARNING.txt"
        warn.write_text(after, encoding="utf-8")
        print(f"[read-only guard] workspace changed during the debate -> {warn}", file=sys.stderr)

    meta = {
        "pair": {k: debaters[k].get("name", k) for k in ("A", "B")},
        "rounds": args.rounds,
        "workdir": str(workdir),
        "timeout_sec": timeout,
        "finished": datetime.now(timezone.utc).isoformat(),
        "results": {tag: {k: {"exit": v["exit"], "chars": len(v["answer"]), "seconds": round(v["seconds"], 1)}
                          for k, v in batch.items()}
                    for tag, batch in (("r1", r1), ("r2", r2)) if batch},
    }
    (outdir / "RUN-META.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n=== output: {outdir} ===")
    for path in sorted(outdir.iterdir()):
        print(f"  {path.name}  ({path.stat().st_size}B)")

    failed = [k for k, v in r1.items() if v["exit"] != 0 or len(v["answer"]) < 80]
    failed += [k for k, v in r2.items() if v["exit"] != 0 or len(v["answer"]) < 80]
    if failed:
        print(f"[runner] debater(s) failed or returned too little: {sorted(set(failed))}", file=sys.stderr)
        return 3
    print("Next: the host reads R1/R2 verbatim, fact-checks new claims itself, then writes the five-part verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
