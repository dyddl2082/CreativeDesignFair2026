#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENT_ID="${1:-competition_arena_1}"

if [[ -f "$HOME/MacRobot/.venv-embedding/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/MacRobot/.venv-embedding/bin/activate"
else
  echo "WARNING: embedding venv not found: $HOME/MacRobot/.venv-embedding" >&2
fi

# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

if ! ros2 pkg prefix macrobot_object_finder >/dev/null 2>&1; then
  echo "ERROR: macrobot_object_finder package not found" >&2
  exit 2
fi

echo "[WSL finder] environment_id=$ENVIRONMENT_ID"
echo "Checking the DINO/XPU runtime first..."
ros2 run macrobot_perception embedding_runtime_check

echo "Starting candidate filter, embedding retrieval, temporal confirmation and finder."
exec ros2 launch macrobot_object_finder object_finder_wsl.launch.py \
  environment_id:="$ENVIRONMENT_ID"
