#!/usr/bin/env bash
set -eo pipefail

WS="${1:-$HOME/MacRobot}"
SAFE_CSV="${2:-$WS/data/safe_region_serial2r_fine/safe_connected_samples.csv}"
CAMERA_TF="${3:-$WS/data/camera_tf/d435_rgb_anchor.yaml}"

set +u
source /opt/ros/jazzy/setup.bash
if [[ -f "$WS/install/setup.bash" ]]; then
  source "$WS/install/setup.bash"
fi
set -u

fail=0
warn=0

ok() { printf 'OK: %s\n' "$*"; }
warning() { printf 'WARNING: %s\n' "$*" >&2; warn=$((warn + 1)); }
error() { printf 'ERROR: %s\n' "$*" >&2; fail=$((fail + 1)); }

printf '[1/8] Required packages\n'
for pkg in \
  macrobot_description \
  macrobot_camera_tf \
  macrobot_pick_pipeline \
  macrobot_perception \
  macrobot_action_gateway
do
  if ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
    ok "$pkg"
  else
    error "ROS package not found: $pkg"
  fi
done

printf '[2/8] Camera TF calibration file\n'
if [[ -s "$CAMERA_TF" ]]; then
  if python3 - "$CAMERA_TF" <<'PYCODE'
from pathlib import Path
import sys
import yaml
path = Path(sys.argv[1])
root = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
assert int(root.get("schema_version", 0)) == 1
items = root.get("transforms") or []
pairs = {(str(x.get("parent")), str(x.get("child"))) for x in items if isinstance(x, dict)}
required = {
    ("camera_link", "camera_color_frame"),
    ("camera_color_frame", "camera_color_optical_frame"),
    ("camera_link", "camera_depth_frame"),
    ("camera_depth_frame", "camera_depth_optical_frame"),
}
missing = sorted(required - pairs)
if missing:
    raise SystemExit(f"missing camera TF pairs: {missing}")
print(f"OK: {path} ({len(items)} transforms)")
PYCODE
  then
    :
  else
    error "invalid camera calibration: $CAMERA_TF"
  fi
else
  error "camera calibration missing or empty: $CAMERA_TF"
fi

printf '[3/8] Safe-region CSV\n'
if [[ -s "$SAFE_CSV" ]]; then
  rows="$(wc -l < "$SAFE_CSV")"
  if [[ "$rows" -gt 1 ]]; then
    ok "$SAFE_CSV ($rows lines)"
  else
    error "safe-region CSV has no samples: $SAFE_CSV"
  fi
else
  error "safe-region CSV missing or empty: $SAFE_CSV"
fi

printf '[4/8] Current model revision\n'
REV_FILE="$WS/src/macrobot_description/config/collision_model_revision.txt"
if [[ -s "$REV_FILE" ]]; then
  printf 'model revision: '
  cat "$REV_FILE"
else
  warning "model revision file not found: $REV_FILE"
fi

printf '[5/8] Perception frame configuration\n'
PERCEPTION="$WS/src/macrobot_pick_pipeline/config/perception.yaml"
if [[ -s "$PERCEPTION" ]]; then
  if grep -Eq '^[[:space:]]*optical_frame_override:[[:space:]]*camera_color_optical_frame[[:space:]]*$' "$PERCEPTION"; then
    ok "optical_frame_override=camera_color_optical_frame"
  else
    error "perception optical_frame_override is not camera_color_optical_frame"
  fi
else
  error "perception config not found: $PERCEPTION"
fi

printf '[6/8] Persistent data directories\n'
for dir in \
  "$WS/data/object_memory" \
  "$WS/data/stored_objects" \
  "$WS/data/grasp_keyframes" \
  "$WS/data/commissioning"
do
  mkdir -p "$dir"
  if touch "$dir/.readiness_write_test" 2>/dev/null; then
    rm -f "$dir/.readiness_write_test"
    ok "writable: $dir"
  else
    error "not writable: $dir"
  fi
done

printf '[7/8] Runtime checks when nodes are active\n'
if ros2 node list 2>/dev/null | grep -qx '/camera/camera'; then
  if ros2 param get /camera/camera publish_tf 2>/dev/null | grep -qi false; then
    ok "RealSense publish_tf=false"
  else
    error "RealSense publish_tf is not false"
  fi
else
  warning "camera node is not running; runtime TF/topic checks skipped"
fi

if timeout 2s ros2 topic echo --once /macrobot/camera_tf/status >/dev/null 2>&1; then
  ok "camera TF status available"
else
  warning "camera TF status unavailable; start macrobot_camera_tf runtime"
fi

printf '[8/8] Boot epoch\n'
if [[ -r /proc/sys/kernel/random/boot_id ]]; then
  printf 'host boot_id: '
  cat /proc/sys/kernel/random/boot_id
else
  warning "host boot_id unavailable"
fi

printf '\n'
if [[ "$fail" -ne 0 ]]; then
  printf 'Readiness FAILED: %d error(s), %d warning(s).\n' "$fail" "$warn" >&2
  exit 2
fi
printf 'Readiness static checks passed with %d warning(s).\n' "$warn"
