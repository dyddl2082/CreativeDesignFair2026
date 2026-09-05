#!/usr/bin/env bash
# Start exactly one authoritative Pi MacRobot URDF publisher and the localizer.
# This mode does not start Pico, chassis motion, arm motion, or stored tasks.
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/macrobot_demo_env.sh"
WAIT_TF="$SCRIPT_DIR/wait_for_macrobot_tf.py"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: environment helper not found: $ENV_FILE" >&2
  exit 2
fi
if [[ ! -f "$WAIT_TF" ]]; then
  echo "ERROR: TF wait helper not found: $WAIT_TF" >&2
  exit 2
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

fresh_nodes() {
  ros2 node list --no-daemon --spin-time 5.0 2>/dev/null || true
}

if fresh_nodes | grep -Fxq '/macrobot_detection_localizer'; then
  echo "ERROR: /macrobot_detection_localizer is already running" >&2
  exit 3
fi

mapfile -t LOCAL_RSP_LINES < <(
  pgrep -af '/robot_state_publisher/robot_state_publisher([[:space:]]|$)' \
    2>/dev/null || true
)

if (( ${#LOCAL_RSP_LINES[@]} > 0 )); then
  echo "ERROR: a local robot_state_publisher is already running." >&2
  echo "Stop its parent launch before starting localization-only mode:" >&2
  printf '  %s\n' "${LOCAL_RSP_LINES[@]}" >&2
  echo >&2
  echo "Typical conflicting launches:" >&2
  echo "  runtime_description.launch.py" >&2
  echo "  display_full.launch.py" >&2
  echo "  arm_pipeline.launch.py" >&2
  echo "  pick_pipeline_robot.launch.py" >&2
  exit 4
fi

DESCRIPTION_PID=""
cleanup() {
  if [[ -n "$DESCRIPTION_PID" ]]; then
    kill -INT "$DESCRIPTION_PID" 2>/dev/null || true
    wait "$DESCRIPTION_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "[localization-only] starting authoritative r4 MacRobot TF publisher"
ros2 launch macrobot_description runtime_description.launch.py \
  rsp_node_name:=macrobot_pi_robot_state_publisher &
DESCRIPTION_PID=$!

if ! python3 "$WAIT_TF" \
  base_link camera_link \
  --timeout 25 \
  --expect-x -0.030650 \
  --expect-y 0.060623 \
  --expect-z 0.025820 \
  --translation-tolerance 0.002; then
  echo >&2
  echo "The authoritative RSP started, but the r4 camera anchor was not received." >&2
  echo "Check its process log above and inspect the active Xacro:" >&2
  echo '  xacro "$(ros2 pkg prefix --share macrobot_description)/urdf/macrobot_full_visual.urdf.xacro" > /tmp/macrobot_active.urdf' >&2
  echo '  grep -n -A5 -B2 camera_fix_joint /tmp/macrobot_active.urdf' >&2
  exit 5
fi

if ! python3 "$WAIT_TF" \
  base_link camera_color_optical_frame \
  --timeout 25; then
  echo "ERROR: base_link -> camera_link is correct, but the camera internal TF tree is disconnected." >&2
  echo "Keep the RSP running and inspect macrobot_rgb_anchor_tf_publisher/calibration YAML." >&2
  exit 6
fi

mapfile -t GRAPH_RSP < <(
  fresh_nodes | grep -E '/.*robot_state_publisher.*$' | sort || true
)
if (( ${#GRAPH_RSP[@]} > 1 )); then
  echo "WARNING: more than one robot_state_publisher is visible in the ROS graph:" >&2
  printf '  %s\n' "${GRAPH_RSP[@]}" >&2
  echo "Stop RSP-containing launches on WSL2 or other hosts before real robot motion." >&2
fi

CONFIG_FILE="$(ros2 pkg prefix --share macrobot_pick_pipeline)/config/perception.yaml"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "ERROR: localizer parameter file not found: $CONFIG_FILE" >&2
  exit 7
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
