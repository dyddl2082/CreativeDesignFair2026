#!/usr/bin/env bash
# Source this file in each terminal: source ~/MacRobot/tools/macrobot_env.sh
set +u
source /opt/ros/jazzy/setup.bash
if [[ -f "$HOME/MacRobot/install/setup.bash" ]]; then
  source "$HOME/MacRobot/install/setup.bash"
fi
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-42}"
export ROS_AUTOMATIC_DISCOVERY_RANGE="${ROS_AUTOMATIC_DISCOVERY_RANGE:-SUBNET}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
unset ROS_LOCALHOST_ONLY || true
