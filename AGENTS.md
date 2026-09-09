# Working with this repository

This repository has two modes: shared Codex clients only, or an optional experiment manager with one agent/worktree per branch. Merely opening the repository is not authorization to install services, launch agents, submit experiments or edit the user's repositories.

When a user asks to set it up, read `skills/codex-lab-onboarding/SKILL.md` and its onboarding reference before acting. Explain the roles in the user's language, ask which mode they want, then follow the staged checklist. Show the next action, its purpose and its effect; after each stage report what was actually verified. Do not dump every question at once or silently run the full setup.

For code maintenance, run `python3 -m unittest discover -s tests -v` and shell syntax checks. Use only temporary repositories and isolated tmux sockets for tests. Do not use the developer's live Codex threads, credentials or tmux server as test fixtures. Do not add personal addresses, paths, experiment identifiers, session UUIDs or private history to public commits.

User configuration, work notes and experiment instructions belong outside this public repository. Match the user's report language, explain project-specific shorthand, and distinguish a running pane from a running job and a successful experiment. No polling, scheduled monitoring, experiment resubmission, branch deletion or Git publication is implied by setup approval.
