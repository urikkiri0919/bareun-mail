# 바른메일 크롬 확장프로그램 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Windows Chrome에서 초안을 입력하고 향후 보정 결과를 표시할 API 미연결 상태의 바른메일 확장프로그램 기반과 재사용 가능한 보정 규칙을 만든다.

**Architecture:** Manifest V3의 `action.default_popup`이 단일 팝업 UI를 연다. UI는 초안 입력·결과 영역·API 미연결 안내를 제공하며 네트워크, 저장소, 메일 서비스 권한을 사용하지 않는다. 향후 모델 지침은 `docs/correction-rules.md`에 별도 관리한다.

**Tech Stack:** Chrome Manifest V3, HTML, CSS, Python 표준 라이브러리 `unittest`.

**Spec:** `docs/superpowers/specs/2026-10-22-bareun-mail-design.md`

## Global Constraints

- 플랫폼은 Windows의 Chrome Manifest V3 확장프로그램이다.
- 외부 라이브러리는 추가하지 않는다.
- API가 준비되기 전에는 AI 호출·네트워크 전송·초안 저장을 하지 않는다.
- API 키를 확장프로그램 코드나 저장소에 넣지 않는다.
- 특정 메일 서비스 연결, 수신함 접근, 자동 발송을 하지 않는다.
- 기본 단축키는 `Ctrl+Shift+E`이며 사용자는 Chrome 단축키 설정에서 바꿀 수 있다.
- 사실·의미 보존, 맞춤법과 띄어쓰기, 정중한 문맥, 중복 제거, 보정된 메일 텍스트만 반환하는 규칙을 문서화한다.
- API가 연결되지 않은 상태에서 실제 보정 결과인 것처럼 보이는 내용을 만들지 않는다.

## Review Focus

- 빈 초안: 입력칸과 결과 안내가 비어도 레이아웃이 깨지지 않고 보정 버튼이 비활성 상태여야 한다. Task 2의 팝업 계약 테스트에서 확인한다.
- API 미연결: 결과를 지어내지 않고 연결 준비 안내만 보여야 한다. Task 2의 팝업 계약 테스트 및 Task 3 브라우저 확인에서 검사한다.
- 한국어·영문·숫자 혼합 초안: 입력 영역이 이 내용을 그대로 받을 수 있고 넘침 없이 스크롤되어야 한다. Task 3의 실제 Chrome 확인에서 검사한다.
- 좁은 팝업 창: 레이블·입력·결과 영역이 가로로 잘리지 않아야 한다. Task 3의 브라우저 화면 확인에서 검사한다.
- 개인정보·외부 전송: 현재 단계에서 권한·fetch·저장 코드가 없어야 한다. Task 1의 manifest 테스트와 Task 3의 소스/Network 확인에서 검사한다.

---

### Task 1: Manifest, 보정 규칙, 저장소 안내

**Files:**
- Create: `manifest.json`
- Create: `docs/correction-rules.md`
- Create: `README.md`
- Create: `tests/test_manifest.py`
- Create: `tests/test_correction_rules.py`

**Interfaces:**
- Consumes: 승인된 설계 문서 `docs/superpowers/specs/2026-10-22-bareun-mail-design.md`.
- Produces: Manifest V3 팝업 실행 설정과 `docs/correction-rules.md`의 향후 보정 기준.

- [ ] **Step 1: 매니페스트와 규칙의 실패 테스트를 작성한다**

  `tests/test_manifest.py`에서 아래를 검사한다.
  - `test_manifest_uses_v3_and_popup`: `manifest_version == 3`, `action.default_popup == "popup.html"`.
  - `test_default_action_shortcut`: `_execute_action.suggested_key.default == "Ctrl+Shift+E"`.
  - `test_extension_requests_no_permissions`: `permissions` 및 `host_permissions`가 없거나 빈 배열이다.

  `tests/test_correction_rules.py`에서 `docs/correction-rules.md`가 사실 보존, 맞춤법·띄어쓰기, 정중한 비즈니스 문맥, 중복 축약, 모호한 내용 추측 금지, 수정 이유 없이 본문만 출력 요구를 포함하는지 검사한다.

- [ ] **Step 2: 테스트를 실행해 실패를 확인한다**

  Run: `python3 -m unittest discover -s tests -v`
  Expected: 파일이 아직 없어 manifest/rules 테스트가 실패한다.

- [ ] **Step 3: manifest와 규칙 문서, README를 작성한다**

  `manifest.json`은 최소 권한으로 `action.default_popup`과 기본 `Ctrl+Shift+E`의 `_execute_action`만 선언한다. `docs/correction-rules.md`에는 설계 문서의 여섯 규칙을 사용자 기준으로 정리한다. `README.md`에는 목적, API 미연결 상태, Windows Chrome에서 `chrome://extensions`로 압축해제된 확장프로그램을 불러오는 방법, 단축키 변경 위치, 개인정보·보안 주의점을 적는다.

