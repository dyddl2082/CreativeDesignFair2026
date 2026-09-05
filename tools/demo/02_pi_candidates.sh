#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

if ! ros2 pkg prefix depth_candidate_proposal >/dev/null 2>&1; then
  echo "ERROR: depth_candidate_proposal package not found" >&2
  exit 2
fi

echo "[Pi candidates] waiting for RealSense color/aligned-depth topics."
exec ros2 launch depth_candidate_proposal edge_candidate_pipeline.launch.py
