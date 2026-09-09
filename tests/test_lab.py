import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('lab_cli', str(ROOT / 'codex-lab'))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)
THREAD1 = '00000000-0000-4000-8000-000000000001'
THREAD2 = '00000000-0000-4000-8000-000000000002'


class LabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex-lab-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        subprocess.run(['git', 'init', '-b', 'main', str(self.repo)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                        'commit', '--allow-empty', '-m', 'fixture'], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(self.repo), 'branch', 'baseline'], check=True)
        self.config = self.root / 'lab.json'
        self.data = {'language': '한국어', 'manager': {'name': 'main', 'cwd': str(self.root / 'manager'), 'thread': THREAD1},
                     'experiments': [{'name': 'demo-baseline', 'cwd': str(self.root / 'baseline'),
                                      'repo': str(self.repo), 'branch': 'baseline', 'thread': THREAD2, 'logs': []}]}
        self.save()

    def save(self):
        self.config.write_text(json.dumps(self.data))

    def lab(self):
        return module.Lab(self.config, 'fixture')

    def test_readonly_plan_does_not_create_directories(self):
        result = subprocess.run([sys.executable, str(ROOT / 'codex-lab'), '--config', str(self.config), 'plan'],
                                check=True, capture_output=True, text=True)
        self.assertIn('Plan only', result.stdout)
        self.assertFalse((self.root / 'manager').exists())
        self.assertFalse((self.root / 'baseline').exists())
        self.assertFalse((self.root / 'lab-state').exists())

    def test_default_socket_is_refused(self):
        with self.assertRaises(ValueError):
            module.Lab(self.config, 'default')

    def test_prepare_and_guide_preserve_existing_text(self):
        lab = self.lab()
        lab.prepare('main')
        lab.prepare('demo-baseline')
        guide = self.root / 'baseline/AGENTS.md'
        guide.write_text('# Existing user rules\nDo not remove.\n')
        lab.guide('demo-baseline')
        before = guide.read_text()
        lab.guide('demo-baseline')
        self.assertEqual(before, guide.read_text())
        self.assertTrue(before.startswith('# Existing user rules\nDo not remove.'))
        self.assertIn('Branch experiment agent role', before)
        self.assertTrue((self.root / 'lab-state/notes/demo-baseline.md').is_file())
        self.assertEqual(module.call('git', '-C', str(self.repo), 'branch', '--show-current'), 'main')

    def test_conflicting_guidance_is_not_overwritten(self):
        lab = self.lab()
        lab.prepare('main')
        guide = self.root / 'manager/AGENTS.md'
        text = '<!-- codex-lab:start -->old<!-- codex-lab:end -->'
        guide.write_text(text)
        with self.assertRaises(ValueError):
            lab.guide('main')
        self.assertEqual(guide.read_text(), text)

    def test_wrong_repo_is_rejected(self):
        self.data['experiments'][0]['cwd'] = str(self.repo)
        self.save()
        with self.assertRaises(ValueError):
            self.lab().verify('demo-baseline')

    def test_duplicate_uuid_and_directory_rejected(self):
        for field, value in [('thread', THREAD1), ('cwd', self.data['manager']['cwd'])]:
            old = self.data['experiments'][0][field]
            self.data['experiments'][0][field] = value
            self.save()
            with self.assertRaises(ValueError):
                self.lab()
            self.data['experiments'][0][field] = old

    def test_restore_without_uuid_fails_before_tmux(self):
        lab = self.lab()
        lab.prepare('main')
        lab.prepare('demo-baseline')
        self.data['experiments'][0]['thread'] = None
        self.save()
        result = subprocess.run([sys.executable, str(ROOT / 'codex-lab'), '--config', str(self.config), 'restore'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('every saved UUID', result.stderr)

    def test_ssh_log_quoting_and_monitor(self):
        lab = self.lab()
        args = module.shlex.split(lab.follower({'host': 'my-host', 'path': '/tmp/a; echo unsafe'}))
        self.assertEqual(args[:5], ['ssh', '-T', '-o', 'BatchMode=yes', 'my-host'])
        self.assertEqual(module.shlex.split(args[5]), ['tail', '-n', '60', '-F', '--', '/tmp/a; echo unsafe'])
        self.assertIn('squeue', lab.monitor_command({'monitor': {'host': None, 'kind': 'slurm'}}))

    def test_tell_preview_and_busy_guard(self):
        lab = self.lab()
        msg = self.root / 'task.txt'
        msg.write_text('Inspect only. Do not launch.')
        with patch.object(lab, 'pane', return_value='%1'), patch.object(lab, 'tmux') as tmux:
            lab.tell('demo-baseline', msg, False)
            tmux.assert_not_called()
            with patch.object(lab, 'capture', return_value='Working (esc to interrupt)'):
                with self.assertRaises(ValueError):
                    lab.tell('demo-baseline', msg, True)
            tmux.assert_not_called()

    def test_optional_install_preserves_core_and_refuses_second_install(self):
        env = {**os.environ, 'CODEX_SHARED_INSTALL_DIR': str(self.root / 'bin'),
               'CODEX_SHARED_DATA_DIR': str(self.root / 'data')}
        subprocess.run(['bash', str(ROOT / 'install.sh')], env=env, check=True, capture_output=True)
        subprocess.run(['bash', str(ROOT / 'install.sh'), '--experiments'], env=env, check=True, capture_output=True)
        self.assertEqual((self.root / 'bin/codex-lab').read_bytes(), (ROOT / 'codex-lab').read_bytes())
        self.assertTrue((self.root / 'data/templates/manager.md').is_file())
        self.assertTrue((self.root / 'data/skills/codex-lab-onboarding/SKILL.md').is_file())
        again = subprocess.run(['bash', str(ROOT / 'install.sh'), '--experiments'], env=env, capture_output=True)
        self.assertNotEqual(again.returncode, 0)

    @unittest.skipUnless(shutil.which('tmux'), 'tmux optional')
    def test_real_layout_focus_logs_and_restore_on_private_socket(self):
        # Fresh TMUX_TMPDIR plus -f /dev/null prevents access to real sessions/config.
        tools = self.root / 'tools'
        tools.mkdir()
        fake = tools / 'codex'
        fake.write_text('#!' + sys.executable + '\nimport sys,time\n'
                        'if sys.argv[1:] == ["--help"]: print("--remote")\n'
                        'elif "--remote" in sys.argv: print("TEST AGENT", flush=True); time.sleep(120)\n')
        fake.chmod(0o755)
        env = {'TMUX_TMPDIR': str(self.root), 'TMUX': '', 'CODEX_SHARED_BIN': str(fake),
               'CODEX_HOME': str(self.root / 'codex-home')}
        with patch.dict(os.environ, env):
            lab = self.lab()
            try:
                for name in lab.entries:
                    lab.prepare(name)
                    lab.guide(name)
                    lab.up(name)
                agent = lab.pane('demo-baseline', 'codex')
                manager = lab.pane('main', 'codex')
                original = lab.tmux('display-message', '-p', '-t', agent, '#{pane_pid}')
                manager_pid = lab.tmux('display-message', '-p', '-t', manager, '#{pane_pid}')
                rows = lab.tmux('list-panes', '-t', 'demo-baseline:0', '-F', '#{@codex-lab-role}').splitlines()
                self.assertEqual(set(rows), {'codex', 'log-0'})
                lab.focus('demo-baseline')
                self.assertEqual(lab.pane('view-demo-baseline', 'codex'), agent)
                # Direct monitor selection must not change the grouped view's selected window.
                lab.tmux('select-window', '-t', 'demo-baseline:1')
                self.assertEqual(lab.tmux('display-message', '-p', '-t', 'view-demo-baseline:', '#{window_index}'), '0')
                log1, log2 = self.root / 'one.out', self.root / 'two.out'
                log1.write_text('FIRST LOG\n')
                log2.write_text('SECOND LOG\n')
                lab.entries['demo-baseline']['logs'] = [{'host': None, 'path': str(log1)}, {'host': None, 'path': str(log2)}]
                lab.logs('demo-baseline')
                self.assertIsNotNone(lab.pane('demo-baseline', 'log-1'))
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    output = lab.tmux('capture-pane', '-p', '-t', lab.pane('demo-baseline', 'log-0'))
                    if 'FIRST LOG' in output:
                        break
                    time.sleep(0.1)
                self.assertIn('FIRST LOG', output)
                lab.entries['demo-baseline']['logs'] = [{'host': None, 'path': str(log1)}]
                lab.logs('demo-baseline')
                self.assertIsNone(lab.pane('demo-baseline', 'log-1', optional=True))
                self.assertEqual(lab.tmux('display-message', '-p', '-t', agent, '#{pane_pid}'), original)
                self.assertEqual(lab.tmux('display-message', '-p', '-t', manager, '#{pane_pid}'), manager_pid)
                lab.up('main')
                self.assertEqual(lab.pane('main', 'codex'), manager)
                lab.tmux('kill-server')
                # A fake reboot reuses the saved UUIDs and rebuilds the view.
                result = subprocess.run([sys.executable, str(ROOT / 'codex-lab'), '--config', str(self.config),
                                         '--socket', 'fixture', 'restore'], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(lab.pane('view-demo-baseline', 'codex'), lab.pane('demo-baseline', 'codex'))
                lab.tmux('new-session', '-d', '-s', 'unrelated', 'sleep 120')
                with self.assertRaises(ValueError):
                    lab.up('main')
            finally:
                subprocess.run(['tmux', '-L', 'fixture', 'kill-server'], capture_output=True, timeout=10)


if __name__ == '__main__':
    unittest.main()
