#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-dry}"
SERIAL_PORT="${2:-/dev/ttyACM0}"
SAFE_CSV="$HOME/MacRobot/data/safe_region_serial2r_r4_fine/safe_connected_samples.csv"
SAFE_SUMMARY="$HOME/MacRobot/data/safe_region_serial2r_r4_fine/safe_region_summary.yaml"
EXPECTED_REVISION="macrobot-serial-2axis-2026-09-04-r4"

case "$MODE" in
  dry)
    ALIGNMENT_DRY_RUN=true
    ;;
  live)
    ALIGNMENT_DRY_RUN=false
    ;;
  *)
    echo "Usage: $0 [dry|live] [/dev/ttyACM0]" >&2
    exit 2
    ;;
esac

# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

if [[ ! -s "$SAFE_CSV" ]]; then
  echo "ERROR: safe-region CSV missing or empty:" >&2
  echo "  $SAFE_CSV" >&2
  exit 2
fi
if [[ ! -s "$SAFE_SUMMARY" ]]; then
  echo "ERROR: safe-region summary missing or empty:" >&2
  echo "  $SAFE_SUMMARY" >&2
  exit 2
fi

python3 - "$SAFE_SUMMARY" "$EXPECTED_REVISION" <<'PY'
from pathlib import Path
import sys
import yaml

path = Path(sys.argv[1])
expected = sys.argv[2]
summary = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
found = str(summary.get("model_revision", ""))
connected = summary.get("counts", {}).get("connected_to_home", 0)
print(f"safe-region revision: {found}")
print(f"connected_to_home: {connected}")
if found != expected:
    raise SystemExit(f"ERROR: expected {expected}, found {found}")
if not isinstance(connected, int) or connected <= 0:
    raise SystemExit("ERROR: home-connected safe region is empty")
PY

if [[ ! -e "$SERIAL_PORT" ]]; then
  echo "WARNING: serial port does not currently exist: $SERIAL_PORT" >&2
fi

echo "[Pi robot stack] alignment mode=$MODE, serial=$SERIAL_PORT"
echo "This launch already starts robot_state_publisher, arm control, Pico bridge and localizer."
echo "Do not start those nodes separately."

exec ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  serial_port:="$SERIAL_PORT" \
  start_pico_debug:=true \
  start_base_alignment:=true \
  start_grasp_keyframes:=true \
  start_depth_clearance:=true \
  task_executable:=resilient_object_task_node \
  perception_input_mode:=legacy \
  alignment_dry_run:="$ALIGNMENT_DRY_RUN"
