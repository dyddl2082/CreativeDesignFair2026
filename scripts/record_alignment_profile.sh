#!/usr/bin/env bash
set -euo pipefail
OBJECT_NAME="${1:-Buds3}"
ALIGNMENT_PROFILE="${2:-$OBJECT_NAME}"
PICK_PROFILE="${3:-$OBJECT_NAME}"
PAYLOAD=$(printf '{"object_name":"%s","alignment_profile":"%s","pick_profile":"%s"}' \
  "$OBJECT_NAME" "$ALIGNMENT_PROFILE" "$PICK_PROFILE")
ros2 topic pub --once /macrobot/base_alignment/record std_msgs/msg/String \
  "{data: '$PAYLOAD'}"
