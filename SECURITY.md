# Security and privacy

- Use your own authenticated Codex account and authorized SSH account. This is not a multi-user isolation layer. People sharing one OS/Codex account may access its conversations and credentials.
- Transport is fixed to the local Unix endpoint. Connect desktop clients using supported SSH remote-project setup. Do not expose an unauthenticated app-server listener to the network.
- Directory trust and Codex approval/sandbox controls still apply. The helper does not accept trust prompts or disable safety checks.
- No telemetry, transcript synchronization or third-party upload is implemented by this helper. Codex itself follows its own service and data policies.
- Keep personal session configs, logs, conversation files, tokens, keys and backups out of public repositories and bug reports. The example uses placeholders only.
- Doctor output contains local paths and daemon metadata. Redact those before sharing. Describe security issues without publishing credentials or private transcripts.
- The helper starts a daemon if needed but does not intentionally stop it. It never kills an existing standalone Codex writer or modifies an unrelated tmux session.
- Reboot services are opt-in. Review systemd lifecycle behavior before using them with active jobs.

This is an unofficial convenience tool, not a guarantee against incompatible upstream changes. Test upgrades on a disposable conversation first.
