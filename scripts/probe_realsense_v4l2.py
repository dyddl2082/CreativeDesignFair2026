import cv2
import glob
import subprocess
from pathlib import Path

out_dir = Path.home() / "MacRobot/data/realsense_probe"
out_dir.mkdir(parents=True, exist_ok=True)

def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=4).stdout
    except Exception as e:
        return str(e)

print("=== v4l2 devices ===")
print(run(["v4l2-ctl", "--list-devices"]))

print("=== by-id ===")
print(run(["bash", "-lc", "ls -l /dev/v4l/by-id/ 2>/dev/null"]))

for dev in sorted(glob.glob("/dev/video*")):
    print("\n==============================")
    print(dev)
    print(run(["v4l2-ctl", "-d", dev, "--info"]))
    print(run(["v4l2-ctl", "-d", dev, "--list-formats-ext"])[:2500])

    cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("OpenCV: cannot open")
        continue

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ok, frame = cap.read()

    if ok and frame is not None:
        save_path = out_dir / f"{Path(dev).name}.jpg"
        cv2.imwrite(str(save_path), frame)
        print(f"Saved: {save_path}, shape={frame.shape}")
    else:
        print("OpenCV: read failed")

    cap.release()