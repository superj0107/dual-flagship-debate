"""Exercise the real PowerShell entry point without starting model CLIs."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")
SOURCE = Path(__file__).resolve().parents[1] / "hosts/windows-cli/run-debate.ps1"


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "requires Windows PowerShell")
class WindowsEntryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sandbox = tempfile.TemporaryDirectory(prefix="debate Windows 中文 ")
        self.addCleanup(self.sandbox.cleanup)
        self.root = Path(self.sandbox.name)
        self.wrapper = self.root / "repo/hosts/windows-cli/run-debate.ps1"
        self.wrapper.parent.mkdir(parents=True)
        shutil.copyfile(SOURCE, self.wrapper)
        engine = self.root / "repo/skills/dual-flagship-debate/scripts/run_debate.py"
        engine.parent.mkdir(parents=True)
        engine.write_text(
            "import json, os, pathlib, sys\n"
            "args = sys.argv[1:]\n"
            "config_path = pathlib.Path(args[args.index('--config') + 1])\n"
            "raw = config_path.read_bytes()\n"
            "record = {'argv': args, 'cwd': os.getcwd(), 'config_path': str(config_path),\n"
            "          'config': json.loads(raw.decode('utf-8')),\n"
            "          'has_bom': raw.startswith(b'\\xef\\xbb\\xbf'),\n"
            "          'config_text': raw.decode('utf-8')}\n"
            "pathlib.Path(os.environ['ENTRY_CAPTURE']).write_text(\n"
            "    json.dumps(record, ensure_ascii=False), encoding='utf-8')\n"
            "print('engine answer')\n"
            "print('engine diagnostic', file=sys.stderr)\n"
            "sys.exit(int(os.environ.get('ENTRY_EXIT', '0')))\n",
            encoding="utf-8",
        )
        self.caller = self.root / "caller & 中文"
        self.caller.mkdir()
        self.workdir = self.root / "target repo & 中文"
        self.workdir.mkdir()
        self.topic = self.caller / "topic & 中文.md"
        self.topic.write_text("议题与基线", encoding="utf-8")
        self.extra = self.caller / "system & 中文.md"
        self.extra.write_text("团队约定", encoding="utf-8")
        self.capture = self.root / "engine-capture.json"
        self.temp = self.root / "temporary config"
        self.temp.mkdir()
        self.sentinel = self.temp / "keep-existing-file.txt"
        self.sentinel.write_text("unrelated", encoding="utf-8")
        self.bin_dir = self.root / "fake CLI bin"
        self.bin_dir.mkdir()
        # These isolate the old implementation during the red phase as well.
        for command in ("codex", "claude"):
            (self.bin_dir / f"{command}.cmd").write_text(
                "@echo off\necho legacy diagnostic 1>&2\nexit /b 7\n", encoding="ascii"
            )
        for command in ("python3", "python"):
            (self.bin_dir / f"{command}.cmd").write_text(
                f'@echo off\n"{sys.executable}" %*\nexit /b %errorlevel%\n',
                encoding="utf-8",
            )
        self.env = os.environ.copy()
        self.env.update(
            PATH=str(self.bin_dir) + os.pathsep + self.env.get("PATH", ""),
            ENTRY_CAPTURE=str(self.capture),
            TEMP=str(self.temp),
            TMP=str(self.temp),
            PYTHONUTF8="1",
            PYTHONIOENCODING="utf-8",
        )

    def run_entry(self, *arguments: str, engine_exit: int = 0) -> subprocess.CompletedProcess:
        env = dict(self.env, ENTRY_EXIT=str(engine_exit))
        return subprocess.run(
            [POWERSHELL, "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(self.wrapper), "-TopicFile", self.topic.name,
             "-WorkDir", os.path.relpath(self.workdir, self.caller), *arguments],
            # The relative WorkDir deliberately starts from the invocation directory.
            cwd=self.caller,
            env=env,
            capture_output=True,
            timeout=30,
        )

    def read_capture(self, result: subprocess.CompletedProcess) -> dict:
        self.assertTrue(self.capture.is_file(), result.stdout.decode(errors="replace") + result.stderr.decode(errors="replace"))
        return json.loads(self.capture.read_text(encoding="utf-8"))

    def assert_temp_cleaned(self, record: dict) -> None:
        self.assertFalse(Path(record["config_path"]).exists())
        self.assertEqual(list(self.temp.iterdir()), [self.sentinel])

    def test_engine_failure_exit_code_and_streams_are_preserved(self) -> None:
        # Only legacy parameters: the old runner swallows its failing child exits.
        result = self.run_entry("-Rounds", "1", "-TimeoutSec", "2", engine_exit=7)
        self.assertEqual(result.returncode, 7, result.stderr.decode(errors="replace"))
        record = self.read_capture(result)
        self.assertIn(b"engine answer", result.stdout)
        self.assertNotIn(b"engine diagnostic", result.stdout)
        self.assertIn(b"engine diagnostic", result.stderr)
        self.assert_temp_cleaned(record)

    def test_paths_unicode_and_overrides_reach_shared_engine(self) -> None:
        outdir = self.root / "new output & 中文"
        codex_model = "codex 中文 & $model; literal"
        claude_model = "claude 中文 & $model; literal"
        result = self.run_entry(
            "-PythonExecutable", sys.executable, "-OutDir", os.path.relpath(outdir, self.caller),
            "-AppendSystemPrompt", self.extra.name, "-Rounds", "1",
            "-TimeoutSec", "37", "-TotalTimeoutSec", "81",
            "-CodexModel", codex_model, "-ClaudeModel", claude_model,
            "-CodexEffort", "high", "-ClaudeEffort", "medium",
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        record = self.read_capture(result)
        args = record["argv"]
        options = dict(zip(args[::2], args[1::2]))
        self.assertEqual(set(options), {"--config", "--topic", "--rounds", "--workdir", "--out-dir", "--timeout", "--total-timeout", "--append-system-prompt"})
        self.assertEqual(Path(options["--topic"]), self.topic.resolve())
        self.assertEqual(Path(options["--workdir"]), self.workdir.resolve())
        self.assertEqual(Path(options["--out-dir"]), outdir.resolve())
        self.assertEqual(Path(options["--append-system-prompt"]), self.extra.resolve())
        self.assertEqual(options["--rounds"], "1")
        self.assertEqual(options["--timeout"], "37")
        self.assertEqual(options["--total-timeout"], "81")
        self.assertEqual(Path(record["cwd"]), self.caller)
        self.assertEqual(record["config"]["debaters"], {
            "A": {"preset": "codex-cli", "name": "Codex A", "model": codex_model, "effort": "high"},
            "B": {"preset": "claude-code", "name": "Claude B", "model": claude_model, "effort": "medium"},
        })
        self.assertFalse(record["has_bom"])
        self.assertIn("中文", record["config_text"])
        self.assert_temp_cleaned(record)

    def test_each_mode_uses_presets_without_overwriting_model_defaults(self) -> None:
        cases = (
            ("cross-vendor", "codex-cli", "claude-code"),
            ("dual-codex", "codex-cli", "codex-cli"),
            ("dual-claude", "claude-code", "claude-code"),
        )
        for mode, preset_a, preset_b in cases:
            with self.subTest(mode=mode):
                result = self.run_entry("-PythonExecutable", sys.executable, "-Mode", mode)
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                record = self.read_capture(result)
                debaters = record["config"]["debaters"]
                self.assertEqual(debaters["A"]["preset"], preset_a)
                self.assertEqual(debaters["B"]["preset"], preset_b)
                for side in ("A", "B"):
                    self.assertEqual(set(debaters[side]), {"preset", "name"})
                    self.assertTrue(debaters[side]["name"])
                self.assertNotIn("--out-dir", record["argv"])
                self.assertNotIn("--total-timeout", record["argv"])
                self.assertNotIn("--append-system-prompt", record["argv"])
                self.assert_temp_cleaned(record)

    def test_explicit_python_older_than_310_is_reported_before_dispatch(self) -> None:
        python39 = self.root / "python39.cmd"
        python39.write_text("@echo off\necho 3.9.18\nexit /b 0\n", encoding="ascii")
        result = self.run_entry("-PythonExecutable", str(python39))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"3.10", result.stderr)
        self.assertFalse(self.capture.exists())
        self.assertEqual(list(self.temp.iterdir()), [self.sentinel])

    def test_automatic_python_detection_skips_bad_candidates_and_uses_py_3(self) -> None:
        (self.bin_dir / "python3.cmd").write_text(
            "@echo off\necho 3.9.18\nexit /b 0\n", encoding="ascii"
        )
        (self.bin_dir / "python.cmd").write_text(
            "@echo off\nexit /b 8\n", encoding="ascii"
        )
        launcher = self.bin_dir / "fake_py_launcher.py"
        launcher.write_text(
            "import subprocess, sys\n"
            "if sys.argv[1] != '-3': sys.exit(23)\n"
            "sys.exit(subprocess.call([sys.executable, *sys.argv[2:]]))\n",
            encoding="utf-8",
        )
        (self.bin_dir / "py.cmd").write_text(
            f'@echo off\n"{sys.executable}" "{launcher}" %*\nexit /b %errorlevel%\n',
            encoding="utf-8",
        )
        result = self.run_entry(engine_exit=7)
        self.assertEqual(result.returncode, 7, result.stderr.decode(errors="replace"))
        record = self.read_capture(result)
        self.assertEqual(Path(record["argv"][record["argv"].index("--workdir") + 1]), self.workdir)
        self.assert_temp_cleaned(record)


if __name__ == "__main__":
    unittest.main()
