#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

ros2 topic pub --once /macrobot/stored_pick/cancel std_msgs/msg/String \
  "{data: 'operator_cancel'}" 2>/dev/null || true
ros2 topic pub --once /object_finder/cancel std_msgs/msg/String \
  "{data: 'operator_cancel'}" 2>/dev/null || true
ros2 topic pub --once /macrobot/arm/stop std_msgs/msg/Empty '{}' 2>/dev/null || true

echo "Cancel/stop requests sent. Servo torque remains enabled to hold the current arm pose."
echo "To release servo torque, support the arm first and run:"
echo "  ros2 topic pub --once /macrobot/arm/disable_servos std_msgs/msg/Empty '{}'"
