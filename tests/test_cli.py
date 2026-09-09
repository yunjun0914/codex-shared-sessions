import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'codex-shared'
loader = importlib.machinery.SourceFileLoader('shared', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
shared = importlib.util.module_from_spec(spec)
loader.exec_module(shared)
THREAD = '00000000-0000-4000-8000-000000000001'


class SharedTests(unittest.TestCase):
    def test_resume_argv_no_shell_evaluation(self):
        with tempfile.TemporaryDirectory(prefix='shared space;') as cwd:
            self.assertEqual(shared.launch_args('/bin/codex', cwd, THREAD),
                             ['/bin/codex', '--remote', 'unix://', 'resume', THREAD, '-C', cwd])

    def test_invalid_names(self):
        for name in ('', '-bad', 'a:b', 'a.b', 'a;touch file', 'x' * 65):
            with self.subTest(name=name), self.assertRaises(ValueError):
                shared.session_name(name)

    def test_uuid_validation(self):
        for value in ('not-a-uuid', 123, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                shared.thread_id(value)

    def test_missing_explicit_binary_does_not_fallback(self):
        with patch.dict(os.environ, {'CODEX_SHARED_BIN': '/nonexistent/codex'}):
            with self.assertRaises(ValueError):
                shared.codex_binary()

    def test_systemd_path_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / 'packages/standalone/current/codex'
            binary.parent.mkdir(parents=True)
            binary.write_text('#!/bin/sh\nexit 0\n')
            binary.chmod(0o755)
            with patch.dict(os.environ, {'CODEX_HOME': directory, 'PATH': '/nonexistent'}, clear=True):
                self.assertEqual(shared.codex_binary(), str(binary))

    def test_restore_rejects_duplicate_or_missing_uuid(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'config.json'
            entry = {'name': 'demo', 'cwd': directory, 'thread': THREAD}
            for entries in ([entry, entry], [{**entry, 'thread': None}], [{**entry, 'extra': 'x'}]):
                config.write_text(json.dumps({'sessions': entries}))
                with self.assertRaises(ValueError):
                    shared.load_sessions(config)

    def test_existing_unrelated_session_is_not_modified(self):
        with patch.object(shared.shutil, 'which', return_value='/bin/tmux'), \
             patch.object(shared.subprocess, 'run') as run, \
             patch.object(shared, 'command', return_value='unrelated') as command:
            run.return_value.returncode = 0
            run.return_value.stdout = 'cs-demo\n'
            with self.assertRaises(ValueError):
                shared.create_tmux('demo', str(ROOT), THREAD)
            self.assertEqual(command.call_count, 1)
            self.assertEqual(command.call_args.args[1], 'show-options')

    def test_tmux_command_is_quoted_and_namespaced(self):
        with tempfile.TemporaryDirectory(prefix='space ;') as cwd, \
             patch.object(shared.shutil, 'which', return_value='/bin/tmux'), \
             patch.object(shared.subprocess, 'run') as run, \
             patch.object(shared, 'command') as command:
            run.return_value.returncode = 1
            shared.create_tmux('demo', cwd, THREAD)
            args = command.call_args.args
            self.assertEqual(args[4], 'cs-demo')
            decoded = shared.shlex.split(args[7])
            self.assertEqual(decoded[decoded.index('--cwd') + 1], cwd)
            self.assertIn('remain-on-exit', args)

    def test_installer_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, 'CODEX_SHARED_INSTALL_DIR': directory}
            subprocess.run(['bash', str(ROOT / 'install.sh')], env=env, check=True, capture_output=True)
            installed = Path(directory) / 'codex-shared'
            self.assertEqual(installed.read_bytes(), SCRIPT.read_bytes())
            second = subprocess.run(['bash', str(ROOT / 'install.sh')], env=env, capture_output=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(installed.read_bytes(), SCRIPT.read_bytes())

    def test_run_and_doctor_with_fake_codex(self):
        # Subprocess test covers exec and daemon-start behavior without a real model/server.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / 'codex'
            log = root / 'calls.txt'
            binary.write_text('#!' + sys.executable + '\n'
                'import json,os,sys\n'
                'with open(os.environ["FAKE_LOG"], "a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n'
                'if sys.argv[1:] == ["--help"]: print("--remote")\n'
                'else: print("fake-ok")\n')
            binary.chmod(0o755)
            env = {**os.environ, 'CODEX_SHARED_BIN': str(binary), 'CODEX_HOME': str(root / 'data'), 'FAKE_LOG': str(log)}
            subprocess.run([sys.executable, str(SCRIPT), 'doctor'], env=env, check=True, capture_output=True)
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertNotIn(['app-server', 'daemon', 'start'], calls)
            subprocess.run([sys.executable, str(SCRIPT), 'run', '--cwd', directory, '--thread', THREAD],
                           env=env, check=True, capture_output=True)
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertIn(['app-server', 'daemon', 'start'], calls)
            self.assertEqual(calls[-1], ['--remote', 'unix://', 'resume', THREAD, '-C', directory])


if __name__ == '__main__':
    unittest.main()
