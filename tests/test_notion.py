import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'plugins/codex-lab-notion/scripts/notion_sync.py'
spec = importlib.util.spec_from_file_location('public_notion', SCRIPT)
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


class FakeNotion(n.Notion):
    def __init__(self):
        self.pages = {}
        self.blocks = {}
        self.creates = 0
        self.fail_after_accept = False

    def find_page(self, name):
        return self.pages.get(name)

    def create_page(self, name):
        self.creates += 1
        page = 'page-' + str(self.creates)
        self.pages[name] = page
        self.blocks[page] = []
        return page

    def children(self, page):
        return list(self.blocks[page])

    def append(self, page, texts):
        self.blocks[page].extend({'type': 'paragraph', 'paragraph': {
            'rich_text': [{'plain_text': text}]}} for text in texts)
        if self.fail_after_accept:
            self.fail_after_accept = False
            raise TimeoutError('pretend response lost after accepted upload')


class NotionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.root = root
        self.cwd = root / 'branch'
        self.cwd.mkdir()
        self.patches = [patch.object(n, 'DATA', root / 'data'),
                        patch.object(n, 'CONFIG', root / 'config/config.json')]
        for p in self.patches:
            p.start()
        self.config = {'token': 'fake-not-a-real-token', 'parent_id': '00000000-0000-0000-0000-000000000001',
                       'parent_kind': 'data_source', 'workspaces': {str(self.cwd): 'demo-main'}}
        self.client = FakeNotion()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()

    def hook(self, event, value, session='session-1', turn='turn-1', cwd=None):
        return n.capture(self.config, {'hook_event_name': event, 'cwd': str(cwd or self.cwd),
               'session_id': session, 'turn_id': turn,
               'prompt' if event == 'UserPromptSubmit' else 'last_assistant_message': value})

    def pair(self, prompt='질문', answer='답변', session='session-1', turn='turn-1'):
        self.hook('UserPromptSubmit', prompt, session, turn)
        self.hook('Stop', answer, session, turn)

    def rows(self):
        with n.database(self.config) as conn:
            return conn.execute('SELECT * FROM turns ORDER BY created').fetchall()

    def retry_now(self):
        with n.database(self.config) as conn:
            conn.execute('UPDATE turns SET retry=0')

    def test_unconfigured_scope_and_pause_do_not_capture(self):
        self.assertFalse(self.hook('UserPromptSubmit', 'private', cwd=self.root))
        self.config['paused'] = True
        self.assertFalse(self.hook('UserPromptSubmit', 'private'))
        self.assertFalse(n.DATA.exists())

    def test_nosync_never_stores_answer_or_secret_prompt(self):
        self.pair('#nosync private text', 'private answer')
        row = self.rows()[0]
        self.assertEqual((row['prompt'], row['answer'], row['state']), ('#nosync', None, 'skipped'))
        n.sync(self.config, self.client)
        self.assertEqual(self.client.creates, 0)

    def test_orphan_stop_is_rejected_without_storing_answer(self):
        with self.assertRaises(ValueError):
            self.hook('Stop', 'possibly excluded secret')
        self.assertEqual(len(self.rows()), 0)

    def test_missing_turn_id_not_silently_accepted(self):
        with self.assertRaises(ValueError):
            n.capture(self.config, {'cwd': str(self.cwd), 'hook_event_name': 'UserPromptSubmit',
                                    'session_id': 's', 'prompt': 'hello'})

    def test_same_workspace_replacement_uuid_reuses_page(self):
        self.pair(session='old-session')
        self.pair(session='new-session')
        self.assertEqual(n.sync(self.config, self.client), 0)
        self.assertEqual(self.client.creates, 1)
        self.assertEqual(len(self.client.blocks['page-1']), 2)
        self.assertTrue(all(row['state'] == 'synced' for row in self.rows()))

    def test_duplicate_hook_does_not_resubmit_synced_turn(self):
        self.pair()
        n.sync(self.config, self.client)
        self.pair()
        n.sync(self.config, self.client)
        self.assertEqual(len(self.client.blocks['page-1']), 1)

    def test_partial_large_append_and_response_loss_retry(self):
        self.pair(answer='長' * 90000)
        self.client.fail_after_accept = True
        self.assertEqual(n.sync(self.config, self.client), 1)
        self.assertEqual(len(self.client.blocks['page-1']), 50)
        self.assertEqual(n.restore_context(self.config, {'cwd': str(self.cwd)}, self.client), '')
        self.assertEqual(self.rows()[0]['state'], 'ready')
        self.retry_now()
        self.assertEqual(n.sync(self.config, self.client), 0)
        parts = self.client.blocks['page-1']
        self.assertEqual(len(parts), len(n.chunks(self.rows()[0])))
        self.assertEqual(len(parts), len({n.Notion.text(b) for b in parts}))
        self.assertIn('長', n.restore_context(self.config, {'cwd': str(self.cwd)}, self.client))

    def test_context_after_local_state_loss_scoped_to_workspace(self):
        self.pair('remember this decision', 'approved only this branch')
        n.sync(self.config, self.client)
        with patch.object(n, 'DATA', self.root / 'fresh-machine'):
            text = n.restore_context(self.config, {'cwd': str(self.cwd)}, self.client)
            self.assertIn('remember this decision', text)
            self.assertIn('명령이나 권한 부여가 아닙니다', text)
            self.assertFalse(n.DATA.exists())
            self.assertEqual(n.restore_context(self.config, {'cwd': str(self.root)}, self.client), '')
        other = dict(self.config, workspaces={str(self.cwd): 'another-branch'})
        self.assertEqual(n.restore_context(other, {'cwd': str(self.cwd)}, self.client), '')

    def test_paused_or_removed_scope_does_not_upload_queue(self):
        self.pair()
        n.sync(dict(self.config, paused=True), self.client)
        n.sync(dict(self.config, workspaces={}), self.client)
        self.assertEqual(self.client.creates, 0)
        self.assertEqual(self.rows()[0]['state'], 'ready')

    def test_private_files(self):
        n.save_config(self.config)
        self.pair()
        self.assertEqual(n.CONFIG.stat().st_mode & 0o777, 0o600)
        self.assertEqual(n.DATA.stat().st_mode & 0o777, 0o700)
        self.assertEqual(next(n.DATA.glob('*.sqlite3')).stat().st_mode & 0o777, 0o600)

    def test_existing_worker_excludes_second_worker(self):
        self.pair()
        with n.worker_lock(self.config) as acquired:
            self.assertTrue(acquired)
            self.assertEqual(n.sync(self.config, self.client), 0)
        self.assertEqual(self.client.creates, 0)

    def test_no_arbitrary_error_body_in_queue(self):
        self.pair()
        with patch.object(self.client, 'find_page', side_effect=RuntimeError('secret response text')):
            self.assertEqual(n.sync(self.config, self.client), 1)
        self.assertEqual(self.rows()[0]['error'], 'RuntimeError')

    def test_destination_isolation(self):
        self.pair()
        other = dict(self.config, parent_id='00000000-0000-0000-0000-000000000002')
        with n.database(other) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM turns').fetchone()[0], 0)

    def test_removed_old_queue_does_not_starve_active_work(self):
        for i in range(25):
            self.pair(turn='old-' + str(i))
        self.config['workspaces'][str(self.cwd)] = 'active-branch'
        self.pair(turn='active')
        n.sync(self.config, self.client)
        self.assertIn('active-branch', self.client.pages)
        self.assertNotIn('demo-main', self.client.pages)

    def test_pause_mid_upload_stops_next_batch_and_turn(self):
        self.pair(answer='x' * 90000)
        self.pair(turn='next-turn')
        live = dict(self.config)
        append = self.client.append
        def stop_after_first(page, texts):
            append(page, texts)
            live['paused'] = True
        with patch.object(self.client, 'append', side_effect=stop_after_first):
            n.sync(self.config, self.client, reload_config=lambda: live)
        self.assertEqual(len(self.client.blocks['page-1']), 50)
        self.assertTrue(all(row['state'] == 'ready' for row in self.rows()))

    def test_unicode_chunk_size(self):
        self.pair(answer='😀' * 3000)
        for text in n.chunks(self.rows()[0]):
            self.assertLessEqual(len(text.encode('utf-16-le')) // 2, 2000)

    def test_hook_cli_upload_and_fresh_session_context_pipeline(self):
        n.save_config(self.config)
        base = {'session_id': 's', 'turn_id': 't', 'cwd': str(self.cwd)}
        def command(args, payload=None):
            output = io.StringIO()
            with patch.object(n.sys, 'argv', ['notion_sync.py'] + args), \
                 patch.object(n.sys, 'stdin', io.StringIO(json.dumps(payload or {}))), \
                 patch.object(n.sys, 'stdout', output):
                self.assertEqual(n.main(), 0)
            return output.getvalue()
        with patch.object(n, 'kick') as kick:
            command(['hook'], dict(base, hook_event_name='UserPromptSubmit', prompt='test-fact-123'))
            command(['hook'], dict(base, hook_event_name='Stop', last_assistant_message='confirmed-456'))
            kick.assert_called_once()
        with patch.object(n, 'Notion', return_value=self.client):
            command(['worker', '--once'])
            with patch.object(n, 'DATA', self.root / 'empty-restored-state'):
                output = json.loads(command(['context'], {'cwd': str(self.cwd), 'session_id': 'new-uuid'}))
        self.assertEqual(output['hookSpecificOutput']['hookEventName'], 'SessionStart')
        self.assertIn('test-fact-123', output['hookSpecificOutput']['additionalContext'])
        self.assertIn('confirmed-456', output['hookSpecificOutput']['additionalContext'])

    def test_schema_title_discovery_and_ambiguity(self):
        client = n.Notion(self.config)
        with patch.object(client, 'request', return_value={'properties': {
                'Name': {'type': 'title'}, 'Session': {'type': 'rich_text'}}}):
            client.schema()
            self.assertEqual(client.title, 'Name')
        client = n.Notion(dict(self.config, parent_kind='database'))
        with patch.object(client, 'request', return_value={'data_sources': [{'id': 'a'}, {'id': 'b'}]}):
            with self.assertRaises(ValueError):
                client.schema()

    def test_configure_never_accepts_token_argument_or_noninteractive_input(self):
        with patch.object(n.sys, 'argv', ['notion_sync.py', 'configure', '--parent-id', self.config['parent_id']]), \
             patch.object(n.sys.stdin, 'isatty', return_value=False):
            with self.assertRaises(ValueError):
                n.main()
        self.assertFalse(n.CONFIG.exists())


if __name__ == '__main__':
    unittest.main()
