import cv2
import time
from pathlib import Path

CAM = "/dev/video0"
OUT_DIR = Path.home() / "MacRobot/data/camera_quality_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(CAM, cv2.CAP_V4L2)

if not cap.isOpened():
    raise RuntimeError("Camera open failed")

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

# 자동노출/자동초점 안정화
for _ in range(60):
    cap.read()
    time.sleep(0.03)

ret, frame = cap.read()

if not ret or frame is None:
    cap.release()
    raise RuntimeError("Frame read failed")

fourcc_value = int(cap.get(cv2.CAP_PROP_FOURCC))
fourcc = "".join([chr((fourcc_value >> 8 * i) & 0xFF) for i in range(4)])

print("Actual width:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Actual height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Actual fps:", cap.get(cv2.CAP_PROP_FPS))
print("Actual fourcc:", fourcc)

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
lap = cv2.Laplacian(gray, cv2.CV_64F).var()
print("Laplacian variance:", lap)

out_path = OUT_DIR / "quality_test_1920x1080.png"
cv2.imwrite(str(out_path), frame)

print("Saved:", out_path)

cap.release()