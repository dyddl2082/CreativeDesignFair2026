#!/usr/bin/env bash
set -euo pipefail
PROFILE="${1:?usage: record_semantic_grasp.sh <profile> [object]}"
OBJECT="${2:-$PROFILE}"
cat <<EOF
Use arm_demo_cli jog-only mode to place the arm, then run each command when ready:

ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture '$PROFILE' '$OBJECT' OPEN
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture '$PROFILE' '$OBJECT' PRE_GRASP
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture '$PROFILE' '$OBJECT' GRASP_OPEN
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture '$PROFILE' '$OBJECT' CLOSE
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture '$PROFILE' '$OBJECT' LIFT
ros2 run macrobot_pick_pipeline grasp_keyframe_cli finalize '$PROFILE'
ros2 run macrobot_pick_pipeline grasp_keyframe_cli preflight '$PROFILE' --object-name '$OBJECT'
EOF
