#!/usr/bin/env bash
set -euo pipefail
for topic in \
  /camera/camera/color/camera_info \
  /depth_candidates/candidates \
  /depth_candidates/rgb_crops \
  /candidate_filter/results \
  /embedding_retrieval/results \
  /temporal_confirmation/confirmed \
  /object_finder/status \
  /object_finder/result; do
  printf '%-48s ' "$topic"
  if timeout 3s ros2 topic info "$topic" >/dev/null 2>&1; then
    echo OK
  else
    echo MISSING
  fi
done
