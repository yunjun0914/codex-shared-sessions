---
name: codex-lab-onboarding
description: Guide a user through setting up shared Codex app and tmux clients, optionally with an integration manager and one experiment agent per Git branch. Use for this repository's onboarding and recovery, not for ordinary coding tasks.
---

# Guided shared sessions and experiment management

Read [the staged onboarding guide](references/onboarding.md) fully before setup or recovery. It is also available to Codex when the user opens this repository through the root AGENTS.md.

- First explain the distinction between a shared connection, the integration-manager role, branch agents, independent worktrees and actual experiment jobs. Ask whether the user wants connection-only mode or the full manager layout.
- Speak in the user's chosen language. Before each meaningful step state what you will do, why and whether it changes files, sessions or services; afterward report evidence and remaining work. Explain every session-specific label on first use.
- Follow the guide's dialogue contract: introduce yourself as the installer, show a roadmap/current stage, distinguish user and agent duties, and end the turn at user-dependent steps. Acknowledgements such as “연결했어” allow verification, not assumed success. Answer questions without advancing the stage.
- Advance through the guide in stages. Begin with read-only inspection, propose a concrete configuration, obtain setup consent, validate a single branch, then expand. Do not infer experiment-launch permission from agent creation.
- If the user uses Tailscale, read [Tailscale connection guidance](references/tailscale.md) before connection setup or troubleshooting. Distinguish ordinary SSH over Tailscale from Tailscale SSH; preserve existing authentication and access policies.
- Keep all private paths, UUIDs, notes and credentials outside the public clone. Existing repositories, worktrees, AGENTS.md guidance and active jobs belong to the user; inspect and preserve them.
- Use the provided commands rather than inventing pane indices or copying a developer's private setup. The lab's dedicated tmux socket must not be confused with a user's preexisting default socket.
- Record progress in a private onboarding note: stage, user decisions, actual config path, verified evidence, unresolved issues and the next step. Resume from that record after interruption; do not repeat completed mutations.
- A setup instruction is not a background goal. Do not schedule polling or automatically submit, cancel or retry jobs. Monitoring requires an explicit cadence and authorization boundary.
- For subsequent management, follow the manager/experiment role guidance installed in each workspace. The manager delegates, but must verify that the intended branch agent actually received and began a task.
- Offer Notion conversation backup once after the chosen core setup is verified. Only if requested, read [optional backup onboarding](references/notion-backup.md). No sync implementation is bundled; no private integration, destination or credential is a public default.
