#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

ACTION="${1:-help}"
OBJECT_NAME="${2:-Eraser}"
REFERENCE_OBJECT="${3:-Cup}"
PROFILE_NAME="${4:-$OBJECT_NAME}"
KEYFRAME_PROFILE="${5:-${OBJECT_NAME}_r4}"

usage() {
  cat <<'EOF'
Usage:
  09_demo_action.sh memory
  09_demo_action.sh clear-held
  09_demo_action.sh localize [OBJECT]
  09_demo_action.sh visible-align [OBJECT] [unused] [PROFILE]
  09_demo_action.sh find-align [OBJECT] [unused] [PROFILE]
  09_demo_action.sh pick [OBJECT] [unused] [PROFILE]
  09_demo_action.sh place [HELD_OBJECT] [REFERENCE_OBJECT] [PROFILE] [KEYFRAME_PROFILE]
  09_demo_action.sh cancel
  09_demo_action.sh stop-arm
  09_demo_action.sh arm-off

Examples:
  09_demo_action.sh localize Eraser
  09_demo_action.sh visible-align Eraser
  09_demo_action.sh find-align Eraser
  09_demo_action.sh pick Eraser
  09_demo_action.sh place Eraser Cup Eraser Eraser_r4
EOF
}

case "$ACTION" in
  memory)
    exec ros2 run macrobot_pick_pipeline stored_object_pick_cli memory
    ;;
  clear-held)
    exec ros2 run macrobot_pick_pipeline stored_object_pick_cli clear-held
    ;;
  localize)
    exec "$SCRIPT_DIR/06_localization_goal.sh" "$OBJECT_NAME" 60
    ;;
  visible-align)
    exec ros2 run macrobot_pick_pipeline stored_object_pick_cli \
      visible-test "$OBJECT_NAME" \
      --profile "$PROFILE_NAME" \
      --align-only \
      --timeout 180
    ;;
  find-align)
    exec ros2 run macrobot_pick_pipeline stored_object_pick_cli \
      run "$OBJECT_NAME" \
      --profile "$PROFILE_NAME" \
      --align-only \
      --timeout 180
    ;;
  pick)
    exec ros2 run macrobot_pick_pipeline stored_object_pick_cli \
      run "$OBJECT_NAME" \
      --profile "$PROFILE_NAME" \
      --timeout 240
    ;;
  place)
    exec ros2 run macrobot_pick_pipeline stored_object_pick_cli \
      place "$REFERENCE_OBJECT" \
      --held-object "$OBJECT_NAME" \
      --held-runtime-profile "$PROFILE_NAME" \
      --grasp-keyframes "$KEYFRAME_PROFILE" \
      --offset-base 0.0 0.12 0.0 \
      --timeout 180
    ;;
  cancel)
    exec "$SCRIPT_DIR/07_cancel_all.sh"
    ;;
  stop-arm)
    exec ros2 topic pub --once /macrobot/arm/stop std_msgs/msg/Empty '{}'
    ;;
  arm-off)
    echo "WARNING: support the arm before disabling servo torque." >&2
    exec ros2 topic pub --once /macrobot/arm/disable_servos std_msgs/msg/Empty '{}'
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "ERROR: unknown action: $ACTION" >&2
    usage >&2
    exit 2
    ;;
esac
