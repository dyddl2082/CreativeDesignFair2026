#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OBJECT_NAME="${1:-Eraser}"
TIMEOUT_SEC="${2:-60}"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

REQUEST_ID="manual-localization-$(date +%s)"
GOAL_JSON="$(python3 - "$OBJECT_NAME" "$REQUEST_ID" "$TIMEOUT_SEC" <<'PY'
import json
import sys
print(json.dumps({
    "object_name": sys.argv[1],
    "request_id": sys.argv[2],
    "timeout_sec": float(sys.argv[3]),
    "continuous": True,
    "rebuild_banks": False,
    "min_score": 0.0,
}, separators=(",", ":")))
PY
)"

echo "Sending finder goal: object=$OBJECT_NAME request_id=$REQUEST_ID"
ros2 topic pub --once /object_finder/goal std_msgs/msg/String "{data: '$GOAL_JSON'}"

echo "Watch in other terminals:"
echo "  $SCRIPT_DIR/05_monitor.sh finder"
echo "  $SCRIPT_DIR/05_monitor.sh finder-result"
echo "  $SCRIPT_DIR/05_monitor.sh localizer"
