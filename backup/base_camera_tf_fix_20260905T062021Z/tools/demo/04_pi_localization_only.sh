#!/usr/bin/env bash
# Start only the URDF/TF tree and detection localizer on the Raspberry Pi.
# No Pico, base motion, arm motion, or stored-task node is started.

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

if ros2 node list 2>/dev/null | grep -Eq '/.*macrobot_detection_localizer.*$'; then
  echo "ERROR: a detection-localizer node is already running" >&2
  ros2 node list 2>/dev/null | grep -E '/.*macrobot_detection_localizer.*$' >&2 || true
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

transform_ready() {
  local output
  output="$(timeout --signal=INT --kill-after=1s 2s \
    ros2 run tf2_ros tf2_echo base_link camera_link 2>&1 || true)"
  printf '%s' "$output" | grep -q 'Translation:'
}

if transform_ready; then
  echo "[localization-only] existing base_link -> camera_link TF found"
else
  if ros2 node list 2>/dev/null | grep -Eq '/.*robot_state_publisher.*$'; then
    echo "[localization-only] robot_state_publisher exists; waiting for its TF tree"
  else
    echo "[localization-only] starting robot description / robot_state_publisher"
    ros2 launch macrobot_description runtime_description.launch.py &
    DESCRIPTION_PID=$!
  fi

  ready=false
  for _ in $(seq 1 20); do
    if transform_ready; then
      ready=true
      break
    fi
    if [[ -n "$DESCRIPTION_PID" ]] && ! kill -0 "$DESCRIPTION_PID" 2>/dev/null; then
      echo "ERROR: runtime_description.launch.py exited before TF became ready" >&2
      wait "$DESCRIPTION_PID" 2>/dev/null || true
      exit 2
    fi
    sleep 0.5
  done

  if [[ "$ready" != true ]]; then
    echo "ERROR: base_link -> camera_link TF is unavailable after waiting" >&2
    echo "Visible TF-related nodes:" >&2
    ros2 node list 2>/dev/null \
      | grep -E 'robot_state_publisher|camera|tf' \
      | sed 's/^/  /' >&2 || true
    exit 2
  fi
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
