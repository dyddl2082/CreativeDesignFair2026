#!/usr/bin/env bash
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

failed=0
check_file() {
  if [[ -s "$1" ]]; then
    echo "OK   $1"
  else
    echo "FAIL $1" >&2
    failed=1
  fi
}

check_file "$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml"
check_file "$HOME/MacRobot/data/safe_region_serial2r_r4_fine/safe_connected_samples.csv"
check_file "$HOME/MacRobot/data/safe_region_serial2r_r4_fine/safe_region_summary.yaml"

for package in \
  macrobot_description \
  macrobot_camera_tf \
  depth_candidate_proposal \
  macrobot_perception \
  macrobot_object_finder \
  macrobot_pick_pipeline \
  macrobot_arm_control \
  pico_debug
do
  if prefix="$(ros2 pkg prefix "$package" 2>/dev/null)"; then
    echo "OK   $package -> $prefix"
  else
    echo "FAIL package not found: $package" >&2
    failed=1
  fi
done

python3 - "$HOME/MacRobot/data/safe_region_serial2r_r4_fine/safe_region_summary.yaml" <<'PY' || failed=1
from pathlib import Path
import sys
import yaml
path = Path(sys.argv[1])
if not path.is_file():
    raise SystemExit(1)
root = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
expected = "macrobot-serial-2axis-2026-09-04-r4"
found = str(root.get("model_revision", ""))
connected = root.get("counts", {}).get("connected_to_home", 0)
print(f"safe revision: {found}")
print(f"connected_to_home: {connected}")
if found != expected or not isinstance(connected, int) or connected <= 0:
    raise SystemExit(1)
PY

if [[ "$failed" -ne 0 ]]; then
  echo "Preflight failed." >&2
  exit 2
fi

echo "Static demo preflight passed. Live topics still need to be checked after launch."
