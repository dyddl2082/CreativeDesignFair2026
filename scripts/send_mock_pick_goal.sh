#!/usr/bin/env bash
set -euo pipefail

OBJECT_NAME="${1:-Buds3}"
PROFILE_NAME="${2:-$OBJECT_NAME}"

ros2 topic pub --once \
  /macrobot/pick/goal \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"${OBJECT_NAME}\",\"profile\":\"${PROFILE_NAME}\",\"execute\":true}'}"
