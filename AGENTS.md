# Unity Project Rules (유니티 프로젝트 규칙)

이 저장소는 Unity 기반 프로젝트다.  
This repository is a Unity project.

---

## 작업 모드 (Working Mode)

- 기본적으로 분석 → 제안 → 승인 → 수정 순서로 진행한다.
- Default flow: Analyze → Propose → Confirm → Modify

- 사용자가 명시적으로 요청하기 전에는 파일을 수정하지 않는다.
- Do NOT modify files without explicit user request.

---

## 작업 범위 (Scope)

- 수정 가능:
  - `Assets/Scripts/**`

- 제한:
  - `Assets/Prefabs/**` → 수정 금지 (read-only)
  - `Assets/Scenes/**` → 수정 금지
  - `Assets/Materials/**` → 수정 금지

- 금지:
  - 프로젝트 루트 밖 접근 금지
  - Do NOT access outside project root

---

## Unity 특화 규칙 (Unity Specific Rules)

- public API 이름 변경 금지
- Do NOT rename public fields or methods

- 직렬화 필드 (`[SerializeField]`) 변경 주의
- Be careful with serialized fields

- `.meta` 파일은 필요할 때만 수정
- Modify `.meta` files only if absolutely necessary

---

## 금지 (Forbidden)

- 민감 파일 접근 금지:
  - `.env`, `.pem`, `.key`, `.p12`
  - `service-account*.json`
  - `Secrets/**`

- Do NOT access secrets or credentials

- Git 변경 금지:
  - `git commit`
  - `git push`
  - `git reset`
  - `git clean`

- 파일 삭제 금지:
  - `rm`, `del`, `rmdir`

- Unity 실행/빌드 금지:
  - Do NOT run Unity Editor
  - Do NOT build project
  - Do NOT run Addressables build

---

## 허용 작업 (Allowed)

- 코드 분석 (Code analysis)
- 오류 분석 (Error debugging)
- 최소 수정 제안 (Minimal patch suggestion)
- read-only 명령:
  - `git diff`
  - `git status`
  - `grep`, `rg`

---

## 오류 처리 (Error Handling)

예: `NullReferenceException`

- null 체크 확인
- Check object reference
- `GetComponent` 결과 확인
- 초기화 순서 확인

---

## 응답 방식 (Response Format)

1. 원인 (Cause)
2. 해결 방법 (Fix)
3. 주의사항 (Caution)

---

## 중요 원칙 (Important)

- 최소 변경 (Minimal change)
- 안전 우선 (Safety first)
- 명확한 설명 (Clear explanation)