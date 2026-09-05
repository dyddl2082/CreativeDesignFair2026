#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

CALIBRATION_FILE="$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml"

if [[ ! -s "$CALIBRATION_FILE" ]]; then
  echo "ERROR: camera calibration file missing or empty:" >&2
  echo "  $CALIBRATION_FILE" >&2
  echo "Run the RGB-anchor capture procedure before the demo." >&2
  exit 2
fi

if ! ros2 pkg prefix macrobot_camera_tf >/dev/null 2>&1; then
  echo "ERROR: macrobot_camera_tf package not found" >&2
  exit 2
fi

echo "[Pi camera] calibration: $CALIBRATION_FILE"
echo "Do not start another realsense2_camera node at the same time."

exec ros2 launch macrobot_camera_tf camera_rgb_anchor.launch.py \
  calibration_file:="$CALIBRATION_FILE" \
  start_realsense:=true \
  initial_reset:=false \
  color_profile:=640x480x15 \
  depth_profile:=640x480x15
