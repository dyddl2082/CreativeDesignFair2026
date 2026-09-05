#!/usr/bin/env bash
# Start only the URDF/TF tree and detection localizer on the Raspberry Pi.
# No Pico, base motion, arm motion, or stored-task node is started.

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

if ros2 node list 2>/dev/null | grep -Fxq /macrobot_detection_localizer; then
  echo "ERROR: /macrobot_detection_localizer is already running" >&2
  exit 2
fi

DESCRIPTION_PID=""
cleanup() {
  if [[ -n "$DESCRIPTION_PID" ]]; then
    kill "$DESCRIPTION_PID" 2>/dev/null || true
    wait "$DESCRIPTION_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if timeout 2s ros2 run tf2_ros tf2_echo base_link camera_link 2>&1 | grep -q 'Translation:'; then
  echo "[localization-only] existing base_link -> camera_link TF found"
else
  echo "[localization-only] starting robot description / robot_state_publisher"
  ros2 launch macrobot_description runtime_description.launch.py &
  DESCRIPTION_PID=$!
  sleep 3
fi

if ! timeout 4s ros2 run tf2_ros tf2_echo base_link camera_link 2>&1 | grep -q 'Translation:'; then
  echo "ERROR: base_link -> camera_link TF is still unavailable" >&2
  exit 2
fi

CONFIG_FILE="$(ros2 pkg prefix --share macrobot_pick_pipeline)/config/perception.yaml"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "ERROR: localizer parameter file not found: $CONFIG_FILE" >&2
  exit 2
fi

echo "[localization-only] starting detection_localizer_node"
echo "[localization-only] config: $CONFIG_FILE"
echo "This mode cannot move the chassis or arm."

set +e
ros2 run macrobot_pick_pipeline detection_localizer_node \
  --ros-args \
  --params-file "$CONFIG_FILE"
status=$?
set -e
exit "$status"
