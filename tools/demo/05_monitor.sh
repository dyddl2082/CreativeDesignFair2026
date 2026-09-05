#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-stored}"
RAW_MESSAGE=false
# shellcheck disable=SC1091
source "$SCRIPT_DIR/macrobot_demo_env.sh"

case "$MODE" in
  finder)    TOPIC=/object_finder/status ;;
  finder-result) TOPIC=/object_finder/result ;;
  localizer) TOPIC=/macrobot/perception/localized_detection ;;
  localizer-status) TOPIC=/macrobot/perception/localizer_status ;;
  object-point) TOPIC=/macrobot/perception/object_point; RAW_MESSAGE=true ;;
  stored)    TOPIC=/macrobot/stored_pick/status ;;
  arm)       TOPIC=/macrobot/arm/servo_bridge/status ;;
  validator) TOPIC=/macrobot/arm/validation_status ;;
  pico)      TOPIC=/pico_debug/response ;;
  embedding) TOPIC=/embedding_retrieval/status ;;
  temporal)  TOPIC=/temporal_confirmation/status ;;
  *)
    echo "Usage: $0 [finder|finder-result|localizer|localizer-status|object-point|stored|arm|validator|pico|embedding|temporal]" >&2
    exit 2
    ;;
esac

echo "Monitoring $TOPIC"
if [[ "$RAW_MESSAGE" == true ]]; then
  exec ros2 topic echo "$TOPIC"
fi
exec ros2 topic echo "$TOPIC" --field data --full-length
