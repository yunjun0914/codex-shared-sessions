# Optional experiment management

This adds the integration-manager/branch-agent workflow without making it a dependency of the shared connection tool. Read [the staged onboarding guide](../skills/codex-lab-onboarding/references/onboarding.md), or open this clone in Codex and ask it to guide you. Root `AGENTS.md` routes setup requests to that guide.

## Roles and layout

The manager is your main conversational interface: it explains plans, delegates to the correct branch agent, checks evidence and reports results. Each branch agent has an independent Git worktree, conversation and tmux session. You may talk directly to any branch agent; its private work note keeps the manager informed.

```text
Dedicated tmux socket: codex-lab
main
├── left: integration-manager Codex
└── right: grouped view of the selected branch session
            ├── above: one or two persisted log streams
            └── below: branch-agent Codex

myrepo-baseline
├── window 0: logs above branch-agent conversation
└── window 1: optional Slurm/GPU status monitor
```

The grouped view shares real panes, not screenshots. Its selected window is independent of direct attachments, so opening a branch's monitor need not replace the manager's experiment view. The right pane is interactive, not read-only.

Names are private configuration choices, normally `main` and `<repo-alias>-<branch-slug>`. Unlike core `codex-shared tmux`, the lab does not prefix session names with `cs-`; instead it isolates them on its own socket. Always include `-L codex-lab` when attaching. A custom `--socket` must be used consistently, including in the boot service.

## Install

```bash
bash install.sh --experiments
export PATH="$HOME/.local/bin:$PATH"
```

This installs `codex-shared`, `codex-lab`, templates, examples and the onboarding skill data. It does not globally activate a skill, write personal lab config, enable services or launch agents. If an identical core helper is already installed, it is reused. Different binaries and existing lab/data installations are refused; inspect and back up those specific paths before an upgrade. Custom `CODEX_SHARED_DATA_DIR` must also be set at runtime for an installed lab CLI to find templates.

To make the skill discoverable outside the clone, optionally install the `skills/codex-lab-onboarding` directory into your Codex skill location after reviewing it. Do not overwrite an existing skill. The root AGENTS.md is sufficient when onboarding inside this repository.

## Configure and start

Copy `examples/lab.example.json` to a private location such as `~/.config/codex-shared-sessions/lab.json` and replace paths/branches. Use real saved thread UUIDs, or null only for explicitly approved first launches. Source repositories and local branches must already exist; review clone/fetch/new-branch operations separately.

```bash
codex-lab plan
codex-lab prepare main
codex-lab guide main
codex-lab prepare myrepo-baseline
codex-lab guide myrepo-baseline
codex-lab up main --new
codex-lab up myrepo-baseline --new
codex-lab focus myrepo-baseline
tmux -L codex-lab attach -t main
```

The above `--new` flags are only for initially empty UUIDs. With existing conversations, use `up NAME` without them. Record the actual UUID afterward in private config; never blindly pick the newest transcript or a helper-agent UUID. Before restarting an existing standalone conversation, let its active turn finish and exit normally.

`guide` preserves existing AGENTS.md text and adds a marked role block; a conflicting block is not silently replaced. It creates private notes beside the config in `lab-state/notes`. The user's report language is part of the role block. The agent should read it, explain its role and wait for the first approved task. Adding role guidance may make the worktree dirty; it is not automatically committed.

`up` leaves existing owned sessions intact. It does not repair exited Codex panes or migrate unrelated layouts silently. If an agent did not load, inspect its pane instead of repeatedly calling up.

## Delegate and observe

```bash
codex-lab capture myrepo-baseline
codex-lab tell myrepo-baseline --message-file /path/to/private-task.txt
```

The second command previews only. After checking the actual idle Codex composer and the approved task, add `--confirm-idle` to paste and submit once. This flag does not replace human/agent judgment; guard checks cannot recognize every possible dialog or racing input. Capture afterward to confirm receipt and processing. Never claim that sending text means an experiment launched or succeeded.

`tell` is for the manager to delegate to another idle agent, not for an agent to interrupt itself. Task files may contain sensitive experimental details and should remain private.

Work notes track current instructions, branch/code/config version, job ID, authoritative logs, outputs, last verified status and next action. Manager summaries use those notes plus actual logs/job evidence; they do not rely solely on old conversation text.

## Logs and server status

Each experiment's `logs` array accepts zero, one or two entries:

```json
[
  {"host": null, "path": "/absolute/path/to/run.log"},
  {"host": "my-ssh-alias", "path": "/absolute/path/to/job.out"}
]
```

After reviewing and editing config, use `codex-lab logs NAME`. Zero means an explicit placeholder, one means one pane, two means separate panes. Only owned log-display processes are replaced/removed when changing this layout; log files and experiment jobs remain intact. Local and remote tails follow file names with `tail -F`; SSH uses your existing alias and BatchMode, not stored passwords or weakened host-key checking. A missing file is not replaced with simulated progress. Remote path access still needs normal authorization.

For two Slurm jobs, select each job's `.out`; inspect their `.err` separately during checks. You can instead choose `.out` and `.err` for one job if desired. Persist direct-run stdout/stderr from startup.

Optional experiment field `"monitor": {"host": "my-ssh-alias", "kind": "slurm"}` runs `watch -n 5 squeue --me` in window 1. `kind: "gpu"` runs `nvtop`; `host: null` uses the local machine. Omit `monitor` to show a placeholder. After editing this field, `codex-lab monitor NAME` refreshes only the monitor display. These programs must exist on the target host. This is a lightweight terminal display, **not periodic AI review or automatic job submission**.

Mouse support and the clickable left status-area session tree are configured only on the lab socket. Default tmux prefix is Ctrl-b. No global user tmux config is changed.

## Recovery and boundaries

Register all real UUIDs before `codex-lab restore`. It validates worktrees and UUID presence, starts manager first, then branches and the last saved focus. It does not create worktrees or brand-new conversations during reboot recovery. A nonexistent saved UUID or trust problem still requires checking the actual Codex screen.

`examples/codex-lab-restore.service` is opt-in. Do not enable both lab and core restore services for the same threads. Read [systemd lifecycle and reset cautions](recovery.md) first, including the effects of stopping services with tmux children. Back up private config, `lab-state`, repositories and Codex data separately; GitHub alone does not restore chat history.

No unattended AI monitoring, goal loop, job retry, scheduler submission, branch deletion, Notion handoff or GUI control is automatically enabled. Those require a separately scoped request. The default is to wait for the user after one check or completed task.
