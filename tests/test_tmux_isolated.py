"""Integration test on a private socket, without Codex or the user's tmux config."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


@unittest.skipUnless(shutil.which('tmux'), 'tmux is optional')
class IsolatedTmuxTest(unittest.TestCase):
    def test_retained_pane_and_collision_protection(self):
        real_tmux = shutil.which('tmux')
        script = Path(__file__).resolve().parents[1] / 'codex-shared'
        with tempfile.TemporaryDirectory(prefix='shared-tmux-test-') as directory:
            root = Path(directory)
            tools = root / 'bin'
            tools.mkdir()
            wrapper = tools / 'tmux'
            wrapper.write_text('#!' + sys.executable + '\nimport os,sys\n'
                               + 'os.execv(' + repr(real_tmux) + ', [' + repr(real_tmux)
                               + ', "-f", "/dev/null", "-L", "isolated"] + sys.argv[1:])\n')
            wrapper.chmod(0o755)
            fake = tools / 'codex'
            calls = root / 'fake-calls.txt'
            fake.write_text('#!' + sys.executable + '\nimport sys,json\n'
                            + 'with open(' + repr(str(calls)) + ', "a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n'
                            +
                            'print("--remote" if sys.argv[1:] == ["--help"] else "FAKE CLIENT OK")\n')
            fake.chmod(0o755)
            env = {**os.environ, 'PATH': str(tools) + os.pathsep + os.environ['PATH'],
                   'TMUX_TMPDIR': directory, 'CODEX_SHARED_BIN': str(fake),
                   'CODEX_HOME': str(root / 'codex-data')}
            env.pop('TMUX', None)
            env.pop('TMUX_PANE', None)
            def tmux(*args):
                return subprocess.run([str(wrapper), *args], env=env, capture_output=True, text=True, timeout=10)
            try:
                result = subprocess.run([sys.executable, str(script), 'tmux', 'smoke', '--cwd', directory],
                                        env=env, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    dead = tmux('list-panes', '-t', 'cs-smoke:', '-F', '#{pane_dead}')
                    if dead.stdout.strip() == '1':
                        break
                    time.sleep(0.1)
                self.assertEqual(dead.stdout.strip(), '1', dead.stderr)
                invocations = [json.loads(line) for line in calls.read_text().splitlines()]
                self.assertEqual(invocations[-1], ['--remote', 'unix://', '-C', directory])
                fingerprint = tmux('show-options', '-v', '-t', 'cs-smoke', '@codex-shared')
                self.assertEqual(json.loads(fingerprint.stdout), [directory, None])
                # An exited client must be inspected, not silently replaced.
                again = subprocess.run([sys.executable, str(script), 'tmux', 'smoke', '--cwd', directory],
                                       env=env, capture_output=True, text=True, timeout=15)
                self.assertNotEqual(again.returncode, 0)
                self.assertIn('exited', again.stderr)
            finally:
                tmux('kill-server')  # Only this test's private socket.


if __name__ == '__main__':
    unittest.main()
