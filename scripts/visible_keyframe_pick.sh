#!/usr/bin/env bash
set -euo pipefail
OBJECT="${1:?usage: visible_keyframe_pick.sh <object> [profile]}"
PROFILE="${2:-$OBJECT}"
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test "$OBJECT" --profile "$PROFILE"
