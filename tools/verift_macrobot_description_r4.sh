#!/usr/bin/env bash
set -euo pipefail

WS="${1:-$HOME/MacRobot}"
PKG="$WS/src/macrobot_description"
EXPECTED_REVISION="macrobot-serial-2axis-2026-09-04-r4"

source_setup() {
  local setup_file="$1"
  if [[ -f "$setup_file" ]]; then
    set +u
    # shellcheck disable=SC1090
    source "$setup_file"
    set -u
  fi
}

if [[ ! -d "$PKG" ]]; then
  echo "ERROR: package not found: $PKG" >&2
  exit 1
fi

printf '%s\n' '[1/7] Package checksum and static validator'
(
  cd "$PKG"
  sha256sum -c CHECKSUMS.sha256
)
python3 "$PKG/scripts/validate_description.py" "$PKG"

printf '%s\n' '[2/7] Python syntax'
python3 -m py_compile \
  "$PKG/scripts/validate_description.py" \
  "$PKG/scripts/print_joint_direction_report.py" \
  "$PKG"/launch/*.py

printf '%s\n' '[3/7] ROS parameter array type check'
python3 - "$PKG/config/kinematics.yaml" <<'PY'
from pathlib import Path
import sys
import yaml

path = Path(sys.argv[1])
root = yaml.safe_load(path.read_text(encoding='utf-8'))
params = root['/**']['ros__parameters']
keys = (
    'shoulder_origin_xyz',
    'shoulder_origin_rpy',
    'shoulder_axis',
    'wrist_origin_xyz',
    'wrist_origin_rpy',
    'wrist_axis',
    'grasp_origin_xyz',
    'grasp_origin_rpy',
    'nominal_grasp_xyz_in_gripper_link',
    'nominal_grasp_rpy_in_gripper_link',
    'shoulder_axis_base',
    'wrist_axis_base_zero',
    'arm_axis_base_xy',
    'positive_tilt_direction_base_xy',
)
for key in keys:
    value = params[key]
    if not isinstance(value, list) or not all(type(item) is float for item in value):
        raise SystemExit(f'ERROR: {key} is not a homogeneous double array: {value!r}')
print('All kinematic vector parameters are homogeneous double arrays.')
PY

printf '%s\n' '[4/7] Active legacy behavior scan'
python3 - "$PKG" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
patterns = {
    'q1_plus_q2': re.compile(r'\bq1\s*\+\s*q2\b'),
    'four_bar_enabled': re.compile(r'\bfour_bar_enabled\s*:\s*(?:true|True|1)\b'),
    'old_passive_joint': re.compile(
        r'ratio_(?:left|right)_gear_joint|back_link_top_link_joint|servo_(?:left|right)_gear_joint'
    ),
    'generic_ros2_control': re.compile(r'<ros2_control\b'),
}
allowed_suffixes = {'.py', '.cpp', '.hpp', '.h', '.yaml', '.yml', '.xml', '.urdf', '.xacro'}
ignored = {'docs', 'original', 'validation', 'backup', 'build', 'install', 'log'}
findings = []
for path in root.rglob('*'):
    if not path.is_file() or path.suffix not in allowed_suffixes:
        continue
    if any(part in ignored for part in path.parts):
        continue
    text = path.read_text(encoding='utf-8', errors='replace')
    for line_number, line in enumerate(text.splitlines(), 1):
        for name, pattern in patterns.items():
            if pattern.search(line):
                findings.append((path, line_number, name, line.strip()))
if findings:
    for item in findings:
        print(f'ERROR {item[0]}:{item[1]}: {item[2]}: {item[3]}')
    raise SystemExit(2)
print('No active four-bar or generic ros2_control behavior remains.')
PY

printf '%s\n' '[5/7] ROS/Xacro expansion'
source_setup /opt/ros/jazzy/setup.bash
source_setup "$WS/install/setup.bash"

if ! command -v ros2 >/dev/null 2>&1; then
  echo 'ERROR: ros2 is not available after sourcing the environment.' >&2
  exit 1
fi

SHARE_DIR="$(ros2 pkg prefix --share macrobot_description)"
case "$SHARE_DIR" in
  "$WS"/*) ;;
  *)
    echo "ERROR: ros2 resolves macrobot_description outside the workspace: $SHARE_DIR" >&2
    exit 1
    ;;
esac

for model in \
  macrobot_full_visual \
  macrobot_full_collision \
  macrobot_full_exact_gripper \
  macrobot_arm_kinematic
do
  xacro "$SHARE_DIR/urdf/${model}.urdf.xacro" > "/tmp/${model}_r4.urdf"
  if command -v check_urdf >/dev/null 2>&1; then
    check_urdf "/tmp/${model}_r4.urdf"
  fi
done

printf '%s\n' '[6/7] Installed revision check'
INSTALLED_REVISION="$(tr -d '[:space:]' < "$SHARE_DIR/config/collision_model_revision.txt")"
if [[ "$INSTALLED_REVISION" != "$EXPECTED_REVISION" ]]; then
  echo "ERROR: installed revision is $INSTALLED_REVISION" >&2
  exit 1
fi
printf 'Installed revision: %s\n' "$INSTALLED_REVISION"

printf '%s\n' '[7/7] Joint direction report'
python3 "$PKG/scripts/print_joint_direction_report.py"

cat <<'MSG'

Static and ROS description checks passed.
This result does not replace RViz visual direction checks, MoveIt collision regeneration,
safe-region regeneration, servo calibration, or low-speed hardware validation.
MSG
