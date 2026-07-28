"""Pure helpers for capture, ROI validation, depth statistics, and file output."""

from __future__ import annotations

import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import cv2
import numpy as np


@dataclass(frozen=True)
class Roi:
    """Pixel ROI using half-open image coordinates."""

    x: int
    y: int
    width: int
    height: int

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height

    def as_dict(self) -> dict[str, int]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


@dataclass(frozen=True)
class DepthStats:
    """Robust statistics for one aligned-depth crop."""

    available: bool
    valid_ratio: float = 0.0
    valid_count: int = 0
    median_m: float | None = None
    near_m: float | None = None
    far_m: float | None = None
    min_m: float | None = None
    max_m: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "valid_ratio": self.valid_ratio,
            "valid_count": self.valid_count,
            "median_m": self.median_m,
            "near_m": self.near_m,
            "far_m": self.far_m,
            "min_m": self.min_m,
            "max_m": self.max_m,
        }


def sanitize_component(value: str, fallback: str = "unnamed", max_length: int = 80) -> str:
    """Return a path-safe Unicode component while preserving Korean names."""

    normalized = unicodedata.normalize("NFKC", str(value or "")).strip()
    normalized = normalized.replace("/", "_").replace("\\", "_")
    normalized = re.sub(r"[^\w.\-]+", "_", normalized, flags=re.UNICODE)
    normalized = re.sub(r"_+", "_", normalized).strip(" ._-")
    if not normalized or normalized in {".", ".."}:
        normalized = fallback
    return normalized[:max_length]


def normalize_roi(
    raw: Mapping[str, Any] | Sequence[Any],
    image_width: int,
    image_height: int,
    min_width: int = 1,
    min_height: int = 1,
) -> Roi:
    """Clamp and validate a rectangle against an image boundary."""

    if image_width <= 0 or image_height <= 0:
        raise ValueError("Image dimensions must be positive")

    if isinstance(raw, Mapping):
        x = raw.get("x", 0)
        y = raw.get("y", 0)
        width = raw.get("width", raw.get("w", 0))
        height = raw.get("height", raw.get("h", 0))
    elif isinstance(raw, Sequence) and len(raw) >= 4:
        x, y, width, height = raw[:4]
    else:
        raise ValueError("ROI must be an object or sequence containing x, y, width, height")

    try:
        x_f = float(x)
        y_f = float(y)
        w_f = float(width)
        h_f = float(height)
    except (TypeError, ValueError) as exc:
        raise ValueError("ROI values must be numeric") from exc

    if not np.isfinite([x_f, y_f, w_f, h_f]).all():
        raise ValueError("ROI values must be finite")

    if w_f < 0:
        x_f += w_f
        w_f = -w_f
    if h_f < 0:
        y_f += h_f
        h_f = -h_f

    x1 = int(np.floor(x_f))
    y1 = int(np.floor(y_f))
    x2 = int(np.ceil(x_f + w_f))
    y2 = int(np.ceil(y_f + h_f))

    x1 = max(0, min(image_width, x1))
    y1 = max(0, min(image_height, y1))
    x2 = max(0, min(image_width, x2))
    y2 = max(0, min(image_height, y2))

    width_i = x2 - x1
    height_i = y2 - y1
    if width_i < int(min_width) or height_i < int(min_height):
        raise ValueError(
            f"Crop is too small: {width_i}x{height_i}px; "
            f"minimum is {min_width}x{min_height}px"
        )

    return Roi(x=x1, y=y1, width=width_i, height=height_i)


def map_roi_between_sizes(
    roi: Roi,
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
) -> Roi:
    """Map a color ROI proportionally to a depth image of another size."""

    if min(source_width, source_height, target_width, target_height) <= 0:
        raise ValueError("Source and target dimensions must be positive")

    x1 = int(np.floor(roi.x * target_width / source_width))
    y1 = int(np.floor(roi.y * target_height / source_height))
    x2 = int(np.ceil(roi.x2 * target_width / source_width))
    y2 = int(np.ceil(roi.y2 * target_height / source_height))

    return normalize_roi(
        {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1},
        target_width,
        target_height,
    )


