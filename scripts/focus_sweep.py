import cv2
import subprocess
import time
from pathlib import Path

CAM = "/dev/video0"
OUT_DIR = Path.home() / "MacRobot/data/focus_sweep"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def set_ctrl(name, value):
    subprocess.run(
        ["v4l2-ctl", "-d", CAM, "-c", f"{name}={value}"],
        check=False
    )

# 수동초점 모드
set_ctrl("focus_automatic_continuous", 0)

cap = cv2.VideoCapture(CAM, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    raise RuntimeError("Camera open failed")

results = []

# 처음에는 넓게 탐색
for focus in range(0, 1024, 50):
    set_ctrl("focus_absolute", focus)
    time.sleep(0.5)

    # 안정화 프레임 버리기
    for _ in range(10):
        cap.read()
        time.sleep(0.02)

    ok, frame = cap.read()
    if not ok or frame is None:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F).var()

    filename = OUT_DIR / f"focus_{focus:04d}_lap_{lap:.1f}.jpg"
    cv2.imwrite(str(filename), frame)

    results.append((focus, lap, filename))
    print(f"focus={focus:4d}, laplacian={lap:.2f}, saved={filename}")

cap.release()

print("\nTop results:")
for focus, lap, filename in sorted(results, key=lambda x: x[1], reverse=True)[:10]:
    print(f"focus={focus:4d}, laplacian={lap:.2f}, file={filename}")