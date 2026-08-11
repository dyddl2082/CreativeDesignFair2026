# MacRobot D435 촬영·크롭·공용 Negative 라이브러리 v2

## 왜 이 구조인가

물체마다 Cup, Mouse, Charger 같은 negative를 다시 촬영해 아래처럼 복제하는 방식은 사용자에게 부담이 큽니다.

```text
negative/confusers/Buds3/Cup/...
negative/confusers/Mouse/Cup/...
negative/confusers/Charger/Cup/...
```

v2에서는 **원본 이미지를 한 번만 저장**합니다.

```text
등록 가능한 물체:
curated/objects/Cup/

목표로 등록하지 않을 공용 방해물:
negative/library/white_cup/

공통 배경:
negative/backgrounds/desk/
```

그 뒤 `d435_capture_crop`가 각 목표의 기존 negative 경로에 상대 심볼릭 링크를 자동 생성합니다.

```text
negative/confusers/Buds3/_auto/
├── registered/
│   ├── Cup/       -> curated/objects/Cup의 view들
│   └── Mouse/     -> curated/objects/Mouse의 view들
└── library/
    ├── white_cup/ -> negative/library/white_cup의 view들
    └── cable/     -> negative/library/cable의 view들
```

따라서 기존 `embedding_retrieval` 설정은 그대로 사용할 수 있습니다.

```yaml
negative_roots:
  - ~/MacRobot/data/negative/confusers/{target}
  - ~/MacRobot/data/negative/backgrounds
```

`discover_images()`가 `_auto` 아래 링크를 재귀적으로 읽기 때문입니다.

## 네 가지 저장 목적

### 1. 등록 물체 (`positive`)

목표 물체의 multi-view positive입니다.

```text
curated/objects/<물체명>/
```

이 이미지는 해당 물체의 positive bank가 되며, **다른 모든 등록 물체의 negative로 자동 연결**됩니다.

예를 들어 Cup을 나중에 찾을 가능성이 있다면 Cup을 공용 negative로 따로 촬영하지 말고 `등록 물체`로 한 번 등록하는 편이 좋습니다.

### 2. 공용 방해물 (`shared_negative`)

목표로 등록할 필요는 없지만 오검출을 일으키는 물체입니다.

```text
negative/library/<방해물명>/
```

한 번 저장하면 모든 등록 목표에 연결됩니다.

예:

```text
white_cup
charger_case
plastic_box
```

### 3. 배경·환경 (`background`)

모든 목표가 공유하는 배경 bank입니다.

```text
negative/backgrounds/<장면명>/
```

예:

```text
empty_desk
hand
cable
shadow
robot_body
```

기존 embedding 노드가 이 경로를 직접 읽으므로 `_auto` 링크가 필요하지 않습니다.

### 4. 목표 전용 hard negative (`hard_negative`)

공용 negative와 negative margin을 적용한 뒤에도 특정 목표에서만 오검출이 반복될 때 사용합니다.

```text
negative/confusers/<목표>/manual/<방해물>/
```

이 모드는 예외 처리용입니다. 평소에는 등록 물체 또는 공용 방해물을 사용하세요.

---

## 설치

압축을 푼 뒤 Raspberry Pi에서:

```bash
rm -rf ~/MacRobot/src/d435_capture_crop

cp -a \
  macrobot_d435_capture_negative_library_v2/d435_capture_crop \
  ~/MacRobot/src/
```

빌드:

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rm -rf \
  build/d435_capture_crop \
  install/d435_capture_crop

colcon build \
  --symlink-install \
  --packages-select d435_capture_crop

source ~/MacRobot/install/setup.bash
```

이번 버전은 `--symlink-install`에서도 웹 정적 파일이 정상 열리도록 경로 검사를 수정했습니다.

## 실행

D435:

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  pointcloud.enable:=false \
  align_depth.enable:=true \
  enable_sync:=true \
  rgb_camera.color_profile:=640x480x30 \
  depth_module.depth_profile:=640x480x30 \
  rgb_camera.color_format:=RGB8 \
  depth_module.depth_format:=Z16
```

