#!/usr/bin/env bash
set -eo pipefail

ENV_FILE="$HOME/MacRobot/tools/demo/macrobot_demo_env.sh"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
else
  set +u
  source /opt/ros/jazzy/setup.bash
  source "$HOME/MacRobot/install/setup.bash"
fi

echo '== Fresh ROS graph (no daemon) =='
NODES="$(ros2 node list --no-daemon --spin-time 5.0 2>&1 || true)"
printf '%s\n' "$NODES" | grep -E 'robot_state_publisher|serial2r_state' || true

echo
echo '== Duplicate counts =='
printf '%s\n' "$NODES" \
  | grep -E '^/.*(robot_state_publisher|serial2r_state).*$' \
  | sort | uniq -c || true

echo
echo '== Local processes and launch parents =='
pgrep -af 'robot_state_publisher|runtime_description.launch.py|display_(full|kinematic|collision)|arm_pipeline.launch.py|pick_pipeline_robot.launch.py|04_pi_localization_only' || true

echo
echo '== /tf_static publisher endpoints =='
ros2 topic info /tf_static -v 2>/dev/null \
  | grep -E 'Node name:|Node namespace:|Endpoint type:|GID:' || true

echo
echo '== base_link -> camera_link =='
timeout 6s ros2 run tf2_ros tf2_echo base_link camera_link 2>&1 || true
