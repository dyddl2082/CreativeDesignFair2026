#!/usr/bin/env bash
# MacRobot ROS 2 공통 환경. 직접 실행하지 말고 각 실행 스크립트가 source한다.
# 수동 사용: source "$HOME/MacRobot/tools/demo/macrobot_demo_env.sh"

set +u

if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  echo "ERROR: /opt/ros/jazzy/setup.bash not found" >&2
  return 1 2>/dev/null || exit 1
fi

# shellcheck disable=SC1091
source /opt/ros/jazzy/setup.bash

if [[ ! -f "$HOME/MacRobot/install/setup.bash" ]]; then
  echo "ERROR: $HOME/MacRobot/install/setup.bash not found" >&2
  return 1 2>/dev/null || exit 1
fi

# shellcheck disable=SC1091
source "$HOME/MacRobot/install/setup.bash"

# Pi와 WSL2 양쪽에서 동일한 값을 사용한다.
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_LOCALHOST_ONLY 2>/dev/null || true
