"""Tests for tools/verify_install.py — the installed-copy consistency checker."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = REPO_ROOT / "tools" / "verify_install.py"
SKILL_NAME = "dual-flagship-debate"

_spec = importlib.util.spec_from_file_location("verify_install", VERIFIER)
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)  # type: ignore[union-attr]


def write_skill(directory: Path, marker: str = "baseline") -> None:
    """Materialise a minimal but structurally valid skill directory."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "SKILL.md").write_text(
        f"---\nname: {SKILL_NAME}\ndescription: test fixture long enough to be plausible\n---\n\n# {marker}\n",
        encoding="utf-8",
    )
    (directory / "references").mkdir(exist_ok=True)
    (directory / "references" / "models-and-hosts.md").write_text("Last Verified: 2026-11-27\nnon-normative\n", encoding="utf-8")
    (directory / "references" / "hosts.md").write_text("hosts\n", encoding="utf-8")
    (directory / "scripts").mkdir(exist_ok=True)
    for name in ("run_debate.py", "process_tree.py", "debate.config.example.json"):
        (directory / "scripts" / name).write_text(f"# {name} {marker}\n", encoding="utf-8")


class VerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="verify test 校验 ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.root = self.base / "root"
        write_skill(self.repo / "skills" / SKILL_NAME)
        installed = self.root / SKILL_NAME
        shutil.copytree(self.repo / "skills" / SKILL_NAME, installed)

    def run_verifier(self, *extra: str) -> tuple[int, str]:
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = verify.main(["--repo", str(self.repo), "--roots", str(self.root), *extra])
        return code, buffer.getvalue()

    def test_consistent_install_passes(self) -> None:
        code, output = self.run_verifier()
        self.assertEqual(code, 0, output)
        self.assertIn("consistent", output)

    def test_missing_required_file_is_reported(self) -> None:
        (self.root / SKILL_NAME / "scripts" / "process_tree.py").unlink()
        code, output = self.run_verifier()
        self.assertEqual(code, 1, output)
        self.assertIn("scripts/process_tree.py", output)

    def test_copies_that_disagree_are_reported(self) -> None:
        second = self.base / "root2"
        shutil.copytree(self.root / SKILL_NAME, second / SKILL_NAME)
        (second / SKILL_NAME / "SKILL.md").write_text("---\nname: dual-flagship-debate\ndescription: drift\n---\n", encoding="utf-8")
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = verify.main(["--repo", str(self.repo), "--roots", str(self.root), "--roots", str(second)])
        self.assertEqual(code, 1)
        self.assertIn("disagree", buffer.getvalue())

    def test_no_installed_copy_is_a_problem(self) -> None:
        empty = self.base / "empty"
        empty.mkdir()
        code, output = self.run_verifier()
        self.assertEqual(code, 0)  # the populated root still passes
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = verify.main(["--repo", str(self.repo), "--roots", str(empty)])
        self.assertEqual(code, 1)
        self.assertIn("no installed copy", buffer.getvalue())

    def test_frontmatter_name_must_match_directory(self) -> None:
        skill_md = self.root / SKILL_NAME / "SKILL.md"
        skill_md.write_text("---\nname: something-else\ndescription: x\n---\n", encoding="utf-8")
        code, output = self.run_verifier()
        self.assertEqual(code, 1, output)
        self.assertIn("frontmatter name", output)

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_tag_comparison_detects_unreleased_content(self) -> None:
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}
        for args in (
            ["init", "-q", "-b", "main"],
            ["add", "-A"],
            ["commit", "-q", "-m", "release"],
            ["tag", "-a", "v1.0.0", "-m", "v1.0.0"],
        ):
            subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, env={**__import__("os").environ, **env})

        code, output = self.run_verifier("--tag", "v1.0.0")
        self.assertEqual(code, 0, output)

        # Simulate the failure this tool exists for: someone installs content that was never released.
        (self.root / SKILL_NAME / "SKILL.md").write_text(
            "---\nname: dual-flagship-debate\ndescription: unreleased edit\n---\n", encoding="utf-8"
        )
        code, output = self.run_verifier("--tag", "v1.0.0")
        self.assertEqual(code, 1, output)
        self.assertIn("differs from the released tag", output)

    def test_unknown_tag_exits_two(self) -> None:
        code, _ = self.run_verifier("--tag", "v9.9.9")
        self.assertEqual(code, 2)

    def test_json_output_is_valid(self) -> None:
        code, output = self.run_verifier("--json")
        self.assertEqual(code, 0, output)
        payload = json.loads(output)
        self.assertEqual(payload["problems"], [])
        self.assertTrue(any(copy["present"] for copy in payload["copies"]))


if __name__ == "__main__":
    unittest.main()
