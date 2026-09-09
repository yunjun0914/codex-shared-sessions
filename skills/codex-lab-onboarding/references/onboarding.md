# Step-by-step onboarding

Use this as an interactive sequence, not an unattended install script. Explain each stage in the user's language and keep a short private progress note after the user chooses its location. Reading the public repository alone creates no files outside it.

## 1. Explain and select the mode (no changes)

Explain:

- `codex-shared`: the app and terminal connect to the same server-side conversation. It does not copy transcripts or share accounts.
- Integration manager: the user's main conversation; plans, delegates, switches the observed experiment, verifies evidence and summarizes results.
- Branch agent: a separate conversation in one branch's worktree; implements and executes only that branch's approved task.
- Worktree: a separate working directory sharing one Git repository's object store. Agents do not switch branches in another agent's directory.
- Experiment job: the actual training/evaluation process. It is not the agent or tmux pane; its scheduler state, persisted log, exit status and artifacts are authoritative.

Ask connection-only or full experiment management. For full mode describe the layout: manager on the left; selected experiment logs above its agent on the right. A branch session itself has logs above chat, with a separate monitor window. The user may talk directly to a branch agent; it must update its work note so the manager can catch up.

Example in Korean: “저는 실험 통합 관리자로 전체 진행을 정리하고, 각 브랜치의 전담 에이전트에게 작업을 전달합니다. 실제 실험 실행은 별도 승인을 받은 뒤 진행합니다. 우선 연결만 쓸지, 이 관리 구조까지 만들지 정해볼까요?”

## 2. Inspect prerequisites (read-only)

Confirm OS, Python, Git, tmux, Codex capability/auth status, the app's SSH account and whether a shared daemon already exists. Use `python3 codex-shared doctor`; do not print tokens, private config contents or environment dumps. Explain missing prerequisites before proposing installs. Core is Linux-specific; the desktop client is a separate machine.

Inspect existing tmux sessions, current Git branch/status and `git worktree list`. Do not stop agents or jobs. If a standalone CLI owns a wanted conversation, wait for its response to finish and ask the user to exit normally before shared reconnection. Never delete writer locks or restart the daemon to force access.

## 3. Agree on a private configuration

Ask for these in small groups, using what the user already supplied:

1. Existing repository paths, selected branches and worktree locations. Proposed workspace names are `<repo-alias>-<branch-slug>`; explain slug normalization and resolve collisions explicitly.
2. A separate manager directory, report language and a private config location. Default is `~/.config/codex-shared-sessions/lab.json`; private notes live beside it in `lab-state/`.
3. Existing conversation UUIDs, or permission to start new conversations. One role/worktree gets one UUID. Never choose the newest guardian/subagent transcript by timestamp alone.
4. Execution hosts/scheduler and authoritative log paths. Logs may be local or use a reviewed SSH alias. Keep Slurm `.out` and `.err` separate. Display one or two selected streams; inspect `.err` even when only `.out` is displayed.

Read `examples/lab.example.json` from the clone (or installed data directory). Replace all example values before use; these are not real repositories, branches or UUIDs. A null thread is allowed for an explicitly approved first `up --new`, not reboot restoration. `logs: []` displays an honest placeholder.

Show the proposed plan, including all paths and sessions, and ask approval to install the optional tool and prepare worktrees/guidance. Do not quietly enable monitoring, fetch remotes, create branches or apply global tmux settings. For missing Git branches, propose the exact fetch/branch-creation operation separately; `prepare` only uses existing local branches.

## 4. Install and prepare one branch

Connection-only users follow the main README and skip the lab steps. For full mode, after consent:

```bash
bash install.sh --experiments
export PATH="$HOME/.local/bin:$PATH"
codex-lab --config PRIVATE_CONFIG plan
codex-lab --config PRIVATE_CONFIG prepare MANAGER_NAME
codex-lab --config PRIVATE_CONFIG guide MANAGER_NAME
codex-lab --config PRIVATE_CONFIG prepare REPO_BRANCH_NAME
codex-lab --config PRIVATE_CONFIG guide REPO_BRANCH_NAME
```

Substitute actual values; never execute the uppercase placeholders. The optional installer copies the lab CLI, role templates and onboarding skill data, but does not globally activate a skill or start agents. If upgrading from the core-only installation, follow the installer's explicit instructions; never overwrite an unrelated binary.

`prepare` creates a missing manager directory or Git worktree; it validates and leaves existing directories intact. `guide` appends a clearly marked role block to AGENTS.md while preserving other text. Existing conflicting blocks require manual review. It creates a private work note. This can make the experiment worktree dirty; report that and do not auto-commit it.

Report exact paths, branch verification and added guidance. If source repositories or branches differ from the agreed plan, stop this stage and ask.

