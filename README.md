# codex-shared-sessions

Use the **same Codex conversation** from a desktop app connected over SSH and a tmux terminal on your server.

This is a small, unofficial Linux helper. It uses Codex's existing local app-server and `--remote unix://` client mode; it does not copy transcripts, share accounts, or implement a new AI backend. Each user supplies their own Codex login and SSH access. No private server configuration or conversation data is included.

[한국어 안내](docs/README.ko.md) · [Recovery](docs/recovery.md) · [Security](SECURITY.md)

Licensed under the [MIT License](LICENSE).

## Requirements and compatibility

- Linux server, Python 3.9+, an authenticated Codex CLI; tmux for the optional session commands.
- A desktop app with SSH remote-project support on your client computer.
- Codex must support `--remote unix://`, `app-server daemon start`, and `app-server daemon version`.
- The underlying shared-thread workflow was manually verified with Codex CLI **0.153.4**. This helper has unit tests, an isolated real-tmux test with a fake Codex, and a live read-only capability check; no claim is made that every app/CLI version works.
- App and terminal must use the same server user, Codex data directory and app-server. Custom `CODEX_HOME` must match on both sides.

The official [remote-connections guide](https://developers.openai.com/codex/remote-connections) describes SSH setup. The [app-server reference](https://developers.openai.com/codex/app-server) describes the server behind Codex clients. This repository is not an OpenAI product or a guarantee of future CLI compatibility.

## Install on your server

```bash
git clone https://github.com/yunjun0914/codex-shared-sessions.git
cd codex-shared-sessions
bash install.sh
export PATH="$HOME/.local/bin:$PATH"
codex-shared doctor
```

Review the source before installing. Installation copies one script into `~/.local/bin`; it does not log in, edit Codex config, modify tmux config, enable boot services, or start model work. Set `CODEX_SHARED_INSTALL_DIR` to choose another destination. Existing files are not overwritten.

If the CLI is not on PATH, the helper checks the user's standalone installation and `~/.local/bin/codex`. `CODEX_SHARED_BIN=/absolute/path/to/codex` explicitly selects a binary, including under systemd.

## Join an existing conversation

First let an existing **standalone** CLI finish its current response, then exit it normally. Do not kill active work or delete lock files. A standalone writer and an app-server writer cannot safely own the same conversation simultaneously.

Replace `YOUR_THREAD_UUID` with the existing conversation UUID, not a tmux name or a helper-agent UUID:

```bash
codex-shared run --cwd ~/projects/my-project --thread YOUR_THREAD_UUID
```

In the desktop app, connect to the same SSH user/host and project, then open that **same existing conversation**. If the app has a stale view, close and reopen the conversation. A new chat in the app has a different UUID and will not share this thread.

Approve directory trust yourself when prompted. Send one short message and verify the same message and answer appear in both clients. Screenshots pasted through the app are part of that same conversation. Connecting another screen does not itself submit a second model task.

To start a new conversation instead, omit `--thread`. Record its UUID before configuring reboot restoration. The Codex CLI displays a resume command on normal exit; do not assume the newest transcript in a directory is the correct thread.

## Optional tmux client

```bash
codex-shared tmux my-project --cwd ~/projects/my-project --thread YOUR_THREAD_UUID
tmux attach -t cs-my-project
```

Names are prefixed with `cs-`. Existing matching managed sessions are left alone; unrelated or differently configured sessions are refused. Exited panes are kept for inspection. Creating a pane is **not proof of a successful connection**: attach and check trust prompts or errors. The helper does not change your mouse bindings or desktop layout.

You can also run `codex-shared run ...` inside a pane you already manage. Branch-specific worktrees, log panes and experiment scheduling are intentionally outside the core tool. Notion, Slurm and any particular repository are not dependencies.

## Reboot and reset

Copy and edit `examples/sessions.example.json` outside this repository. Restore entries require saved UUIDs, preventing accidental creation of new chats at every boot.

```bash
codex-shared restore --config ~/.config/codex-shared-sessions/sessions.json --dry-run
codex-shared restore --config ~/.config/codex-shared-sessions/sessions.json
```

See [recovery instructions](docs/recovery.md) before opting into systemd restoration. **Reinstalling this repository does not restore your transcripts or credentials.** No background polling, automatic job submission or timer is installed.

## Tests

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh
```

Tests do not call a real model or modify your live tmux server. `doctor` only checks CLI capabilities and daemon status; it does not start the daemon.

## Uninstall or upgrade

The installed file is `~/.local/bin/codex-shared` unless you selected another destination. Back up and remove that specific file to uninstall or before reinstalling. Do not remove Codex's data directory. If you opted into the example service, disable it first; stopping it can stop tmux processes started inside its service group. Do not stop a shared daemon just to uninstall this helper: other app clients may still be using it.
