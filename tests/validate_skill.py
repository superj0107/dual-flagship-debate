#!/usr/bin/env python3
"""Validate dual-flagship-debate: skill contract, references, repository files, privacy hygiene."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "dual-flagship-debate"
SKILL_PATH = SKILL_DIR / "SKILL.md"
REFERENCE_PATH = SKILL_DIR / "references" / "models-and-hosts.md"

EXPECTED_SKILL_NAME = "dual-flagship-debate"
NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MAX_SKILL_LINES = 90

# SKILL.md must stay model- and host-agnostic: concrete IDs and CLI verbs belong in references/.
FORBIDDEN_SKILL_PATTERNS = [
    ("hardcoded_gemini_neon", re.compile(r"gemini-4-neon", re.IGNORECASE)),
    ("hardcoded_gemini_carbon", re.compile(r"gemini-4-carbon", re.IGNORECASE)),
    ("hardcoded_gpt_model", re.compile(r"\bgpt-\d", re.IGNORECASE)),
    ("hardcoded_claude_model", re.compile(r"\bclaude-(?:opus|sonnet|haiku|fable)\b", re.IGNORECASE)),
    ("hardcoded_qwen_model", re.compile(r"\bqwen\d", re.IGNORECASE)),
    ("hardcoded_kimi_model", re.compile(r"\bkimi-", re.IGNORECASE)),
    ("hardcoded_deepseek_model", re.compile(r"\bdeepseek-", re.IGNORECASE)),
    ("cli_verb_codex", re.compile(r"codex\s+exec", re.IGNORECASE)),
    ("cli_verb_claude_print", re.compile(r"claude\s+-p\b", re.IGNORECASE)),
    ("t3_delegate_task", re.compile(r"\bdelegate_task\b")),
    ("t3_thread_send", re.compile(r"\bt3_thread_send\b")),
    ("t3_orchestrator_capabilities", re.compile(r"\borchestrator_capabilities\b")),
]

REQUIRED_SKILL_MARKERS = [
    "references/models-and-hosts.md",
    "辩手 A",
    "辩手 B",
    "模式：同旗舰双隔离",
    "硬阻断",
    "有状态宿主",
    "无状态宿主",
    "CONVERGED",
    "SHIFTED",
    "MAINTAINING_DISSENT",
    "Steelman",
    "Pre-Mortem",
    "Double Crux",
    "双盲独立",
    "既定双案攻防",
    "动态张力双轴",
    "Step 0",
    "Step 1",
    "Step 2",
    "Step 3",
    "事实纠偏闸门",
]

REQUIRED_FILES = [
    "README.md",
    "README.zh-CN.md",
    "LICENSE",
    "CHANGELOG.md",
    "examples/topic-template.md",
    "examples/case-install-sync.md",
    "hosts/README.md",
    "hosts/dsh/HOSTS.md",
    "hosts/codex/HOSTS.md",
    "hosts/claude-code/HOSTS.md",
    "hosts/gemini-cli/HOSTS.md",
    "hosts/cursor/HOSTS.md",
    "hosts/copilot-vscode/HOSTS.md",
    "hosts/cline-roo/HOSTS.md",
    "hosts/opencode-aider/HOSTS.md",
    "hosts/rules-snippets/README.md",
    "hosts/rules-snippets/AGENTS.md",
    "hosts/rules-snippets/cursor.mdc",
    "hosts/rules-snippets/copilot-instructions.md",
    "hosts/rules-snippets/clinerules.md",
    "hosts/rules-snippets/windsurfrules.md",
    "hosts/rules-snippets/CONVENTIONS.md",
    "hosts/portable/run_debate.py",
    "hosts/portable/debate.config.example.json",
    "hosts/portable/README.md",
    "hosts/windows-cli/run-debate.ps1",
    "skills/dual-flagship-debate/references/models-and-hosts.md",
    "skills/dual-flagship-debate/references/hosts.md",
    "skills/dual-flagship-debate/scripts/run_debate.py",
    "skills/dual-flagship-debate/scripts/process_tree.py",
    "skills/dual-flagship-debate/scripts/debate.config.example.json",
    ".github/workflows/validate.yml",
]

PRIVACY_PATTERNS = [
    ("absolute_home_path", re.compile(r"(?:/Users/|/home/|C:\\Users\\|F:\\\\)[A-Za-z0-9._\u4e00-\u9fff-]+")),
    ("personal_email", re.compile(r"[A-Za-z0-9._%+-]+@(?:gmail|qq|163|126|outlook|icloud)\.com\b", re.IGNORECASE)),
    ("private_ipv4", re.compile(r"\b(?:192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|127\.0\.0\.1)\b")),
    ("token_prefix", re.compile(r"\b(?:ghp_|gho_|ghs_|github_pat_|sk-[A-Za-z0-9]{16,}|AIza[0-9A-Za-z_-]{20,})\b")),
]


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n([\s\S]+?)\n---\n", text)
    if not match:
        raise AssertionError("SKILL.md must begin with YAML frontmatter delimited by ---")
    raw = match.group(1)
    fields: dict[str, str] = {}
    current_key: str | None = None
    buffer: list[str] = []
    for line in raw.splitlines():
        if re.match(r"^[A-Za-z0-9_-]+\s*:", line):
            if current_key is not None:
                fields[current_key] = " ".join(buffer).strip()
            key, rest = line.split(":", 1)
            current_key = key.strip()
            val = rest.strip()
            buffer = [] if val in {">", ">-", "|", "|-"} else [val]
        elif current_key is not None and (line.startswith(" ") or line.startswith("\t")):
            buffer.append(line.strip())
    if current_key is not None:
        fields[current_key] = " ".join(buffer).strip()
    return fields


def validate_skill() -> None:
    if not SKILL_PATH.is_file():
        raise AssertionError(f"Missing skill definition: {SKILL_PATH}")
    content = SKILL_PATH.read_text(encoding="utf-8")
    line_count = len(content.splitlines())
    if line_count > MAX_SKILL_LINES:
        raise AssertionError(f"SKILL.md exceeds {MAX_SKILL_LINES} lines ({line_count} lines)")

    frontmatter = parse_frontmatter(content)
    name = frontmatter.get("name", "")
    if name != EXPECTED_SKILL_NAME:
        raise AssertionError(f"Expected name {EXPECTED_SKILL_NAME!r}, got {name!r}")
    if not NAME_PATTERN.fullmatch(name):
        raise AssertionError(f"Skill name {name!r} must match ^[a-z0-9]+(?:-[a-z0-9]+)*$")
    if SKILL_DIR.name != name:
        raise AssertionError(f"Skill directory {SKILL_DIR.name!r} must equal frontmatter name {name!r}")

    description = frontmatter.get("description", "")
    if len(description) < 40:
        raise AssertionError("Frontmatter description is missing or too short")
    for vendor in ("gemini", "anthropic", "openai"):
        if vendor in description.lower():
            raise AssertionError(f"Frontmatter description must stay model-agnostic (mentions {vendor})")

    for label, pattern in FORBIDDEN_SKILL_PATTERNS:
        match = pattern.search(content)
        if match:
            raise AssertionError(f"SKILL.md must stay model/host-agnostic ({label}): found {match.group(0)!r}")

    missing = [marker for marker in REQUIRED_SKILL_MARKERS if marker not in content]
    if missing:
        raise AssertionError(f"SKILL.md is missing required protocol markers: {missing}")


def validate_references_and_repo() -> None:
    if not REFERENCE_PATH.is_file():
        raise AssertionError(f"Missing skill reference file: {REFERENCE_PATH.relative_to(ROOT)}")
    ref_text = REFERENCE_PATH.read_text(encoding="utf-8")
    if not re.search(r"Last Verified:\s*\d{4}-\d{2}-\d{2}", ref_text):
        raise AssertionError("references/models-and-hosts.md must declare 'Last Verified: YYYY-MM-DD'")
    if "non-normative" not in ref_text.lower():
        raise AssertionError("references/models-and-hosts.md must include a non-normative snapshot warning")

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            raise AssertionError(f"Missing required repository file: {rel}")

    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    if "README.zh-CN.md" not in readme_en:
        raise AssertionError("README.md must link to README.zh-CN.md")
    if "README.md" not in readme_zh:
        raise AssertionError("README.zh-CN.md must link to README.md")
    ref_rel = "skills/dual-flagship-debate/references/models-and-hosts.md"
    if ref_rel not in readme_en or ref_rel not in readme_zh:
        raise AssertionError(f"Both READMEs must link to {ref_rel}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    for needle in ("MIT License", "Copyright (c)", "dual-flagship-debate contributors"):
        if needle not in license_text:
            raise AssertionError(f"LICENSE must contain {needle!r}")


def validate_privacy() -> None:
    skip_dirs = {".git", "__pycache__", ".venv", ".idea", ".vscode"}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(ROOT).parts
        # Skip VCS internals and local run artifacts (transcripts echo paths from the machine).
        if any(part in skip_dirs or part.startswith(("out-", "debate-")) for part in parts[:-1]):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PRIVACY_PATTERNS:
            match = pattern.search(text)
            if match:
                raise AssertionError(f"Privacy/hygiene violation ({label}) in {path.relative_to(ROOT)}: {match.group(0)!r}")


def main() -> int:
    validate_skill()
    validate_references_and_repo()
    validate_privacy()
    print("validate_skill: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
