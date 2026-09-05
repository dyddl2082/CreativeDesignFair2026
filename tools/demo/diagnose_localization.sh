#!/usr/bin/env bash
# Diagnose the MacRobot perception/localization chain from the Raspberry Pi.
# Usage:
#   diagnose_localization.sh
#   diagnose_localization.sh Eraser --send-goal

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OBJECT_NAME="Eraser"
SEND_GOAL=false

for arg in "$@"; do
  case "$arg" in
    --send-goal) SEND_GOAL=true ;;
    --help|-h)
      sed -n '1,8p' "$0"
      exit 0
      ;;
    *) OBJECT_NAME="$arg" ;;
  esac
done

# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

ok()   { printf 'OK    %s\n' "$*"; }
warn() { printf 'WARN  %s\n' "$*" >&2; }
fail() { printf 'FAIL  %s\n' "$*" >&2; }
section() { printf '\n========== %s ==========\n' "$*"; }

node_list() {
  ros2 node list 2>/dev/null || true
}

node_exists() {
  node_list | grep -Fxq "$1"
}

node_matches() {
  local pattern="$1"
  node_list | grep -Eq "$pattern"
}

show_nodes_matching() {
  local label="$1"
  local pattern="$2"
  local matches
  matches="$(node_list | grep -E "$pattern" || true)"
  if [[ -n "$matches" ]]; then
    ok "$label"
    printf '%s\n' "$matches" | sed 's/^/  /'
  else
    warn "$label not visible"
  fi
}

topic_counts() {
  local topic="$1"
  local output
  output="$(ros2 topic info "$topic" 2>&1 || true)"
  printf '%s\n' "$output" | sed 's/^/  /'
}

sample_field() {
  local label="$1"
  local topic="$2"
  local field="$3"
  local seconds="${4:-5}"
  local reliability="${5:-best_effort}"
  local output

  if output="$("$SCRIPT_DIR/ros2_wait_for_one.py" "$topic" \
      --field "$field" --timeout "$seconds" \
      --reliability "$reliability" 2>&1)"; then
    ok "$label"
    printf '%s\n' "$output" | sed 's/^/  /'
    return 0
  fi

  fail "$label: no valid sample within ${seconds}s"
  printf '%s\n' "$output" | sed 's/^/  /' >&2
  return 1
}

sample_string() {
  local label="$1"
  local topic="$2"
  local seconds="${3:-7}"
  local output

  if output="$("$SCRIPT_DIR/ros2_wait_for_one.py" "$topic" \
      --field data --timeout "$seconds" \
      --reliability best_effort 2>&1)"; then
    ok "$label"
    printf '%s\n' "$output" | sed 's/^/  /'
    return 0
  fi

  warn "$label: no valid sample within ${seconds}s"
  printf '%s\n' "$output" | sed 's/^/  /' >&2
  return 1
}

check_tf() {
  local parent="$1"
  local child="$2"
  local output=""
  local attempt

  for attempt in 1 2 3 4 5; do
    output="$(timeout --signal=INT --kill-after=1s 2s \
      ros2 run tf2_ros tf2_echo "$parent" "$child" 2>&1 || true)"
    if printf '%s' "$output" | grep -q 'Translation:'; then
      ok "TF $parent -> $child"
      printf '%s\n' "$output" \
        | grep -E 'Translation:|Rotation:' \
        | head -n 2 \
        | sed 's/^/  /'
      return 0
    fi
    sleep 0.5
  done

  fail "TF $parent -> $child unavailable"
  printf '%s\n' "$output" | tail -n 10 | sed 's/^/  /' >&2
  return 1
}

section "ROS environment"
printf 'HOME=%s\n' "$HOME"
printf 'ROS_DOMAIN_ID=%s\n' "${ROS_DOMAIN_ID:-unset}"
printf 'ROS_AUTOMATIC_DISCOVERY_RANGE=%s\n' "${ROS_AUTOMATIC_DISCOVERY_RANGE:-unset}"
printf 'RMW_IMPLEMENTATION=%s\n' "${RMW_IMPLEMENTATION:-unset}"
printf 'macrobot_pick_pipeline=%s\n' "$(ros2 pkg prefix macrobot_pick_pipeline 2>/dev/null || echo NOT_FOUND)"

section "Visible nodes"
show_nodes_matching "RealSense camera node" '/.*(camera|realsense).*$'
show_nodes_matching "Depth-candidate node" '/.*aligned_depth_candidate.*$'
show_nodes_matching "RGB-crop node" '/.*rgb_candidate_crop.*$'
show_nodes_matching "Candidate filter" '/.*candidate_filter.*$'
show_nodes_matching "Embedding retrieval" '/.*embedding_retrieval.*$'
show_nodes_matching "Temporal confirmation" '/.*temporal_confirmation.*$'
show_nodes_matching "Object finder" '/.*macrobot_object_finder.*$'
show_nodes_matching "Robot state publisher" '/.*robot_state_publisher.*$'
show_nodes_matching "Detection localizer" '/.*macrobot_detection_localizer.*$'

