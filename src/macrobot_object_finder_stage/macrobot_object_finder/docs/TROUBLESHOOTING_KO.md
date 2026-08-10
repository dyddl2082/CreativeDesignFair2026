# 문제 해결

## `/object_finder/result` publisher가 두 개

```bash
ros2 topic info /object_finder/result -v
```

정상은 `macrobot_object_finder` 하나다. 기존 `macrobot_perception pc_recognition_pipeline.launch.py`를 별도로 실행하면 temporal node의 legacy publisher와 중복될 수 있다. 이 패키지의 `object_finder_wsl.launch.py`만 사용한다.

## `positive_bank_unavailable`

```bash
find ~/MacRobot/data/curated/objects/Buds3 -type f
```

Pi에서 촬영한 전체 data tree를 WSL로 `rsync -a`로 복사한다.

## health의 `camera_info` 또는 `candidate_stream_seen_by_temporal`이 false

Pi와 WSL의 ROS domain, RMW, subnet discovery 설정을 맞춘다. Finder는 후보 heartbeat를 직접 한 번 더 구독하지 않고 temporal status의 `received_heartbeats`를 사용하므로 추가 대역폭을 만들지 않는다.

```bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_LOCALHOST_ONLY
```

## full image가 WSL로 전송되는 것 같음

WSL에서 Image, PointCloud2, `image_view`, `rqt_image_view`, camera RViz display를 종료한다. 이 detector launch는 full image를 구독하지 않는다.
