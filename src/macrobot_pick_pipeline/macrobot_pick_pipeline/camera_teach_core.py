"""Pure helpers for camera-authoritative grasp teaching.

The teaching workflow deliberately locks one robust RGB-D object observation
before the arm starts to occlude the target.  Every semantic keyframe and the
stored grasp docking profile then share that exact reference point and axial
orientation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median
from typing import Iterable, Mapping, Sequence, Tuple


Vector3 = Tuple[float, float, float]


@dataclass(frozen=True)
class CameraReferenceSample:
    point_base: Vector3
    orientation_deg: float
    orientation_class: str
    orientation_quality: float
    localization_quality: float
    depth_std_m: float
    center_std_px: float
    score: float
    source_stamp_sec: float
    published_stamp_sec: float


@dataclass(frozen=True)
class CameraTeachingReference:
    point_base: Vector3
    point_radius_m: float
    orientation_deg: float
    orientation_class: str
    orientation_quality: float
    orientation_spread_deg: float
    localization_quality: float
    depth_std_m: float
    center_std_px: float
    score: float
    sample_count: int

    def orientation_mapping(self) -> dict[str, object]:
        return {
            "angle_deg": self.orientation_deg,
            "class": self.orientation_class,
            "quality": self.orientation_quality,
            "spread_deg": self.orientation_spread_deg,
        }

    def to_mapping(self) -> dict[str, object]:
        return {
            "point_base": list(self.point_base),
            "point_radius_m": self.point_radius_m,
            "orientation": self.orientation_mapping(),
            "localization_quality": self.localization_quality,
            "depth_std_m": self.depth_std_m,
            "center_std_px": self.center_std_px,
            "score": self.score,
            "sample_count": self.sample_count,
        }


def _finite(value: object, field: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def _point(value: object) -> Vector3:
    if isinstance(value, Mapping):
        raw = (value.get("x"), value.get("y"), value.get("z"))
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        raw = value
    else:
        raise ValueError("point_base must be an x/y/z mapping or three-vector")
    result = tuple(_finite(item, "point_base") for item in raw)
    return result  # type: ignore[return-value]


def sample_from_localized_payload(
    payload: Mapping[str, object],
    *,
    expected_object: str,
) -> CameraReferenceSample:
    if str(payload.get("event", "")) != "localized_object":
        raise ValueError("payload is not a localized_object event")
    object_name = str(payload.get("object_name", "")).strip()
    if object_name.casefold() != expected_object.strip().casefold():
        raise ValueError("localized object name does not match teaching target")

    localization_raw = payload.get("localization", {})
    orientation_raw = payload.get("orientation", {})
    localization = localization_raw if isinstance(localization_raw, Mapping) else {}
    orientation = orientation_raw if isinstance(orientation_raw, Mapping) else {}

    angle = _finite(orientation.get("angle_deg", 0.0), "orientation.angle_deg") % 180.0
    quality = max(
        0.0,
        min(1.0, _finite(orientation.get("quality", 0.0), "orientation.quality")),
    )
    orientation_class = str(orientation.get("class", "unknown")).strip() or "unknown"
    return CameraReferenceSample(
        point_base=_point(payload.get("point_base")),
        orientation_deg=angle,
        orientation_class=orientation_class,
        orientation_quality=quality,
        localization_quality=max(
            0.0,
            min(
                1.0,
                _finite(localization.get("quality", 0.0), "localization.quality"),
            ),
        ),
        depth_std_m=max(0.0, _finite(payload.get("depth_std_m", 0.0), "depth_std_m")),
        center_std_px=max(
            0.0,
            _finite(payload.get("center_std_px", 0.0), "center_std_px"),
        ),
        score=max(0.0, min(1.0, _finite(payload.get("score", 0.0), "score"))),
        source_stamp_sec=_finite(payload.get("stamp_sec", 0.0), "stamp_sec"),
        published_stamp_sec=_finite(
            payload.get("published_at_sec", payload.get("stamp_sec", 0.0)),
            "published_at_sec",
        ),
    )


def axial_error_deg(first_deg: float, second_deg: float) -> float:
    difference = abs((float(first_deg) - float(second_deg)) % 180.0)
    return min(difference, 180.0 - difference)


def axial_mean_deg(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("at least one axial angle is required")
    cosine = sum(math.cos(math.radians(2.0 * value)) for value in values)
    sine = sum(math.sin(math.radians(2.0 * value)) for value in values)
    if abs(cosine) < 1e-12 and abs(sine) < 1e-12:
        # Degenerate axial mean: choose the sample minimising total axial error.
        return min(
            (float(value) % 180.0 for value in values),
            key=lambda candidate: sum(axial_error_deg(candidate, item) for item in values),
        )
    return (0.5 * math.degrees(math.atan2(sine, cosine))) % 180.0


def _median_point(samples: Sequence[CameraReferenceSample]) -> Vector3:
    return (
        float(median(sample.point_base[0] for sample in samples)),
        float(median(sample.point_base[1] for sample in samples)),
        float(median(sample.point_base[2] for sample in samples)),
    )


def aggregate_camera_reference(
    samples: Iterable[CameraReferenceSample],
    *,
    minimum_count: int = 5,
    maximum_point_radius_m: float = 0.008,
    minimum_localization_quality: float = 0.15,
    maximum_depth_std_m: float = 0.035,
    maximum_center_std_px: float = 20.0,
    minimum_orientation_quality: float = 0.45,
    maximum_orientation_spread_deg: float = 8.0,
) -> CameraTeachingReference:
    accepted = [
        sample
        for sample in samples
        if sample.localization_quality >= float(minimum_localization_quality)
        and sample.depth_std_m <= float(maximum_depth_std_m)
        and sample.center_std_px <= float(maximum_center_std_px)
        and sample.orientation_quality >= float(minimum_orientation_quality)
        and sample.orientation_class != "unknown"
    ]
    if len(accepted) < max(1, int(minimum_count)):
        raise ValueError(
            "not_enough_camera_reference_samples: "
            f"accepted={len(accepted)} required={max(1, int(minimum_count))}"
        )

    # Use only the most recent required-size window.  This prevents an old view
    # from being mixed with the operator's final teaching placement.
    window = accepted[-max(1, int(minimum_count)) :]
    center = _median_point(window)
    radius = max(
        math.dist(sample.point_base, center)
        for sample in window
    )
    if radius > float(maximum_point_radius_m):
        raise ValueError(
            "camera_reference_position_unstable: "
            f"radius={radius:.6f} limit={float(maximum_point_radius_m):.6f}"
        )

    angle = axial_mean_deg([sample.orientation_deg for sample in window])
    spread = max(axial_error_deg(sample.orientation_deg, angle) for sample in window)
    if spread > float(maximum_orientation_spread_deg):
        raise ValueError(
            "camera_reference_orientation_unstable: "
            f"spread={spread:.3f} limit={float(maximum_orientation_spread_deg):.3f}"
        )

    # Raw patch quality and multi-frame angular consistency are both required.
    raw_quality = float(median(sample.orientation_quality for sample in window))
    consistency = max(0.0, 1.0 - spread / max(float(maximum_orientation_spread_deg), 1e-6))
    combined_quality = max(0.0, min(1.0, raw_quality * (0.5 + 0.5 * consistency)))

    classes = [sample.orientation_class for sample in window]
    orientation_class = max(sorted(set(classes)), key=classes.count)
    return CameraTeachingReference(
        point_base=center,
        point_radius_m=radius,
        orientation_deg=angle,
        orientation_class=orientation_class,
        orientation_quality=combined_quality,
        orientation_spread_deg=spread,
        localization_quality=float(median(sample.localization_quality for sample in window)),
        depth_std_m=float(median(sample.depth_std_m for sample in window)),
        center_std_px=float(median(sample.center_std_px for sample in window)),
        score=float(median(sample.score for sample in window)),
        sample_count=len(window),
    )