촬영 노드:

```bash
ros2 launch d435_capture_crop d435_capture_crop.launch.py
```

Windows 브라우저:

```text
http://<PI_IP>:8090
```

## 브라우저 사용법

1. 저장 목적을 선택합니다.
2. 이름과 view 라벨을 입력합니다.
3. `현재 프레임 촬영`을 누릅니다.
4. 저장 영역을 드래그합니다.
5. Depth 통계를 확인합니다.
6. 역할에 맞는 저장 버튼을 누릅니다.

positive 또는 shared negative를 저장하면 자동 negative 연결이 즉시 갱신됩니다.

수동으로 다시 갱신하려면 상단의 `Negative 연결 새로고침` 버튼을 누릅니다.

## 생성되는 폴더

```text
~/MacRobot/data/
├── objects/
│   └── Buds3/
├── curated/
│   ├── objects/
│   │   ├── Buds3/
│   │   └── Cup/
│   ├── depth/
│   └── metadata/
└── negative/
    ├── library/
    │   └── white_charger/
    ├── backgrounds/
    │   └── empty_desk/
    ├── confusers/
    │   ├── Buds3/
    │   │   ├── _auto/       # 자동 생성, 직접 편집 금지
    │   │   └── manual/      # 사용자 hard negative
    │   └── Cup/
    │       └── _auto/
    ├── originals/
    ├── depth/
    └── metadata/
```

`negative/confusers/<target>/_auto`만 자동 재생성됩니다. `manual` 및 `_auto` 바깥의 기존 파일은 삭제하지 않습니다.

## WSL2로 데이터 복사

자동 negative는 상대 심볼릭 링크이므로 `rsync -a`로 링크를 보존하고, 같은 `data` 구조를 유지해야 합니다.

가장 단순한 방법:

```bash
rsync -av \
  <PI_USER>@<PI_IP>:~/MacRobot/data/ \
  ~/MacRobot/data/
```

일부만 복사한다면 최소한 다음 두 트리는 함께 복사합니다.

```text
curated/objects/
negative/
```

복사 후 WSL2에서 embedding bank를 다시 읽습니다.

```bash
ros2 service call \
  /embedding_retrieval/reload_banks \
  std_srvs/srv/Trigger \
  "{}"
```

이미지나 링크 상태를 완전히 다시 계산하려면:

```bash
ros2 service call \
  /embedding_retrieval/rebuild_banks \
  std_srvs/srv/Trigger \
  "{}"
```

## CLI 촬영

기존 plain string은 positive 촬영으로 유지됩니다.

```bash
ros2 topic pub --once \
  /capture_object_name \
  std_msgs/msg/String \
  "{data: 'Buds3'}"
```

공용 방해물:

```bash
ros2 topic pub --once \
  /capture_object_name \
  std_msgs/msg/String \
  "{data: '{\"dataset_role\":\"shared_negative\",\"object_name\":\"white_cup\",\"view_label\":\"left\"}'}"
```

배경:

```bash
ros2 topic pub --once \
  /capture_object_name \
  std_msgs/msg/String \
  "{data: '{\"dataset_role\":\"background\",\"object_name\":\"empty_desk\",\"view_label\":\"front\"}'}"
```

목표 전용:

```bash
ros2 topic pub --once \
  /capture_object_name \
  std_msgs/msg/String \
  "{data: '{\"dataset_role\":\"hard_negative\",\"object_name\":\"white_cup\",\"target_object\":\"Buds3\",\"view_label\":\"close\"}'}"
```

CLI 명령은 프레임만 고정합니다. 최종 크롭과 저장은 웹 UI에서 완료합니다.

## 운영 권장 순서

```text
1. 찾을 가능성이 있는 물체는 각각 positive로 등록
2. 찾지는 않지만 자주 혼동되는 물체는 shared negative로 한 번 저장
3. 빈 배경·손·케이블은 background로 저장
4. 특정 목표에서만 오검출이 남을 때 hard negative 사용
```

이 규칙을 따르면 물체 수가 늘어나도 negative를 목표마다 반복 촬영할 필요가 없습니다.
