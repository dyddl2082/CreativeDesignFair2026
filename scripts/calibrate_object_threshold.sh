#!/usr/bin/env bash
set -euo pipefail
OBJECT="${1:?usage: calibrate_object_threshold.sh <object> [environment] [duration_sec]}"
ENVIRONMENT="${2:-default}"
DURATION="${3:-10}"
ros2 run macrobot_object_finder threshold_calibration_cli \
  calibrate "$OBJECT" \
  --environment "$ENVIRONMENT" \
  --duration "$DURATION" \
  --confirm-visible
