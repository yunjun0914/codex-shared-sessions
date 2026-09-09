# Security and privacy

- Use your own authenticated Codex account and authorized SSH account. This is not a multi-user isolation layer. People sharing one OS/Codex account may access its conversations and credentials.
- Transport is fixed to the local Unix endpoint. Connect desktop clients using supported SSH remote-project setup. Do not expose an unauthenticated app-server listener to the network.
- Directory trust and Codex approval/sandbox controls still apply. The helper does not accept trust prompts or disable safety checks.
- The core session-sharing helper implements no telemetry or transcript upload. The separately installed Notion plugin uploads only explicitly registered workspace turns; see below. Codex itself follows its own service and data policies.
- Keep personal session configs, logs, conversation files, tokens, keys and backups out of public repositories and bug reports. The example uses placeholders only.
- Doctor output contains local paths and daemon metadata. Redact those before sharing. Describe security issues without publishing credentials or private transcripts.
- The helper starts a daemon if needed but does not intentionally stop it. It never kills an existing standalone Codex writer or modifies an unrelated tmux session.
- Reboot services are opt-in. Review systemd lifecycle behavior before using them with active jobs.
- The optional lab uses a dedicated tmux socket, refuses the default socket and checks configuration ownership before changing its settings. Agent messages are preview-only unless the caller explicitly confirms an inspected idle composer; visible-screen checks are not a complete dialog or race detector. Do not treat a message as accepted until the intended agent visibly processes it.
- Role guidance is appended to AGENTS.md only by an explicit guide command. Review it alongside existing project rules. Setup consent does not authorize experiment jobs, Git publication, unattended monitoring or blanket permission approvals.

This is an unofficial convenience tool, not a guarantee against incompatible upstream changes. Test upgrades on a disposable conversation first.

## Optional Notion backup

The optional `codex-lab-notion` plugin sends selected user prompts and final assistant text to the user's chosen Notion destination. It is not enabled by the main installer. Review workspace scope, permissions and hooks first. Tokens are entered only via a hidden prompt, stored privately, never accepted as command arguments. Treat both the local queue and remote pages as private conversation data. `#nosync` excludes a new turn; it is not a deletion mechanism for already-uploaded history. Pausing does not revoke already-in-flight requests or remove old records.

Only one capture host/queue should own a named workspace. Local worker locking and chunk checks reduce duplicates, but there is no distributed exactly-once guarantee. Restored context is untrusted historical text, not new authorization, and is not an original Codex-state backup. Real hook delivery and Notion permissions must be verified by the user; repository tests use fake API responses.
