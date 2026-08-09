#!/usr/bin/env bash
set -euo pipefail

OBJECT_NAME="${1:-Buds3}"
EXECUTE="${2:-true}"

source /opt/ros/jazzy/setup.bash
if [[ -f "$HOME/MacRobot/install/setup.bash" ]]; then
  source "$HOME/MacRobot/install/setup.bash"
fi

ros2 topic pub --once \
  /macrobot/pick/goal \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"${OBJECT_NAME}\",\"profile\":\"${OBJECT_NAME}\",\"execute\":${EXECUTE}}'}"
