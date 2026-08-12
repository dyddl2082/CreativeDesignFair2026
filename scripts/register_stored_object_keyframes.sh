#!/usr/bin/env bash
set -euo pipefail
OBJECT="${1:?usage: register_stored_object_keyframes.sh <object> [stored_profile] [keyframe_profile]}"
PROFILE="${2:-$OBJECT}"
KEYFRAMES="${3:-$OBJECT}"
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record "$OBJECT" \
  --profile "$PROFILE" \
  --grasp-keyframes "$KEYFRAMES"
