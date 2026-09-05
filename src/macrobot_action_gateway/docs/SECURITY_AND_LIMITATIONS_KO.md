# Code Worker 보안과 현재 한계

## 적용된 방어

- AST allow/deny 검사
- import, file access, subprocess, network API, ROS 직접 접근 금지
- `robot.<canonical API>` 외 메서드 호출 금지
- private/dunder attribute 접근 금지
- 비동기 API handle 저장 및 종료 관리(`WAIT_ACTION`/cancel/STOP) 강제
- recursion 금지
- 모든 for/while에 runtime loop guard 주입
- 최소 builtins만 제공
- 별도 process 실행
- CPU, address-space, output file size, open-file 수 제한
- wall timeout 또는 worker 오류 시 Gateway `abort_run`과 STOP
- `main()` 종료 시 active action이 남아 있으면 자동 취소 후 실행 실패 처리
- 명시적 `--approved` 없이는 실행 안 함

## 중요한 한계

Python의 in-process AST sandbox는 완전한 적대 코드 보안 경계가 아니다. 현재 구현은 승인된 LLM 출력의 실수와 정책 위반을 방지하는 MVP다.

운영판 권장 추가 조치:

```text
전용 비권한 Linux 사용자
read-only root filesystem
mount namespace
network namespace 차단
seccomp / AppArmor
cgroup CPU·memory 제한
일회성 container 또는 microVM
Gateway socket만 bind mount
```

## 현재 기능 한계

- 사양의 timeout/거리/각도 수치는 아직 TBD이며 기본 config는 provisional이다.
- 차체 pose는 odometry가 아니라 성공한 명령 이력 기반이다.
- 부분 이동·취소·통신 실패 후 차체 pose는 `UNRELIABLE`이 된다.
- 팔·그리퍼 상태는 encoder 실측이 아닌 commanded state다.
- `PICK_OBJECT`의 기본 verification은 command sequence 완료다.
- `PLACE_NEXTTO_OBJECT`는 기준 물체를 재탐색한 뒤 semantic reverse-pick을 실행한다. 외부 물체 형상의 완전한 3D 충돌 지도와 release 센서 검증은 아직 없다.
- system primitive 영구 목록과 placement profile schema는 별도 결정이 필요하다.
