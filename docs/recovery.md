# Recovery and troubleshooting

## Ordinary reboot

Restore your mounts and SSH access first. Keep the same operating-system account and Codex data directory. Codex local history must still exist.

Save your **real** session names, working directories and thread UUIDs in `~/.config/codex-shared-sessions/sessions.json`, based on the example. Keep this personal configuration out of Git. Validate it before enabling anything:

```bash
codex-shared doctor
codex-shared restore --config ~/.config/codex-shared-sessions/sessions.json --dry-run
codex-shared restore --config ~/.config/codex-shared-sessions/sessions.json
```

All entries are validated before any tmux session is created. Configuration order is restoration order. Restoring clients does not submit experiment jobs. Attach to every client to inspect startup and trust prompts.

### Optional systemd user service

After a successful manual restore, review the sample unit. Its install path assumes `~/.local/bin/codex-shared`; change it if necessary. A custom `CODEX_HOME` or `CODEX_SHARED_BIN` must also be set consistently in the service and app environment.

```bash
mkdir -p ~/.config/systemd/user
cp -i examples/codex-shared-restore.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable codex-shared-restore.service
```

This opts in for the next user-manager startup; it does not start the service immediately. To start before login, consult your administrator about user lingering and data-mount ordering. This project does not enable lingering or modify system services.

Keep `RemainAfterExit=yes`: processes started by a oneshot unit can otherwise be torn down when it completes. Do not restart/stop a live restore service casually; systemd can terminate tmux processes in its cgroup. Inspect existing jobs first. Actual reboot behavior depends on your system and must be verified locally.

## Complete reset

1. Restore OS dependencies, your repositories, worktrees and data mounts.
2. Install and authenticate Codex through your own secure process.
3. Clone this repository and install the helper.
4. If you have a consistent private backup of Codex history/state/attachments and the personal session config, restore them with correct ownership **before** starting clients. Do not overwrite newer conversations. A live database file copy is not necessarily a consistent backup.
5. Without that backup, start new conversations. A notes/handoff system can restore context, but cannot recreate missing original transcripts or UUIDs.
6. Run the manual checks above, reconnect the app and verify both screens show the same conversation.

No secret, transcript, SSH key, private path, personal session registry or backup is supplied by this repository. Back up your data privately; a complete Codex directory may contain credentials and requires access controls and encryption.

## Troubleshooting

| Symptom | Check |
|---|---|
| `codex` not found under systemd | Use `CODEX_SHARED_BIN` with an absolute path or verify the standard standalone installation. |
| Unsupported `--remote` or daemon command | Run `doctor`; install a compatible CLI. Never fall back to an independent writer for the same UUID. |
| Another app / active-writer conflict | A standalone CLI may own the thread. Let its turn finish, exit it normally, then reconnect through the shared server. |
| Different conversations in the two screens | Compare SSH account, host, `CODEX_HOME`, project and UUID. Reopen the existing conversation in the app. |
| Pane exists but no conversation | Attach and inspect trust prompts, authentication or errors. Pane creation alone is not success. |
| Managed pane exited | Inspect the retained pane first. Remove only that specific session when safe, then recreate it. The helper deliberately does not kill or overwrite it. |
| Desktop app closes or disconnects | Check `codex app-server daemon version` and the terminal. Do not assume a client disconnect stopped the underlying task. |

Do not publish app-server sockets/ports, delete lock files, globally bypass trust, or restart the shared daemon as a first-line fix.
