# 앱과 tmux에서 같은 Codex 대화 사용하기

이 프로젝트는 [MIT 라이선스](../LICENSE)로 배포합니다.

## Codex에게 단계별로 설치 안내받기

저장소를 받은 뒤 Codex에서 이 폴더를 열고 이렇게 요청하세요:

> AGENTS.md를 읽고 단계별로 설정을 안내해줘. 통합 관리자와 브랜치별 에이전트의 역할을 먼저 설명하고, 내 환경을 확인한 뒤 설정 변경 전에 물어봐. 실험은 아직 실행하지 마.

기본 공유 연결만 사용할지, **통합 관리자 + 브랜치별 에이전트 + worktree + 로그 화면**까지 구성할지 먼저 고릅니다. Codex가 단계마다 무엇을 왜 하는지 설명하고, 실제 확인 결과를 보고하도록 지침을 넣었습니다.

전체 관리 기능은 `bash install.sh --experiments`로 선택 설치합니다. 관리자는 왼쪽, 선택한 실험의 로그와 전담 에이전트는 오른쪽에 표시됩니다. 실험 에이전트에게 직접 말해도 작업 메모로 맥락을 이어갑니다. 자세한 내용은 [실험 관리 안내](experiment-management.md)와 [단계별 지침](../skills/codex-lab-onboarding/references/onboarding.md)을 참고하세요.

핵심은 대화를 복사하는 것이 아니라, **서버에서 실행 중인 하나의 app-server에 앱과 터미널을 함께 연결하는 것**입니다. 같은 사용자·서버·Codex 데이터 경로·대화 UUID를 사용해야 합니다.

공식 OpenAI 제품이 아닌 Linux용 개인 프로젝트입니다. 연결 방식은 Codex CLI 0.153.4에서 검증했으며 다른 버전은 `doctor`와 실제 연결 테스트가 필요합니다. Python 3.9 이상, Codex 로그인, SSH 접근이 필요하고 tmux는 선택 사항입니다.

## 시작

```bash
git clone https://github.com/yunjun0914/codex-shared-sessions.git
cd codex-shared-sessions
bash install.sh
export PATH="$HOME/.local/bin:$PATH"
codex-shared doctor
```

설치는 실행 스크립트 하나만 복사합니다. 계정 로그인, 설정 변경, 서비스 활성화, 모델 실행은 하지 않습니다. 설치 경로는 `CODEX_SHARED_INSTALL_DIR`, Codex 실행 파일은 `CODEX_SHARED_BIN`으로 지정할 수 있습니다.

독립 실행 중인 기존 Codex가 있다면 작업이 끝난 뒤 정상 종료합니다. 실행 중인 작업을 강제로 끊거나 lock 파일을 삭제하지 않습니다. 기존 UUID를 아래에 넣습니다.

```bash
codex-shared tmux my-project --cwd ~/projects/my-project --thread YOUR_THREAD_UUID
tmux attach -t cs-my-project
```

tmux 없이 `codex-shared run --cwd ... --thread ...`로 실행해도 됩니다. `--thread`를 생략하면 새 대화를 시작합니다. 재부팅 복원에는 반드시 실제 UUID를 기록해야 합니다.

앱에서는 같은 SSH 계정과 프로젝트에 연결하고 동일한 기존 대화를 엽니다. 새 채팅을 만들면 별개 대화입니다. 폴더 신뢰 프롬프트는 직접 확인·승인하세요. 짧은 메시지 하나를 보내 양쪽에 같은 답변이 나오는지 확인합니다.

## 가능한 것과 아닌 것

- 앱에서 이미지 첨부, 터미널에서 작업 확인, 양쪽에서 같은 대화에 입력.
- 기존 tmux 설정을 유지하며 원하는 pane에 연결.
- 선택한 대화 UUID로 재부팅 후 tmux 복원.
- 다른 사람의 계정·대화를 공유하거나 Codex 이용 권한을 제공하는 도구는 아닙니다.
- 선택형 실험 관리 기능은 포함하지만, 실험 자동 제출·주기적 AI 감시는 기본으로 켜지지 않습니다.
- Computer Use, 바탕화면 원격 제어, Notion 동기화는 포함하지 않습니다.

## 초기화 복구

저장소를 다시 clone·설치하고 개인 설정을 복원하면 연결 도구를 재구성할 수 있습니다. **기존 대화 원문·첨부·UUID·인증 정보는 이 저장소에 없으므로 별도 비공개 백업이 필요합니다.** 백업이 없다면 새 대화를 시작해야 합니다.

자세한 절차와 systemd 예시는 [복구 안내](recovery.md), 권한과 개인정보 주의사항은 [보안 안내](../SECURITY.md)를 참고하세요. 자동 복원은 직접 활성화해야 하며, 실험을 자동 제출하거나 주기적으로 모델을 호출하지 않습니다.
