"""Behavioral regression tests shared by Windows, macOS and Linux."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'hosts' / 'portable' / 'run_debate.py'
FIXTURE = ROOT / 'tests' / 'fixture_cli.py'
module_spec = importlib.util.spec_from_file_location('debate_runner', ENTRY)
runner = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='debate test 测试 ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.workdir = self.base / 'repo space'
        self.workdir.mkdir()
        self.outdir = self.base / 'out'
        self.topic = self.base / 'topic.md'
        self.topic.write_text('评估实际方案。\nVerified baseline: example.', encoding='utf-8')

    def spec(self, behavior='answer', name='same-cli', **extra):
        cmd = [sys.executable, str(FIXTURE), '--out', '{out}', '--behavior', behavior]
        for key, value in extra.items():
            cmd += ['--' + key.replace('_', '-'), str(value)]
        return {'name': name, 'cmd': cmd,
                'read_only': {'mechanism': 'external-sandbox',
                              'evidence': 'Synthetic fixture only; no model tools enabled.'}}

    def run_cli(self, a=None, b=None, rounds=2, **config_extra):
        config = self.base / 'config.json'
        config.write_text(json.dumps({'debaters': {'A': a or self.spec(), 'B': b or self.spec()},
                                      'workdir': str(self.workdir), **config_extra}), encoding='utf-8')
        env = dict(os.environ, PYTHONIOENCODING='utf-8', GIT_CONFIG_COUNT='0')
        return subprocess.run([sys.executable, '-B', str(ENTRY), '--config', str(config),
                               '--topic', str(self.topic), '--out-dir', str(self.outdir),
                               '--rounds', str(rounds)], cwd=self.base, capture_output=True,
                              encoding='utf-8', errors='replace', env=env, timeout=30)

    def meta(self):
        return json.loads((self.outdir / 'RUN-META.json').read_text(encoding='utf-8'))

    def test_same_names_keep_four_distinct_answers_and_verbatim_crossfeed(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        outputs = list(self.outdir.glob('*.out.md'))
        self.assertEqual(len(outputs), 4)
        for side, opponent in [('A', 'B'), ('B', 'A')]:
            first = (self.outdir / f'r1-{side}.out.md').read_text(encoding='utf-8')
            other = (self.outdir / f'r1-{opponent}.out.md').read_text(encoding='utf-8')
            second = json.loads((self.outdir / f'r2-{side}.out.md').read_text(encoding='utf-8'))
            self.assertEqual(second['side'], side)
            self.assertIn(first, second['prompt'])
            self.assertIn(other, second['prompt'])
        self.assertEqual(self.meta()['status'], 'complete')

    def test_r1_failure_prevents_r2(self):
        result = self.run_cli(a=self.spec('fail-r1', 'A'), b=self.spec(name='B'))
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertFalse(list(self.outdir.glob('r2-*')))
        self.assertEqual(self.meta()['status'], 'failed')

    def test_empty_answer_is_failed_before_r2(self):
        result = self.run_cli(a=self.spec('empty', 'A'), b=self.spec(name='B'))
        self.assertEqual(result.returncode, 3)
        self.assertFalse(list(self.outdir.glob('r2-*')))

    def test_missing_file_does_not_substitute_stdout_as_answer(self):
        result = self.run_cli(a=self.spec('missing', 'A'), rounds=1)
        self.assertEqual(result.returncode, 3)
        self.assertIn('answer', result.stderr.lower())

    def test_existing_directory_is_preserved_and_rejected_before_dispatch(self):
        self.outdir.mkdir()
        stale = self.outdir / 'r1-A.out.md'
        stale.write_text('old answer', encoding='utf-8')
        marker = self.base / 'dispatch-marker'
        result = self.run_cli(a=self.spec(marker=marker))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(stale.read_text(encoding='utf-8'), 'old answer')
        self.assertFalse(marker.exists())

    def test_string_commands_fail_preflight_with_clear_error(self):
        a = self.spec()
        a['cmd'] = f'"{sys.executable}" "{FIXTURE}" --out "{{out}}"'
        result = self.run_cli(a=a)
        self.assertEqual(result.returncode, 2)
        self.assertIn('argv', result.stderr.lower())

    def test_custom_command_without_readonly_evidence_is_not_dispatched(self):
        a = self.spec(marker=self.base / 'should-not-run')
        a.pop('read_only')
        result = self.run_cli(a=a)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.base / 'should-not-run').exists())

    def test_prompt_or_git_status_are_not_readonly_mechanisms(self):
        a = self.spec(marker=self.base / 'should-not-run')
        a['read_only'] = {'mechanism': 'prompt', 'evidence': 'Please do not edit'}
        result = self.run_cli(a=a)
        self.assertEqual(result.returncode, 2)

    def test_cwd_is_explicit_for_both_roles(self):
        result = self.run_cli(a=self.spec(name='A'), b=self.spec(name='B'), rounds=1)
        self.assertEqual(result.returncode, 0, result.stderr)
        for side in 'AB':
            answer = json.loads((self.outdir / f'r1-{side}.out.md').read_text(encoding='utf-8'))
            self.assertEqual(Path(answer['cwd']).resolve(), self.workdir.resolve())

    def test_per_role_cwd_is_audited_as_well(self):
        other = self.base / 'other repo'
        other.mkdir()
        target = other / 'file.txt'
        target.write_text('before', encoding='utf-8')
        a = self.spec(name='A', touch=target)
        a['cwd'] = str(other)
        result = self.run_cli(a=a, b=self.spec(name='B'), rounds=1)
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertTrue((self.outdir / 'WORKSPACE-DIFF-WARNING.txt').exists())

    def test_dirty_file_content_change_is_detected(self):
        target = self.workdir / 'already-dirty.txt'
        target.write_text('dirty before', encoding='utf-8')
        result = self.run_cli(a=self.spec(name='A', touch=target), b=self.spec(name='B'), rounds=1)
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertTrue((self.outdir / 'WORKSPACE-DIFF-WARNING.txt').exists())

    def test_ignored_file_content_change_is_detected(self):
        (self.workdir / '.gitignore').write_text('ignored.txt\n', encoding='utf-8')
        target = self.workdir / 'ignored.txt'
        target.write_text('before', encoding='utf-8')
        result = self.run_cli(a=self.spec(name='A', touch=target), b=self.spec(name='B'), rounds=1)
        self.assertEqual(result.returncode, 4, result.stderr)

    def test_prompt_budget_is_checked_before_dispatch(self):
        marker = self.base / 'marker'
        result = self.run_cli(a=self.spec(marker=marker), max_prompt_chars=10)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(marker.exists())

    def test_output_size_limit_causes_failure(self):
        result = self.run_cli(a=self.spec('oversized', 'A'), b=self.spec(name='B'),
                              rounds=1, max_output_bytes=1000)
        self.assertEqual(result.returncode, 3)

    def test_metadata_records_roles_cwd_hashes_and_readonly_scope(self):
        result = self.run_cli(a=self.spec(name='A'), b=self.spec(name='B'), rounds=1)
        self.assertEqual(result.returncode, 0, result.stderr)
        meta = self.meta()
        self.assertIn('run_id', meta)
        self.assertIn('read_only', meta['pair']['A'])
        self.assertEqual(meta['results']['r1']['A']['cwd'], str(self.workdir.resolve()))
        self.assertEqual(len(meta['results']['r1']['A']['answer_sha256']), 64)

    def test_total_deadline_prevents_r2(self):
        result = self.run_cli(a=self.spec(name='A', delay=3), b=self.spec(name='B', delay=3),
                              timeout_sec=10, total_timeout_sec=1)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertFalse(list(self.outdir.glob('r2-*')))

    def test_timeout_cleans_descendant_processes(self):
        marker = self.workdir / 'descendant-marker'
        a = self.spec('descendant', 'A', touch=marker)
        result = self.run_cli(a=a, b=self.spec(name='B'), rounds=1, timeout_sec=1)
        self.assertEqual(result.returncode, 3, result.stderr)
        time.sleep(2.3)
        self.assertFalse(marker.exists(), 'Descendant survived timeout and wrote later')

    @unittest.skipUnless(shutil.which('git'), 'git required')
    def test_git_errors_are_not_returned_as_clean_state(self):
        subprocess.run(['git', 'init', str(self.workdir)], capture_output=True, check=True)
        old_count = os.environ.get('GIT_CONFIG_COUNT')
        old_key = os.environ.pop('GIT_CONFIG_KEY_0', None)
        os.environ['GIT_CONFIG_COUNT'] = '1'
        try:
            with self.assertRaises(RuntimeError):
                runner.git_status(self.workdir)
        finally:
            if old_count is None:
                os.environ.pop('GIT_CONFIG_COUNT', None)
            else:
                os.environ['GIT_CONFIG_COUNT'] = old_count
            if old_key is not None:
                os.environ['GIT_CONFIG_KEY_0'] = old_key

    def test_unsafe_presets_are_not_offered(self):
        for name in ('gemini-cli', 'aider'):
            self.assertNotIn(name, runner.PRESETS)
        claude = runner.PRESETS['claude-code']['cmd']
        self.assertIn('--safe-mode', claude)
        self.assertIn('--tools', claude)
        self.assertIn('Read,Grep,Glob', claude)
        self.assertIn('--strict-mcp-config', claude)

    def test_round_one_is_dispatched_concurrently(self):
        barrier = self.base / 'barrier'
        barrier.mkdir()
        result = self.run_cli(a=self.spec(name='A', barrier=barrier),
                              b=self.spec(name='B', barrier=barrier), rounds=1)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stdout_answer_mode(self):
        a = self.spec(name='A')
        a['cmd'] = [sys.executable, str(FIXTURE)]
        result = self.run_cli(a=a, b=self.spec(name='B'), rounds=1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.outdir / 'r1-A.out.md').read_text(encoding='utf-8'))['side'], 'A')

    def test_stdout_newlines_are_preserved_exactly_in_answer_file(self):
        a = self.spec(name='A')
        a['cmd'] = [sys.executable, str(FIXTURE), '--behavior', 'crlf']
        result = self.run_cli(a=a, b=self.spec(name='B'), rounds=1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.outdir / 'r1-A.out.md').read_bytes(),
                         b'INDEPENDENT: first line\r\nsecond line\r\n')

    def test_r2_budget_failure_preserves_r1_and_skips_dispatch(self):
        result = self.run_cli(max_prompt_chars=2000)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(len(list(self.outdir.glob('r1-*.out.md'))), 2)
        self.assertFalse(list(self.outdir.glob('r2-*')))

    @unittest.skipUnless(os.name != 'nt', 'POSIX signal semantics')
    def test_sigterm_cancels_and_writes_metadata(self):
        config = self.base / 'config.json'
        marker = self.base / 'started'
        config.write_text(json.dumps({'debaters': {'A': self.spec(name='A', delay=20, marker=marker),
                                                    'B': self.spec(name='B', delay=20)},
                                      'workdir': str(self.workdir)}), encoding='utf-8')
        proc = subprocess.Popen([sys.executable, '-B', str(ENTRY), '--config', str(config),
                                 '--topic', str(self.topic), '--out-dir', str(self.outdir)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: proc.kill() if proc.poll() is None else None)
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue(marker.exists(), 'Fixture did not start')
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=5), 130)
        self.assertEqual(self.meta()['status'], 'cancelled')

    @unittest.skipUnless(os.name == 'nt', 'Windows batch shim')
    def test_windows_batch_shim_preserves_spaces_unicode_and_cwd(self):
        shim = self.base / 'fixture shim.cmd'
        shim.write_text('@"' + sys.executable + '" %*\r\n', encoding='utf-8')
        a = self.spec(name='A')
        a['cmd'][0] = str(shim)
        result = self.run_cli(a=a, b=self.spec(name='B'), rounds=1)
        self.assertEqual(result.returncode, 0, result.stderr + (self.outdir / 'r1-A.log.txt').read_text(encoding='utf-8', errors='replace'))
        answer = json.loads((self.outdir / 'r1-A.out.md').read_text(encoding='utf-8'))
        self.assertTrue(os.path.samefile(answer['cwd'], self.workdir))

    def test_codex_preflight_confirms_effective_mcp_restrictions(self):
        def probe(argv, cwd, **kwargs):
            if '--help' in argv:
                return '--ephemeral --sandbox --ignore-rules'
            if '--version' in argv:
                return 'synthetic codex'
            # Model the CLI's dotted key override semantics, including names
            # with hyphens. Quoted path segments create different config keys.
            disabled = {argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == '-c'}
            return json.dumps([{'name': name, 'enabled': f'mcp_servers.{name}.enabled=false' not in disabled}
                               for name in ('server-one', 'server_two')])
        with mock.patch.dict(runner.prepare_debater.__globals__, {'_probe': probe}):
            spec = runner.prepare_debater({'preset': 'codex-cli'}, 'A', self.workdir)
        overrides = {spec['cmd'][i + 1] for i, arg in enumerate(spec['cmd'][:-1]) if arg == '-c'}
        self.assertIn('mcp_servers.server-one.enabled=false', overrides)
        self.assertIn('mcp_servers.server_two.enabled=false', overrides)

    def test_codex_preflight_blocks_when_mcp_remains_enabled(self):
        def probe(argv, cwd, **kwargs):
            if '--help' in argv:
                return '--ephemeral --sandbox --ignore-rules'
            if '--version' in argv:
                return 'synthetic codex'
            return json.dumps([{'name': 'stubborn', 'enabled': True}])
        with mock.patch.dict(runner.prepare_debater.__globals__, {'_probe': probe}):
            with self.assertRaises(ValueError):
                runner.prepare_debater({'preset': 'codex-cli'}, 'A', self.workdir)

    @unittest.skipUnless(os.name == 'nt', 'Windows junction semantics')
    def test_audit_does_not_follow_windows_junction_outside_workspace(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (outside / 'unrelated.txt').write_text('unrelated content', encoding='utf-8')
        junction = self.workdir / 'linked-directory'
        # Create a junction without elevation. No command text is constructed
        # from arbitrary data: the paths belong to this TemporaryDirectory.
        command = 'mklink /J "' + str(junction) + '" "' + str(outside) + '"'
        prefix = subprocess.list2cmdline([os.environ.get('COMSPEC', 'cmd.exe'), '/d', '/s', '/c'])
        subprocess.run(prefix + ' "' + command + '"', check=True, capture_output=True)
        self.addCleanup(lambda: junction.rmdir() if junction.exists() else None)
        snapshot = runner.snapshot_workspace(self.workdir, self.outdir, 100, 100000)
        self.assertNotIn('linked-directory/unrelated.txt', snapshot['files'])
        self.assertIn('linked-directory', snapshot['files'])

    def test_process_timeout_applies_when_child_never_reads_large_stdin(self):
        import threading
        with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            before = time.monotonic()
            code, error = runner.run_process([sys.executable, '-c', 'import time;time.sleep(2)'],
                                             b'x' * 1048576, self.workdir, output, errors,
                                             .2, threading.Event())
            elapsed = time.monotonic() - before
        self.assertEqual(error, 'timeout')
        self.assertLess(elapsed, 1.5, 'Timeout stalled while writing stdin')

    def test_preflight_obeys_the_global_deadline(self):
        # Real capability subprocess: no model, no paid API, no mocked timeout.
        before = time.monotonic()
        with self.assertRaises(TimeoutError):
            runner._probe([sys.executable, '-c', 'import time;time.sleep(2)'],
                          self.workdir, deadline=before + .2)
        self.assertLess(time.monotonic() - before, 1.5)

    @unittest.skipUnless(shutil.which('git'), 'git required')
    def test_output_inside_git_workspace_is_excluded_from_audit(self):
        subprocess.run(['git', 'init', str(self.workdir)], capture_output=True, check=True)
        self.outdir = self.workdir / 'results' / 'review1'
        result = self.run_cli(rounds=1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.meta()['workspace_changes'], {})

    def test_bom_transcript_hash_matches_raw_file_and_crossfeed(self):
        result = self.run_cli(a=self.spec('bom', 'A'), b=self.spec(name='B'))
        self.assertEqual(result.returncode, 0, result.stderr)
        raw = (self.outdir / 'r1-A.out.md').read_bytes()
        self.assertEqual(self.meta()['results']['r1']['A']['answer_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertIn(raw, (self.outdir / 'r2-B.prompt.md').read_bytes())

    def test_workspace_snapshot_obeys_expired_deadline(self):
        with self.assertRaises(TimeoutError):
            runner.snapshot_workspace(self.workdir, self.outdir, 100, 100000,
                                      deadline=time.monotonic() - 1)


if __name__ == '__main__':
    unittest.main()
