#!/usr/bin/env bash
set -euo pipefail
OBJECT_NAME="${1:-Buds3}"
ALIGNMENT_PROFILE="${2:-$OBJECT_NAME}"
PICK_PROFILE="${3:-$OBJECT_NAME}"
PAYLOAD=$(printf '{"object_name":"%s","alignment_profile":"%s","pick_profile":"%s","execute_pick":false}' \
  "$OBJECT_NAME" "$ALIGNMENT_PROFILE" "$PICK_PROFILE")
ros2 topic pub --once /macrobot/align_pick/goal std_msgs/msg/String \
  "{data: '$PAYLOAD'}"
