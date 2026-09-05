#!/usr/bin/env bash
# Start one authoritative robot_state_publisher and the detection localizer.
# Prevents the startup/discovery race that could create a second publisher.
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$HOME/MacRobot/tools/demo/macrobot_demo_env.sh"

if [[ -f "$SCRIPT_DIR/macrobot_demo_env.sh" ]]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/macrobot_demo_env.sh"
elif [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
else
  echo "ERROR: macrobot_demo_env.sh not found" >&2
  exit 2
fi

DESCRIPTION_PID=""
cleanup() {
  if [[ -n "$DESCRIPTION_PID" ]]; then
    kill -TERM "$DESCRIPTION_PID" 2>/dev/null || true
    wait "$DESCRIPTION_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

fresh_nodes() {
  ros2 node list --no-daemon --spin-time 3.0 2>/dev/null || true
}

local_rsp_pids() {
  pgrep -f '/robot_state_publisher/robot_state_publisher([[:space:]]|$)' 2>/dev/null || true
}

tf_ready() {
  timeout 2s ros2 run tf2_ros tf2_echo base_link camera_link 2>&1 \
    | grep -q 'Translation:'
}

if fresh_nodes | grep -Fxq '/macrobot_detection_localizer'; then
  echo "ERROR: /macrobot_detection_localizer is already running" >&2
  exit 2
fi

mapfile -t RSP_PIDS < <(local_rsp_pids)
if (( ${#RSP_PIDS[@]} > 1 )); then
  echo "ERROR: multiple local robot_state_publisher processes already exist:" >&2
  ps -o pid,ppid,etimes,args -p "$(IFS=,; echo "${RSP_PIDS[*]}")" >&2 || true
  echo "Stop the duplicate launch processes before continuing." >&2
  exit 3
fi

if (( ${#RSP_PIDS[@]} == 1 )); then
  echo "[localization-only] existing local robot_state_publisher PID=${RSP_PIDS[0]}"
else
  GRAPH_COUNT="$(fresh_nodes | grep -Ec '(^|/)robot_state_publisher$' || true)"
  if (( GRAPH_COUNT > 1 )); then
    echo "ERROR: multiple robot_state_publisher nodes are visible in the ROS graph." >&2
    fresh_nodes | grep -E 'robot_state_publisher|serial2r_state' >&2 || true
    exit 3
  elif (( GRAPH_COUNT == 1 )); then
    echo "[localization-only] using the robot_state_publisher already visible in the ROS graph"
  else
    echo "[localization-only] starting robot description / robot_state_publisher"
    ros2 launch macrobot_description runtime_description.launch.py &
    DESCRIPTION_PID=$!
  fi
fi

# Give process startup plus DDS discovery enough time. Never start another
# publisher merely because the first TF lookup was early.
TF_OK=0
for attempt in $(seq 1 15); do
  if tf_ready; then
    TF_OK=1
    echo "[localization-only] base_link -> camera_link ready (attempt ${attempt}/15)"
    break
  fi
  echo "[localization-only] waiting for TF discovery (${attempt}/15)"
  sleep 1
done

if (( TF_OK == 0 )); then
  echo "ERROR: base_link -> camera_link remained unavailable after the readiness wait" >&2
  echo "Visible related nodes:" >&2
  fresh_nodes | grep -E 'robot_state_publisher|serial2r_state' >&2 || true
  echo "Local processes:" >&2
  pgrep -af 'robot_state_publisher|runtime_description.launch.py|arm_pipeline.launch.py|pick_pipeline_robot.launch.py' >&2 || true
  exit 4
fi

mapfile -t RSP_PIDS < <(local_rsp_pids)
if (( ${#RSP_PIDS[@]} > 1 )); then
  echo "ERROR: duplicate robot_state_publisher processes appeared during startup" >&2
  ps -o pid,ppid,etimes,args -p "$(IFS=,; echo "${RSP_PIDS[*]}")" >&2 || true
  exit 3
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
