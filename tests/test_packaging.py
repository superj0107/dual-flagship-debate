"""A copied skill must execute without the surrounding Git repository."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_install_directory_contains_a_working_runner_and_references(self):
        with tempfile.TemporaryDirectory(prefix='skill install 测试 ') as directory:
            root = Path(directory)
            installed = root / 'skills' / 'dual-flagship-debate'
            shutil.copytree(ROOT / 'skills' / 'dual-flagship-debate', installed,
                            ignore=shutil.ignore_patterns('__pycache__'))
            fixture = root / 'fixture.py'
            fixture.write_text('import sys\nprint("INDEPENDENT: synthetic final answer")\n', encoding='utf-8')
            spec = {'cmd': [sys.executable, str(fixture)],
                    'read_only': {'mechanism': 'tool-allowlist', 'evidence': 'No tools; synthetic CLI fixture'}}
            config = root / 'config.json'
            config.write_text(json.dumps({'debaters': {'A': spec, 'B': spec}}), encoding='utf-8')
            workdir = root / 'repo'
            workdir.mkdir()
            topic = root / 'topic.md'
            topic.write_text('Standalone install verification', encoding='utf-8')
            runner = installed / 'scripts' / 'run_debate.py'
            result = subprocess.run([sys.executable, '-B', str(runner), '--config', str(config),
                                     '--topic', str(topic), '--workdir', str(workdir),
                                     '--out-dir', str(root / 'out')], cwd=root, capture_output=True,
                                    text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(list((root / 'out').glob('*.out.md'))), 4)
            self.assertTrue((installed / 'scripts' / 'debate.config.example.json').is_file())
            self.assertTrue((installed / 'references' / 'hosts.md').is_file())


if __name__ == '__main__':
    unittest.main()