- [ ] **Step 4: 테스트와 JSON 검증을 실행한다**

  Run: `python3 -m unittest discover -s tests -v`
  Expected: 모든 테스트 통과.

  Run: `python3 -m json.tool manifest.json`
  Expected: JSON 파싱 성공.

### Task 2: API 미연결 팝업 UI

**Files:**
- Create: `popup.html`
- Create: `popup.css`
- Create: `tests/test_popup_contract.py`

**Interfaces:**
- Consumes: Task 1의 `manifest.json`이 `popup.html`을 연다.
- Produces: `#draft-input` 초안 입력, `#connection-status` 연결 안내, 비활성 `#correct-button`, `#result-output` 결과 표시 영역.

- [ ] **Step 1: 팝업 구조의 실패 테스트를 작성한다**

  `tests/test_popup_contract.py`의 HTMLParser 기반 검사로 다음을 확인한다.
  - `#draft-input`은 레이블을 가진 `textarea`다.
  - `#connection-status`는 API 미연결 안내를 담는다.
  - `#correct-button`은 API 연결 전 `disabled`다.
  - `#result-output`은 결과를 위한 빈 영역이며 예시 보정 결과를 하드코딩하지 않는다.
  - `popup.css`만 로컬 참조하고 외부 스크립트·외부 폰트·API 호출 코드가 없다.

- [ ] **Step 2: 팝업 테스트를 실행해 실패를 확인한다**

  Run: `python3 -m unittest discover -s tests -v`
  Expected: 팝업 파일이 없어 새 계약 테스트가 실패한다.

- [ ] **Step 3: 입력·상태·결과 영역을 가진 팝업을 구현한다**

  `popup.html`에 접근 가능한 한글 레이블을 붙인 텍스트 입력과 결과 영역을 둔다. `popup.css`는 좁은 팝업에서도 가로 넘침이 없도록 폭을 제한하고, 프로젝트의 색상·글꼴은 간결한 기본 스타일로 정한다. “AI 연결 준비 중” 상태를 명확히 보이며 `보정하기` 버튼은 비활성화한다. 입력 내용은 저장하거나 전송하지 않는다.

- [ ] **Step 4: 전체 테스트를 실행한다**

  Run: `python3 -m unittest discover -s tests -v`
  Expected: manifest, 규칙, 팝업 계약 테스트가 모두 통과한다.

### Task 3: Chrome 로드와 브라우저 확인

**Files:**
- Modify: `README.md` (필요한 경우 검증 결과 반영)
- Test: `manifest.json`, `popup.html`, `popup.css`, `docs/correction-rules.md`

**Interfaces:**
- Consumes: Task 1의 매니페스트·규칙과 Task 2의 팝업.
- Produces: Windows Chrome에서 확인된 압축해제 확장프로그램과 사용자 검토용 미리보기.

- [ ] **Step 1: 전체 자동 검증을 다시 실행한다**

  Run: `python3 -m unittest discover -s tests -v`
  Expected: 모든 테스트 통과.

  Run: `python3 -m json.tool manifest.json`
  Expected: JSON 파싱 성공.

- [ ] **Step 2: Chrome에서 압축해제 확장프로그램을 불러와 확인한다**

  `chrome://extensions`의 개발자 모드에서 저장소 폴더를 불러온다. 도구 모음에서 팝업이 열리고 API 미연결 안내가 보이는지, `Ctrl+Shift+E`가 팝업을 열고 Chrome 단축키 설정에서 변경 가능한지 확인한다. 짧은 한국어·영문·숫자 혼합 텍스트를 입력해도 가로 넘침이나 임의 결과가 없는지 확인한다.

- [ ] **Step 3: 외부 전송·권한을 확인하고 사용자에게 검토를 요청한다**

  매니페스트에 host/메일 권한이 없고, 팝업 코드에 네트워크 호출과 저장 코드가 없는지 확인한다. 브라우저에서 화면을 보여주고 사용자가 확인하기 전에는 커밋하거나 푸시하지 않는다.

## 실행·저장소 게이트

구현 방법은 설계가 단일 UI 중심이므로 Native(이 세션에서 직접 구현) 방식을 권장한다. 사용자가 브라우저에서 확인하고 괜찮다고 승인한 뒤 별도로 커밋·푸시한다. 이 계획 문서 생성만으로 GitHub에 코드를 올리거나 제출하지 않는다.