## 5. Start, explain and verify the layout

Start manager then one branch, using `up NAME` for saved UUIDs. Use `up NAME --new` only when a new conversation was approved.

```bash
codex-lab --config PRIVATE_CONFIG up MANAGER_NAME
codex-lab --config PRIVATE_CONFIG up REPO_BRANCH_NAME
codex-lab --config PRIVATE_CONFIG focus REPO_BRANCH_NAME
tmux -L codex-lab attach -t MANAGER_NAME
```

The lab uses a dedicated `codex-lab` socket; `tmux attach` without `-L` refers to a different server. The left pane is the manager; the right is an interactive grouped view of the experiment. Its window selection is independent of the direct branch session. Mouse support is scoped to this socket; clicking the left status area opens the session tree. Normal prefix is Ctrl-b. Do not overwrite the user's normal tmux config.

Handle directory trust with user consent. Confirm each conversation actually loads; pane creation alone is not success. The user should send a harmless message through the app and see the same answer in tmux, using the same server user, Codex data directory and UUID. Do not run a training job as a connectivity test.

A newly created agent may initially be idle. Send one approved role introduction: “Read your AGENTS.md and work note, explain your role and current branch, then wait. Do not run an experiment.” Verify its answer before calling the role initialized. Store the actual new UUID in private config afterward, preserving every other entry. Do not save a helper-agent UUID.

Do not reconnect the currently speaking manager until its response is complete unless its conversation already lives in the shared server and only the display client is being repaired.

## 6. Teach the everyday workflow

Explain, then demonstrate only an approved read-only task:

1. User asks the manager for an experiment. Manager states branch, model/data, parameters, resources, success criteria and output locations, confirming missing choices.
2. Manager reads the branch's work note and captures its actual agent screen. Preview a message with `codex-lab tell NAME --message-file PRIVATE_MESSAGE_FILE`. After visually confirming an idle composer and authorization, use `--confirm-idle` to submit once. Verify that the correct agent starts; submission is not completion.
3. Branch agent checks code/environment and, only if authorized, submits the job. Record job ID, config, checkpoint and `.out`/`.err` or `run.log` paths in the work note.
4. User can speak directly to that branch agent. Agent updates the work note at meaningful changes so switching sessions does not lose operational context.
5. Manager updates private `logs` paths and runs `codex-lab logs NAME`, then `focus NAME`. One configured stream uses one log pane; two use two separate panes. This follows real persisted output, not a periodically rewritten synthetic summary.
6. On completion, compare scheduler/process exit, error logs, required artifacts and metrics. Report successful/running/pending/failed counts separately. Do not classify disappearance from a queue as success.

Monitor window 1 is a placeholder unless the experiment config includes a reviewed `monitor` field: `{"host":"my-ssh-alias","kind":"slurm"}` for `watch -n 5 squeue --me`, or `kind: "gpu"` for `nvtop`. Use `host: null` for local status. `codex-lab monitor NAME` applies a change to that display only. This is terminal status refresh, not periodic AI review, and does not authorize reading another user's private logs.

Explain how to attach directly (`tmux -L codex-lab attach -t REPO_BRANCH_NAME`) or return to the manager. Notes should contain current task, code/config version, job IDs, log paths, outputs, last verification and next action, not the full transcript.

## 7. Expand and choose recovery/monitoring

Only after the first branch works, repeat prepare/guide/up for approved additional branches. Never switch branches inside managed worktrees. No new repository is required for every branch.

Before boot restoration, every configured conversation needs a real UUID and all worktrees must exist. `codex-lab restore` starts the manager first, then branch clients, then the last saved focus. It does not clone missing repositories, create new chats, submit jobs or start periodic review. Keep config and lab-state privately backed up. Restore source code, model data and Codex conversations through their separate backups after a full reset.

The optional `examples/codex-lab-restore.service` uses the default private config path/socket. Explain user-service lifecycle, lingering/mount dependencies and that stopping a service can stop its tmux children. Enable it only after consent and manual validation; do not enable both core and lab restore services for the same conversations.

Ask about unattended monitoring only if requested. Agree on cadence, selected jobs, error-handling authority, notification method and stop condition. The default is no timer, no polling and no autonomous retries. GUI Computer Use and Notion integrations are optional future integrations, not included or implied by this setup.

## 8. Hand off a self-contained summary

Report: installed mode, manager/branch responsibilities, config and note paths, socket and attach commands, exact worktrees/UUID registration status, observed app/tmux synchronization, test evidence, boot-service state, and remaining blockers. Say which mutations occurred and which were deliberately not enabled. Ask for the first real experiment only after setup is verified; do not invent one.

If interrupted, record the last completed stage and evidence in the private onboarding note. On resumption, inspect actual state before continuing rather than replaying all commands.
