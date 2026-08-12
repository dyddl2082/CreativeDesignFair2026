#!/usr/bin/env bash
set -euo pipefail
ros2 topic echo \
  --once \
  /embedding_retrieval/results \
  macrobot_interfaces/msg/EmbeddingRetrievalResult