section "Localizer configuration"
if node_exists /macrobot_detection_localizer; then
  for parameter in \
    input_mode \
    finder_result_topic \
    camera_info_topic \
    aligned_depth_topic \
    base_frame \
    optical_frame_override \
    require_patch_localization \
    minimum_localization_quality \
    depth_sync_tolerance_sec \
    allow_candidate_depth_fallback
  do
    printf '%-36s ' "$parameter"
    ros2 param get /macrobot_detection_localizer "$parameter" 2>/dev/null || echo UNAVAILABLE
  done
else
  fail "localizer node is not running"
  cat >&2 <<MSG
  Localization-only start:
    $SCRIPT_DIR/04_pi_localization_only.sh
  Full robot-stack start:
    $SCRIPT_DIR/04_pi_robot_stack.sh dry /dev/ttyACM0
MSG
fi

section "TF publishers"
show_nodes_matching "Robot-state publisher" '/.*robot_state_publisher.*$'
show_nodes_matching "Camera-TF publisher" '/.*camera.*tf.*$'

section "Camera and TF"
sample_field "Color CameraInfo" /camera/camera/color/camera_info header.frame_id 7 best_effort || true
sample_field "Aligned depth" /camera/camera/aligned_depth_to_color/image_raw header.frame_id 7 best_effort || true
check_tf base_link camera_link || true
check_tf base_link camera_color_optical_frame || true

section "Pi candidate pipeline"
topic_counts /depth_candidates/candidates
topic_counts /depth_candidates/rgb_crops
sample_field "Depth candidate sample" /depth_candidates/candidates header.stamp 7 best_effort || true
sample_field "RGB crop sample" /depth_candidates/rgb_crops proposal_header.stamp 7 best_effort || true

section "WSL perception/finder visibility"
for topic in \
  /candidate_filter/status \
  /embedding_retrieval/status \
  /temporal_confirmation/status \
  /object_finder/status \
  /object_finder/result
do
  printf '\n[%s]\n' "$topic"
  topic_counts "$topic"
done

sample_string "Candidate-filter status" /candidate_filter/status 7 || true
sample_string "Embedding status" /embedding_retrieval/status 7 || true
sample_string "Temporal status" /temporal_confirmation/status 7 || true
sample_string "Finder status" /object_finder/status 7 || true

section "Localizer outputs before optional goal"
topic_counts /macrobot/perception/localized_detection
topic_counts /macrobot/perception/localizer_status
sample_string "Localized detection" /macrobot/perception/localized_detection 3 || true
sample_string "Localizer error/status" /macrobot/perception/localizer_status 3 || true

if [[ "$SEND_GOAL" != true ]]; then
  cat <<MSG

No finder goal was sent by this diagnostic run.
The finder is command-driven, so an idle finder may publish status but no
/object_finder/result and therefore no localized detection.

Run the active test with:
  $0 "$OBJECT_NAME" --send-goal
MSG
  exit 0
fi

section "Send a localization-only finder goal"
REQUEST_ID="manual-localization-$(date +%s)"
GOAL_JSON="$(python3 - "$OBJECT_NAME" "$REQUEST_ID" <<'PY'
import json
import sys
print(json.dumps({
    "object_name": sys.argv[1],
    "request_id": sys.argv[2],
    "timeout_sec": 45.0,
    "continuous": True,
    "rebuild_banks": False,
    "min_score": 0.0,
}, separators=(",", ":")))
PY
)"

printf 'object=%s\nrequest_id=%s\n' "$OBJECT_NAME" "$REQUEST_ID"
ros2 topic pub --once /object_finder/goal std_msgs/msg/String "{data: '$GOAL_JSON'}"

sleep 1
sample_string "Active target" /macrobot/pick/active_target 5 || true
sample_string "Finder acknowledgement/status" /object_finder/status 10 || true
sample_string "Finder result" /object_finder/result 45 || true

section "Localization result after finder goal"
if sample_string "Localized detection" /macrobot/perception/localized_detection 10; then
  echo
  ok "End-to-end localization is producing output."
else
  sample_string "Localizer rejection/status" /macrobot/perception/localizer_status 5 || true
  cat <<'MSG'

No localized result was observed. Check the first failed stage above.
If /object_finder/result contains object_found=true, inspect these JSON fields:
  localization.available
  localization.quality
  center_px.x / center_px.y
  depth_m
  stamp_sec
  frame_id

Common final-stage causes:
  - localizer node is not running
  - base_link -> camera_color_optical_frame TF is missing
  - require_patch_localization=true but localization.available=false
  - localization.quality below minimum_localization_quality
  - delayed result has no aligned-depth frame inside depth_sync_tolerance_sec
  - result object_name differs from /macrobot/pick/active_target
MSG
fi

section "Stop manual finder session"
ros2 topic pub --once /object_finder/cancel std_msgs/msg/String \
  "{data: 'manual_localization_diagnostic_complete'}" || true