def crop_array(image: np.ndarray, roi: Roi) -> np.ndarray:
    """Return an independent copy of an image crop."""

    if image.ndim < 2:
        raise ValueError("Image must have at least two dimensions")
    height, width = image.shape[:2]
    bounded = normalize_roi(roi.as_dict(), width, height)
    return image[bounded.y : bounded.y2, bounded.x : bounded.x2].copy()


def depth_to_meters(depth: np.ndarray, encoding: str, depth_scale_m: float) -> np.ndarray:
    """Convert common RealSense ROS depth encodings to float32 meters."""

    normalized = str(encoding or "").lower()
    array = np.asarray(depth)
    if normalized in {"32fc1", "32fc"} or np.issubdtype(array.dtype, np.floating):
        meters = array.astype(np.float32, copy=False)
    elif normalized in {"16uc1", "mono16", "16sc1", ""} or np.issubdtype(
        array.dtype, np.integer
    ):
        if depth_scale_m <= 0:
            raise ValueError("depth_scale_m must be positive for integer depth images")
        meters = array.astype(np.float32) * float(depth_scale_m)
    else:
        raise ValueError(f"Unsupported depth encoding: {encoding}")

    meters = meters.copy()
    meters[~np.isfinite(meters)] = 0.0
    meters[meters <= 0.0] = 0.0
    return meters


def compute_depth_stats(
    depth_m: np.ndarray | None,
    roi: Roi | None = None,
    min_depth_m: float = 0.05,
    max_depth_m: float = 10.0,
) -> DepthStats:
    """Compute robust p10/median/p90 statistics for valid depth values."""

    if depth_m is None:
        return DepthStats(available=False)

    array = np.asarray(depth_m, dtype=np.float32)
    if array.ndim != 2:
        raise ValueError("Depth image must be two-dimensional")
    if roi is not None:
        array = crop_array(array, roi)

    total = int(array.size)
    if total == 0:
        return DepthStats(available=False)

    valid_mask = np.isfinite(array) & (array >= min_depth_m) & (array <= max_depth_m)
    valid = array[valid_mask]
    if valid.size == 0:
        return DepthStats(available=True, valid_ratio=0.0, valid_count=0)

    p10, median, p90 = np.percentile(valid, [10.0, 50.0, 90.0])
    return DepthStats(
        available=True,
        valid_ratio=float(valid.size / total),
        valid_count=int(valid.size),
        median_m=float(median),
        near_m=float(p10),
        far_m=float(p90),
        min_m=float(valid.min()),
        max_m=float(valid.max()),
    )


def encode_image(image: np.ndarray, extension: str, quality: int = 95) -> bytes:
    """Encode an OpenCV image and raise a useful error on failure."""

    extension = extension.lower()
    if extension not in {".jpg", ".jpeg", ".png"}:
        raise ValueError(f"Unsupported image extension: {extension}")
    params: list[int] = []
    if extension in {".jpg", ".jpeg"}:
        params = [int(cv2.IMWRITE_JPEG_QUALITY), int(np.clip(quality, 20, 100))]
    elif extension == ".png":
        params = [int(cv2.IMWRITE_PNG_COMPRESSION), 3]
    success, encoded = cv2.imencode(extension, image, params)
    if not success:
        raise RuntimeError(f"OpenCV failed to encode {extension} image")
    return encoded.tobytes()


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write bytes atomically in the destination directory."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write UTF-8 JSON atomically."""

    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False)
    atomic_write_bytes(path, (serialized + "\n").encode("utf-8"))


def ensure_under_root(root: Path, candidate: Path) -> Path:
    """Resolve a path and ensure it remains below the configured root."""

    root_resolved = Path(root).expanduser().resolve()
    candidate_resolved = Path(candidate).expanduser().resolve()
    if candidate_resolved != root_resolved and root_resolved not in candidate_resolved.parents:
        raise ValueError(f"Path escapes configured root: {candidate}")
    return candidate_resolved
