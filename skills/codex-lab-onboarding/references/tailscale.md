# Tailscale connection branch

Use during connection setup or recovery when the user uses Tailscale. This changes the route to the server, not the worktree layout or shared-conversation identity. Compatibility is conditional on actual SSH and app tests; this repository has not established an end-to-end Tailscale certification.

## Identify the connection method

Ask for the user's existing connection method and whether both devices already have Tailscale access. Do not ask for passwords, private keys, auth keys or full network inventories. Tailscale can mean two different setups:

- **Ordinary SSH over Tailscale:** a normal SSH server is reached by its Tailscale IP or MagicDNS name (Tailscale's device hostname). Existing SSH keys/passwords and the SSH server's port still apply.
- **Tailscale SSH:** Tailscale also handles SSH authentication and authorization. This uses port 22 and may require browser re-authentication under the network's SSH policy. Do not assume this feature is enabled simply because Tailscale is installed or a command starts with `ssh`.

Keep a working setup. Do not enable Tailscale SSH, replace OpenSSH, change ports, restart networking or relax policies merely to follow an example. A user who only knows “I use Tailscale” should get a guided diagnostic, not be forced to choose unfamiliar authentication terminology.

Official references (consult current documentation when applying version-specific commands or policies): [SSH over Tailscale](https://tailscale.com/docs/reference/ssh-over-tailscale), [Tailscale SSH](https://tailscale.com/docs/features/tailscale-ssh), [Codex SSH connections](https://learn.chatgpt.com/docs/remote-connections).

## Walk through the connection checkpoints

Follow the main guide's user-action/agent-action/acknowledgement pattern. End the turn when waiting for login or UI action. Do not repeat a completed checkpoint just to fit the sequence.

1. **Network access.** On the computer running the desktop app, confirm Tailscale is connected and the intended server is reachable under the applicable network permissions. Use a targeted status/ping check supported by the installed CLI, or ask the user to check the Tailscale app. `tailscale ping VERIFIED_SERVER` can help diagnose the route; replace the placeholder first. It does not prove SSH permission or Codex compatibility. Login, device approval and administrative access grants are user/admin actions. No automatic policy edits.
2. **Normal SSH client.** From that same computer, test `ssh VERIFIED_ALIAS` with the actual existing alias, or use the verified server address and account. Success with `tailscale ssh` alone does not prove the app's OpenSSH path works. Inspect the existing client SSH configuration without disclosing unrelated hosts. If needed, propose one concrete host entry and ask before writing it; preserve other entries. On Windows this belongs to the app user's `.ssh/config`, not a Linux server's config or a different WSL account.
3. **Authentication.** With ordinary SSH, use the existing approved authentication method. With Tailscale SSH, let the user complete any browser check themselves. Distinguish failed network access, denied SSH policy/user, host-key mismatch and re-authentication. Never disable host-key checking or delete known-host entries blindly. If access requires an administrator, report the exact blocked source/destination/account privately and stop that stage.
4. **App and server.** Confirm remote Codex is installed/authenticated and available in the remote login shell, using the main guide's read-only checks. Ask the user to select the verified SSH alias in the app's connections UI. Verify the intended server user, Codex data directory and conversation UUID match the tmux client. Keep the app-server on its local Unix socket: do not expose its port on the public network or the Tailscale network, and do not enable Serve/Funnel for this workflow.
5. **Shared conversation and reconnection.** Run the agreed harmless message test in the app and tmux. With consent and no active turn at risk, test disconnecting/reconnecting the display client without killing the daemon, tmux or jobs. A re-authentication policy may make unattended reconnect require human action; report that limit rather than weakening the policy or promising automatic recovery.

Example host entry, only after resolving the real values and checking for name collisions:

```sshconfig
Host lab-server
    HostName your-server-magicdns-name
    User your-linux-user
```

These are placeholders, not a command to install verbatim. For ordinary SSH retain the actual port and approved identity settings; Tailscale SSH is not a reason to copy an unrelated key configuration.

Example conversation:

> 현재 서버 연결 단계입니다. Tailscale은 서버까지 연결하는 경로이고, 그 위에서 SSH와 Codex 연결을 확인하겠습니다.
> 제가 할 일: 현재 접속 방식과 SSH 설정을 확인하고, 승인받은 변경만 진행하겠습니다.
> 사용자님이 할 일: Codex 앱을 실행하는 컴퓨터에서 Tailscale에 로그인되어 있고 대상 서버가 보이는지 확인해주세요.
> 확인되면 “서버 보여”라고 해주세요. 다음으로 SSH 접속을 확인하겠습니다. 비밀번호나 인증 키는 보내지 마세요.

## Recovery and handoff

Record verified route, SSH mode/alias/account, app/tmux test evidence, and any manual re-authentication requirement in private onboarding notes. Never commit actual device names, addresses, policy files or credentials to this repository.

For reboot recovery, distinguish server-local tmux restoration from remote client access: local clients may restore while Tailscale is unavailable, but SSH/app access and remote log streams still need network readiness. Reboot tests require separate approval and a safe time; do not reboot an experiment server as an installation test. On full reset, restore or re-enroll Tailscale and obtain device approval as needed, then recheck SSH before reconnecting shared conversations. Re-enrollment/expired access is not fixed by deleting Codex state or creating replacement UUIDs.

Return to the main guide after connection checks. Do not claim worktrees, experiments, Notion backup or boot services were configured merely because Tailscale/SSH works.
