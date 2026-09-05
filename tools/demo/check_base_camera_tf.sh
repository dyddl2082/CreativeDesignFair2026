#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1090
source "$SCRIPT_DIR/macrobot_demo_env.sh"

echo "== Local robot_state_publisher processes =="
pgrep -af '/robot_state_publisher/robot_state_publisher([[:space:]]|$)' \
  || echo "none"

echo
echo "== Fresh ROS graph =="
ros2 node list --no-daemon --spin-time 5.0 \
  | grep -E 'robot_state_publisher|rgb_anchor|detection_localizer' \
  | sort || true

echo
echo "== Duplicate node-name counts =="
ros2 node list --no-daemon --spin-time 5.0 \
  | grep -E 'robot_state_publisher|rgb_anchor|detection_localizer' \
  | sort | uniq -c || true

echo
echo "== r4 camera anchor TF =="
python3 "$SCRIPT_DIR/wait_for_macrobot_tf.py" \
  base_link camera_link \
  --timeout 15 \
  --expect-x -0.030650 \
  --expect-y 0.060623 \
  --expect-z 0.025820 \
  --translation-tolerance 0.002

echo
echo "== Complete optical TF =="
python3 "$SCRIPT_DIR/wait_for_macrobot_tf.py" \
  base_link camera_color_optical_frame \
  --timeout 15
