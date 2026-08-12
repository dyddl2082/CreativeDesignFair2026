#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-Buds3}"
TIMEOUT="${2:-60}"
ros2 topic pub --once /object_finder/goal std_msgs/msg/String \
  "{data: '{\"object_name\":\"${TARGET}\",\"timeout_sec\":${TIMEOUT},\"continuous\":true}'}"
