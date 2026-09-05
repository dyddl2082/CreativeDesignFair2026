#!/usr/bin/env bash
set -eo pipefail

WS="${1:-$HOME/MacRobot}"

set +u
source /opt/ros/jazzy/setup.bash
if [[ -f "$WS/install/setup.bash" ]]; then
  source "$WS/install/setup.bash"
fi
set -u

fail=0

echo "[1/6] RealSense publish_tf must be false"
if ros2 param get /camera/camera publish_tf 2>/dev/null | grep -qi 'false'; then
  echo "OK: RealSense TF publication is disabled."
else
  echo "ERROR: /camera/camera publish_tf is not false or the node is unavailable." >&2
  fail=1
fi

echo "[2/6] Camera TF publisher status"
if timeout 5s ros2 topic echo --once /macrobot/camera_tf/status >/tmp/macrobot_camera_tf_status.txt 2>&1; then
  cat /tmp/macrobot_camera_tf_status.txt
else
  echo "ERROR: no /macrobot/camera_tf/status sample." >&2
  cat /tmp/macrobot_camera_tf_status.txt >&2 || true
  fail=1
fi

echo "[3/6] Color CameraInfo header"
if timeout 5s ros2 topic echo /camera/camera/color/camera_info --once --field header.frame_id >/tmp/macrobot_color_frame.txt 2>&1; then
  cat /tmp/macrobot_color_frame.txt
else
  echo "ERROR: color CameraInfo unavailable." >&2
  fail=1
fi

echo "[4/6] Aligned depth header"
if timeout 5s ros2 topic echo /camera/camera/aligned_depth_to_color/image_raw --once --field header.frame_id >/tmp/macrobot_aligned_frame.txt 2>&1; then
  cat /tmp/macrobot_aligned_frame.txt
else
  echo "ERROR: aligned depth unavailable." >&2
  fail=1
fi

echo "[5/6] Required transforms"
python3 - <<'PY' || fail=1
import subprocess
pairs = [
    ("base_link", "camera_link"),
    ("base_link", "camera_color_optical_frame"),
    ("base_link", "camera_depth_optical_frame"),
]
for parent, child in pairs:
    result = subprocess.run(
        ["timeout", "4s", "ros2", "run", "tf2_ros", "tf2_echo", parent, child],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    text = result.stdout
    ok = "Translation:" in text and "Rotation:" in text
    print(f"{parent} -> {child}: {'OK' if ok else 'FAILED'}")
    if not ok:
        print(text)
        raise SystemExit(1)
PY

echo "[6/6] Localizer optical-frame configuration"
PARAM="$WS/src/macrobot_pick_pipeline/config/perception.yaml"
if grep -Eq '^[[:space:]]*optical_frame_override:[[:space:]]*camera_color_optical_frame[[:space:]]*$' "$PARAM"; then
  echo "OK: localizer is pinned to camera_color_optical_frame."
else
  echo "ERROR: optical_frame_override is not camera_color_optical_frame in $PARAM" >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "Camera TF runtime verification failed." >&2
  exit 2
fi

echo "Camera TF runtime verification passed."
