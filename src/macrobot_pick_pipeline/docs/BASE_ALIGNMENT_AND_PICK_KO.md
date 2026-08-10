# 기록된 카메라 상대 위치로 차체 정렬 후 잡기

## 1. 설계 목적

로봇이 실제로 물체를 잡을 수 있는 위치에 있을 때 카메라가 보는 물체의 `base_link` 3D 좌표를 한 번 기록한다.

```text
잡을 수 있는 실제 위치
→ 안정된 object point_base 기록
→ alignment profile 저장
```

운영 시에는 현재 물체 좌표와 기록 좌표의 planar bearing/range를 비교한다.

```text
현재 bearing이 다름
→ 작은 TURN_DEG
→ 새 카메라 표본 대기

현재 range가 다름
→ 작은 MOVE_CM
→ 새 카메라 표본 대기

bearing/range가 허용 오차 안
→ pick goal 전달
```

한 번에 큰 open-loop 명령을 보내지 않고, 매 동작 뒤 카메라로 다시 확인하는 visual-servo 방식이다.

---

## 2. 현재 좌표/명령 convention

기본 설정:

```text
로봇 전방 = -base_link.x
로봇 왼쪽 = +base_link.y
Pico TURN_DEG 양수 = 오른쪽 회전
Pico MOVE_CM 양수 = 전진
```

모두 `config/base_alignment.yaml` 파라미터로 변경할 수 있다.

---

## 3. 저장 파일

```text
~/MacRobot/data/alignment/base_alignment_profiles.yaml
```

예:

```yaml
schema: macrobot.base_alignment/v1
profiles:
  Buds3:
    object_name: Buds3
    pick_profile: Buds3
    frame_id: base_link
    reference_point_base:
      x: -0.31
      y: 0.064
      z: 0.105
    bearing_tolerance_deg: 2.0
    range_tolerance_m: 0.015
    height_tolerance_m: 0.030
    max_turn_step_deg: 8.0
    max_move_step_m: 0.040
```

`z` 차이는 평면 차체 이동으로 보정할 수 없으므로, height 오차가 크면 정렬을 중단한다.

---

## 4. 전체 stack 실행

최신 safe-region CSV:

```bash
export SAFE_CSV="$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv"
```

실제 로봇:

```bash
ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  start_base_alignment:=true \
  alignment_dry_run:=false \
  perception_input_mode:=legacy \
  start_camera_teach:=false
```

팀 detector가 typed `TemporalConfirmationResult`만 발행하면:

```bash
perception_input_mode:=typed
```

주의:

- 정렬·pick 중에는 `macrobot_teleop`을 동시에 실행하지 않는다.
- `base_alignment_node`와 arm servo bridge가 같은 Pico serial bridge를 사용하지만, 정렬 단계와 arm 단계는 상태 머신으로 순차 실행한다.
- arm은 차체 이동 전에 `[0, 0, 0]`으로 stow된다.

---

## 5. 잡을 수 있는 위치 기록

### CLI

```bash
ros2 run macrobot_pick_pipeline base_alignment_cli
```

메뉴 `2`를 선택한다.

1. 물체를 실제로 잡을 수 있는 위치에 로봇을 수동 배치한다.
2. 물체가 카메라에 안정적으로 보이게 한다.
3. `RECORD`를 입력한다.
4. 최근 안정된 `point_base` median이 저장된다.

### Topic 직접 사용

```bash
ros2 topic pub --once \
  /macrobot/base_alignment/record \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"alignment_profile\":\"Buds3\",\"pick_profile\":\"Buds3\"}'}"
```

결과:

```bash
ros2 topic echo --full-length --field data \
  /macrobot/base_alignment/result
```

---

## 6. 정렬만 실행

```bash
ros2 topic pub --once \
  /macrobot/align_pick/goal \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"alignment_profile\":\"Buds3\",\"pick_profile\":\"Buds3\",\"execute_pick\":false}'}"
```

상태:

```bash
ros2 topic echo --full-length --field data \
  /macrobot/base_alignment/status
```

Pico에 보내려는 명령:

```bash
ros2 topic echo /macrobot/base_alignment/command_preview
```

---

## 7. 정렬 후 잡기

```bash
ros2 topic pub --once \
  /macrobot/align_pick/goal \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"alignment_profile\":\"Buds3\",\"pick_profile\":\"Buds3\",\"execute_pick\":true}'}"
```

흐름:

```text
arm stow
→ finder continuous tracking
→ bearing correction
→ range correction
→ 2회 연속 정렬 확인
→ /macrobot/pick/goal hand-off
→ OPEN / PRE_GRASP / APPROACH / CLOSE / LIFT
```

최종 결과:

```bash
ros2 topic echo --full-length --field data \
  /macrobot/base_alignment/result
```

---

## 8. Dry-run

차체 명령을 실제 Pico로 보내지 않고 계산만 확인한다.

```bash
ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=false \
  start_base_alignment:=true \
  alignment_dry_run:=true \
  perception_input_mode:=legacy
```

`command_preview`와 status를 확인한다.

---

## 9. 취소

```bash
ros2 topic pub --once \
  /macrobot/base_alignment/cancel \
  std_msgs/msg/String \
  "{data: 'user_cancel'}"
```

실제 모드에서는 Pico에 `STOP`을 보내고 arm/pick도 취소한다.

---

## 10. 주요 실패 원인

| reason | 의미 |
|---|---|
| `alignment_search_timeout` | 안정된 물체 위치를 얻지 못함 |
| `height_error_not_correctable_by_planar_base` | 물체 높이가 기록 상태와 너무 다름 |
| `object_not_in_front_half_plane` | 좌표 convention상 물체가 차체 뒤쪽 |
| `alignment_total_turn_limit` | 누적 회전 안전 한계 초과 |
| `alignment_total_move_limit` | 누적 이동 안전 한계 초과 |
| `base_motion_failed` | Pico motion이 timeout/stall/stop/estop |
| `alignment_stow_rejected` | arm stow 자세가 validator에서 거부됨 |
| `pick_after_alignment_failed` | 정렬 후 기존 pick pipeline 실패 |

---

## 11. 튜닝 순서

처음에는 다음을 보수적으로 유지한다.

```yaml
default_max_turn_step_deg: 5~8
default_max_move_step_m: 0.02~0.04
default_bearing_tolerance_deg: 2
default_range_tolerance_m: 0.015
default_stability_count: 5
```

실제 차체의 `TICKS_PER_CM`, `TICKS_PER_DEG`, motor 방향이 먼저 보정되어 있어야 한다.
