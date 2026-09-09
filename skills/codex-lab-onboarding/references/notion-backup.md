# Optional conversation backup onboarding

Use only after the user requests Notion backup. The public clone now contains the optional **codex-lab-notion** plugin with uploader, hooks, private queue and workspace-scoped context recovery. It is **not installed or enabled by default**. Read `plugins/codex-lab-notion/docs/setup.md` in the source clone before installing or configuring it. If using the standalone installed onboarding skill data, locate the source clone first; do not assume its data directory also contains the plugin. No private page ID, account or server is a default.

## Explain and choose the integration

Present a separate roadmap in the user's language:

> Notion 백업 설정을 시작하겠습니다. 순서는 ① 연동 도구와 백업 범위 선택 → ② Notion 연결 권한 설정 → ③ 서버에 비밀키 안전하게 저장 → ④ 테스트 대화 백업 확인입니다.
> 저는 설치 가능한 도구와 설정을 확인하고, 승인받은 설치 및 테스트를 진행합니다. 사용자님은 Notion 로그인, 대상 페이지 선택, 권한 부여와 비밀키 입력을 직접 해주세요. 지금은 1/4 단계입니다.

Use the bundled public plugin unless the user chooses a different trusted integration. Read its actual documentation and check the installed Codex hook capabilities. Explain where conversations go, which turns/roles are captured, whether past conversations upload, exclusion controls and background behavior. Agree on destination and capture scope before any external write. The public plugin supports stable session names and `#nosync`, but real hook capture/upload/context tests are still required.

If no suitable integration is available, report that prerequisite and offer to defer or separately scope its installation/development. Do not fabricate commands, install an unrelated plugin, or mark backup configured. The core session-sharing setup remains usable.

## Guide the user's Notion actions

Use the selected integration's current setup instructions and official documentation; UI labels and token/OAuth flows can differ. For a token-based integration, link to [Notion integrations](https://www.notion.so/profile/integrations), guide the user to create/select their own integration, then separately grant it access to the chosen destination. Limit access to the intended pages. For OAuth, use the tool's supported authorization UI instead of requesting a token.

Give one current step, explain its purpose, and end the turn with a completion cue such as “대상 페이지에 연결 권한을 주셨다면 ‘권한 줬어’라고 해주세요.” Answer questions without advancing. Do not inspect the secret in the browser, request a screenshot containing it, or claim authorization succeeded from acknowledgement alone.

## Configure credentials privately

Only after implementation and destination are agreed, supply the **actual verified** secure configuration command, labelled with the machine where it must run. Prefer the integration's hidden interactive prompt in the user's own terminal:

> [3/4 · 서버에 비밀키 저장]
> 제가 할 일: 입력이 끝나면 비밀키를 출력하지 않는 연결 검사를 하겠습니다.
> 사용자님이 할 일: 서버 터미널에서 아래의 확인된 설정 명령을 실행하고, 비밀 입력창에 키를 붙여넣어주세요. 키는 이 채팅에 보내지 마세요.
> 완료되면 “입력했어”라고 해주세요.

Insert a real command only after checking the selected implementation. Never put secrets in chat, agent-visible tool arguments, shell history, Git, logs or transcript backups. If tools cannot provide user-only secret entry, let the user run the command directly; lack of a private prompt is not permission to collect the token. Confirm private credential-file permissions without printing contents. If the implementation has no safe supported credential path, stop this optional stage and explain the blocker.

## Verify and hand off

Run a redacted connectivity check, then explain the exact hook/capture definitions before the user trusts/enables them. Upload one agreed harmless test conversation, not private history. Verify capture, delivery status, actual destination content and page identity. When stable per-branch grouping is desired, verify that the selected implementation updates the intended page on another test turn; do not automatically merge/archive existing pages.

Background retry services or auto-upload require explicit consent to their scope and lifecycle. A test upload does not authorize all past conversations. Explain how to pause capture and uploads with the selected tool's verified commands/UI. Record status, destination identity, capture scope, evidence and unresolved issues in private notes, never the secret.

Report “백업 확인 완료” only after end-to-end evidence. Otherwise distinguish authorized, configured, capture-enabled, upload-pending and verified. State that transcript/context backup is not automatically an executable Codex session or the original UUID: exact conversation restoration requires the appropriate Codex data backup. Store credentials in a secret manager or re-enter after reset, never in this public repository.
