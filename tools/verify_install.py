#!/usr/bin/env python3
"""Verify installed copies of the dual-flagship-debate skill.

Answers the question the debate protocol keeps raising but no install format encodes:
*is what my hosts load the same thing I released?*

It checks, per skill root:

1. the skill directory exists and actually resolves (catches broken junctions/symlinks,
   which on Windows still report as existing even when their target is gone);
2. the required files are present, including the packaged runner under ``scripts/``;
3. the frontmatter name matches the directory name;
4. every installed copy is byte-identical to the others;
5. optionally, every installed copy is byte-identical to a released git tag.

Usage::

    python3 tools/verify_install.py                     # all copies agree with each other
    python3 tools/verify_install.py --tag v2.0.0        # ...and with that release tag
    python3 tools/verify_install.py --json              # machine-readable
    python3 tools/verify_install.py --roots ~/.claude/skills --roots ./.agents/skills

Exit codes: 0 all checks pass, 1 problems found, 2 usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_NAME = "dual-flagship-debate"
REQUIRED_FILES = (
    "SKILL.md",
    "references/models-and-hosts.md",
    "references/hosts.md",
    "scripts/run_debate.py",
    "scripts/process_tree.py",
    "scripts/debate.config.example.json",
)
# Windows reparse tags, so a junction is reported as a link rather than a plain directory.
REPARSE_TAGS = {0x9000001A: "symlink", 0xA0000003: "junction"}


def default_roots() -> list[Path]:
    home = Path.home()
    roots = [
        home / ".agents" / "skills",
        home / ".codex" / "skills",
        home / ".claude" / "skills",
        Path.cwd() / ".agents" / "skills",
        Path.cwd() / ".claude" / "skills",
    ]
    seen: list[Path] = []
    for root in roots:
        if root not in seen:
            seen.append(root)
    return seen


def sha256_bytes(data: bytes) -> str:
    """Hash text content with line endings normalised.

    A Windows checkout and a ``git show`` blob of the same file differ only by CRLF, so hashing
    raw bytes would report drift that is not real. Every required file here is text.
    """
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def sha256_file(path: Path) -> str:
    with open(path, "rb") as handle:
        return sha256_bytes(handle.read())


def frontmatter_name(skill_md: Path) -> str | None:
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def link_kind(path: Path) -> str:
    """Return 'junction', 'symlink' or 'directory' without following the link."""
    try:
        stat = os.lstat(path)
    except OSError:
        return "missing"
    tag = getattr(stat, "st_reparse_tag", 0) or 0
    if tag in REPARSE_TAGS:
        return REPARSE_TAGS[tag]
    if os.path.islink(path):
        return "symlink"
    if path.is_dir():
        return "directory"
    return "other"


def inspect(root: Path) -> dict:
    """Inspect one skill root. Never raises: problems are reported, not thrown."""
    skill_dir = root / SKILL_NAME
    record: dict = {
        "root": str(root),
        "path": str(skill_dir),
        "present": skill_dir.exists(),
        "kind": link_kind(skill_dir),
        "target": None,
        "readable": False,
        "missing_files": [],
        "sha256": {},
        "frontmatter_name": None,
        "problems": [],
    }
    if not record["present"]:
        return record

    # A junction or symlink whose target is gone still "exists" on Windows; resolving it is
    # the only reliable test, and it is exactly the silent-failure case worth catching.
    try:
        resolved = Path(os.path.realpath(skill_dir))
        record["target"] = str(resolved)
        record["readable"] = resolved.is_dir() and os.access(resolved, os.R_OK)
    except OSError as exc:
        record["problems"].append(f"cannot resolve link target: {exc}")
        return record

    if record["kind"] in ("junction", "symlink") and not record["readable"]:
        record["problems"].append("link target is missing or unreadable (skill silently unavailable)")
        return record

    for rel in REQUIRED_FILES:
        candidate = resolved / rel
        if not candidate.is_file():
            record["missing_files"].append(rel)
        else:
            record["sha256"][rel] = sha256_file(candidate)

    if record["missing_files"]:
        record["problems"].append("missing required files: " + ", ".join(record["missing_files"]))

    name = frontmatter_name(resolved / "SKILL.md")
    record["frontmatter_name"] = name
    if name and name != skill_dir.name:
        record["problems"].append(f"frontmatter name {name!r} != directory name {skill_dir.name!r}")
    return record


def tag_hashes(repo: Path, tag: str) -> tuple[dict[str, str], list[str], str | None]:
    """Hashes of the required files at ``tag``.

    Returns ``(hashes, absent, error)``: ``absent`` lists files the tag does not contain (a real
    drift signal — an installed copy must not have files a release never shipped), ``error`` is set
    only when git itself cannot resolve the tag or repository.
    """
    try:
        probe = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", f"{tag}^{{commit}}"],
            capture_output=True,
        )
    except OSError as exc:
        return {}, [], f"git not runnable: {exc}"
    if probe.returncode != 0:
        return {}, [], f"cannot resolve tag {tag!r} in {repo}"

    hashes: dict[str, str] = {}
    absent: list[str] = []
    prefix = f"skills/{SKILL_NAME}/"
    for rel in REQUIRED_FILES:
        blob = subprocess.run(
            ["git", "-C", str(repo), "show", f"{tag}:{prefix}{rel}"],
            capture_output=True,
        )
        if blob.returncode != 0:
            absent.append(rel)
        else:
            hashes[rel] = sha256_bytes(blob.stdout)
    return hashes, absent, None


def compare(reports: list[dict], expected: dict[str, str] | None, absent_in_tag: list[str] | None = None) -> list[str]:
    """Cross-copy and tag comparisons. Returns a list of problem strings."""
    problems: list[str] = []
    installed = [r for r in reports if r["present"]]
    if not installed:
        problems.append("no installed copy found in any checked root")
        return problems

    for record in reports:
        problems.extend(f"{record['path']}: {p}" for p in record["problems"])

    hashes = [r["sha256"].get("SKILL.md") for r in installed]
    if len(set(hashes)) > 1:
        problems.append("installed copies disagree with each other (SKILL.md): " + ", ".join(
            f"{r['path']}={str(h)[:10]}" for r, h in zip(installed, hashes)
        ))

    if absent_in_tag:
        present = [rel for rel in absent_in_tag if any(r["sha256"].get(rel) for r in installed)]
        if present:
            problems.append("installed copy contains files absent from the tag: " + ", ".join(present))

    if expected:
        for record in installed:
            for rel, want in expected.items():
                got = record["sha256"].get(rel)
                if got is None:
                    continue  # already reported as missing
                if got != want:
                    problems.append(
                        f"{record['path']}: {rel} differs from the released tag "
                        f"(installed {got[:10]}, tag {want[:10]})"
                    )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify installed copies of the skill.")
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]),
                        help="repository to compare against (default: this repository)")
    parser.add_argument("--tag", default=None, help="compare the install against this git tag")
    parser.add_argument("--roots", action="append", default=None,
                        help="skill root to check; may repeat (default: user and project roots)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    roots = [Path(r).expanduser() for r in args.roots] if args.roots else default_roots()
    expected = None
    absent_in_tag: list[str] = []
    if args.tag:
        expected, absent_in_tag, error = tag_hashes(Path(args.repo), args.tag)
        if error:
            print(f"[verify] {error}", file=sys.stderr)
            return 2

    reports = [inspect(root) for root in roots]
    problems = compare(reports, expected, absent_in_tag)

    if args.json:
        print(json.dumps({"tag": args.tag, "copies": reports, "problems": problems}, indent=2, ensure_ascii=False))
    else:
        print(f"verify-install: {SKILL_NAME}" + (f" (expected tag {args.tag})" if args.tag else ""))
        for record in reports:
            if not record["present"]:
                status = "absent"
                detail = ""
            elif record["problems"]:
                status = "PROBLEM"
                detail = record["problems"][0]
            else:
                status = "ok"
                detail = f"SKILL.md={str(record['sha256'].get('SKILL.md'))[:10]}"
            print(f"  [{status:7}] {record['path']}  ({record['kind']})"
                  + (f"  -> {record['target']}" if record["target"] and record["kind"] != "directory" else "")
                  + (f"  {detail}" if detail else ""))
        if problems:
            print(f"\n  {len(problems)} problem(s):")
            for problem in problems:
                print(f"   - {problem}")
        else:
            print("\n  all checked copies are consistent" + (f" with {args.tag}" if args.tag else ""))

    return 1 if problems else 0


if __name__ == "__main__":
    try:  # keep non-ASCII paths readable in legacy Windows consoles
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    sys.exit(main())
