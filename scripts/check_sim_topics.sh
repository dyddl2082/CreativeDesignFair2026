#!/usr/bin/env bash
set -euo pipefail

source /opt/ros/jazzy/setup.bash
if [[ -f "$HOME/MacRobot/install/setup.bash" ]]; then
  source "$HOME/MacRobot/install/setup.bash"
fi

printf '\n== Gazebo / ROS bridge topics ==\n'
ros2 topic list | grep -E '^/(clock|sim/camera|sim/gz)' || true

printf '\n== MacRobot pick topics ==\n'
ros2 topic list | grep -E '^/(macrobot/pick|macrobot/perception|object_finder)' || true

printf '\n== Robot model / TF topics ==\n'
ros2 topic list | grep -E '^/(robot_description|joint_states|tf|tf_static)$' || true

printf '\n== One health message ==\n'
timeout 4 ros2 topic echo /macrobot/sim/health --once || true
