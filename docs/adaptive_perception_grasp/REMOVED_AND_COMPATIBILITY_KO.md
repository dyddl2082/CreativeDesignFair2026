# 제거된 경로와 호환성

## active path에서 제거

```text
horizontal_error_norm
suggested_turn
image-center turn_left/turn_right control
candidate_refiner_node
edge_candidate_pipeline_cable_guard.launch.py
force-square high-recall crop hotfix
legacy embedding wrapper script
```

## 호환용 유지

```text
arm_demo trajectory executor
pick_coordinator profile executor
legacy /object_finder/result JSON
```

신규 stored-object profile의 기본은 `grasp.executor=keyframes`이다.

## custom interface 변경

Pi와 WSL2의 `macrobot_interfaces`를 반드시 함께 clean rebuild한다. 메시지 정의가 한 글자라도 다르면 DDS custom type 통신이 성립하지 않는다.

- `real_camera.rviz`에서도 `Image`, `PointCloud2`, `Camera`, `DepthCloud` display를 제거했다. RViz를 실행해도 WSL2가 전체 RGB/depth/point cloud subscriber가 되지 않고 RobotModel·TF·작은 marker만 구독한다.
