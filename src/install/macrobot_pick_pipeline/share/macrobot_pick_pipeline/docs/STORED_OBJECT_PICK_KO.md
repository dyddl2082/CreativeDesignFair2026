# 저장 위치 기반 찾기·정렬·잡기 설계

## 1. 변경된 전체 흐름

이전의 단순한:

```text
finder → align → pick
```

대신 다음 흐름을 사용한다.

```text
등록 단계
1. 물체가 잡기 좋은 위치에 차체를 둠
2. 물체를 finder/localizer로 안정 검출
3. Pico encoder odom pose 저장
4. base_link 기준 물체 3D 점 저장
5. 물체 점을 odom frame으로 변환해 저장
6. recorded arm grasp trajectory 이름 저장

실행 단계
1. 현재 Pico odom 확인
2. 저장 search pose 근처로 coarse return
3. 저장 방향 주변 finder yaw scan
4. 물체가 보이면 저장 camera-relative point와 비교
5. 작은 TURN_DEG / MOVE_CM 후 매번 재검출
6. 정렬 완료 후 recorded arm trajectory 재생
```

## 2. 왜 odom과 카메라 기준점을 둘 다 저장하는가

encoder odom은 빠르게 대략적인 검색 위치로 돌아가는 데 유용하지만 누적 오차가 있다. 사용자가 관찰한 약 1% 이동 오차와 회전당 약 1cm drift도 이 계층에서 허용한다.

```text
encoder odom: coarse search seed
camera point: final alignment authority
```

따라서 odom만으로 파지하지 않는다.

## 3. 저장 profile의 현재 내부 형식

팀원이 최종 물체 구조체를 담당하므로 아래 형식은 public contract가 아닌 runtime adapter v0이다.

```yaml
schema: macrobot.stored_object_runtime/v0
profiles:
  Buds3:
    object_name: Buds3
    position_scope: pico_odom_session

    search_pose_odom:
      x_m: 0.10
      y_m: -0.04
      yaw_deg: 12.0
      reliable: true
      pico_time_ms: 123456

    object_point_odom:
      x: 0.42
      y: 0.03
      z: 0.10

    alignment:
      reference_point_base:
        x: -0.30
        y: 0.06
        z: 0.10
      bearing_tolerance_deg: 2.0
      range_tolerance_m: 0.015
      turn_speed: 150
      move_speed: 80

    grasp:
      executor: arm_demo
      trajectory: Buds3_FIXED_PICK_V1
      pick_profile: Buds3
```

팀 구조체가 확정되면 `StoredObjectProfileStore`만 adapter로 교체하고 ROS goal/result와 실행 state machine은 유지한다.

## 4. full mode의 search

저장 search pose에 coarse return한 뒤 finder를 시작한다. 바로 찾지 못하면 기록 방향 기준으로 bounded scan한다.

기본 절대 offset:

```text
0, +10, -10, +20, -20, +30, -30, 0 degree
```

마지막에는 기록 방향으로 복귀한 뒤 `OBJECT_NOT_FOUND`로 끝난다.

## 5. visible_test mode

이미 finder가 continuous tracking 중이라고 가정한다.

```text
coarse odom return 생략
finder 새 goal 생략
recent localized detection 요구
visual alignment
recorded grasp
```

이 모드는 현재 배치에서 카메라-차체-팔 연결만 빠르게 확인하는 용도다.

## 6. persistent 위치의 제한

현재 profile은 `pico_odom_session` 범위다.

다음이 일어나면 저장 위치를 그대로 사용할 수 없다.

```text
Pico reboot
RESET_ODOM
로봇을 전원 꺼진 상태에서 손으로 이동
큰 slip 또는 충돌
```

정식 node는 기록 시 Pico `time_ms`와 현재 값을 비교해 명백한 reboot를 감지하면 `POSE_ESTIMATE_UNRELIABLE`로 실패한다.

재부팅을 넘어 유지되는 위치가 필요하면 다음 중 하나가 필요하다.

```text
SLAM map localization
AprilTag / ArUco landmark
외부 motion capture
사용자가 매 boot마다 동일 physical origin에서 RESET_ODOM
```
