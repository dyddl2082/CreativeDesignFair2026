"""Pure helpers for camera-authoritative grasp teaching.

The teaching workflow locks one robust RGB-D object observation before the arm
occludes the target.  Position samples and orientation samples are evaluated
separately: position always comes from the recent stable RGB-D window, while
orientation is aggregated only inside one compatible domain.  In particular,
base-frame depth-assisted 3-D yaw is never averaged with image-plane 2-D angle.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median
from typing import Iterable, Mapping, Optional, Sequence, Tuple

from .orientation_domain import (
    axis_from_mapping,
    axis_mapping,
    axial_yaw_deg,
    canonical_axis,
    is_measured_base_axis_orientation,
)


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
    orientation_source: str = ""
    orientation_coordinate_frame: str = ""
    orientation_semantics: str = ""
    orientation_axis_base: Optional[Vector3] = None
    orientation_3d_available: bool = False
    orientation_2d_deg: float = 0.0
    orientation_2d_class: str = "unknown"
    orientation_2d_quality: float = 0.0


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
    orientation_source: str = ""
    orientation_coordinate_frame: str = ""
    orientation_semantics: str = ""
    orientation_axis_base: Optional[Vector3] = None
    orientation_sample_count: int = 0
    orientation_mode: str = "auto"

    def orientation_mapping(self) -> dict[str, object]:
        result: dict[str, object] = {
            "angle_deg": self.orientation_deg,
            "class": self.orientation_class,
            "quality": self.orientation_quality,
            "spread_deg": self.orientation_spread_deg,
            "source": self.orientation_source,
            "coordinate_frame": self.orientation_coordinate_frame,
            "semantics": self.orientation_semantics,
            "sample_count": self.orientation_sample_count,
            "selection_mode": self.orientation_mode,
        }
        mapped_axis = axis_mapping(self.orientation_axis_base)
        if mapped_axis is not None:
            result["axis_base"] = mapped_axis
        return result

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


def _orientation_fields(value: object) -> tuple[float, str, float, str, str, str]:
    mapping = value if isinstance(value, Mapping) else {}
    angle = _finite(mapping.get("angle_deg", 0.0), "orientation.angle_deg") % 180.0
    quality = max(
        0.0,
        min(1.0, _finite(mapping.get("quality", 0.0), "orientation.quality")),
    )
    return (
        angle,
        str(mapping.get("class", "unknown")).strip() or "unknown",
        quality,
        str(mapping.get("source", "")).strip(),
        str(mapping.get("coordinate_frame", "")).strip(),
        str(mapping.get("semantics", "")).strip(),
    )


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
    localization = localization_raw if isinstance(localization_raw, Mapping) else {}
    orientation_raw = payload.get("orientation", {})
    orientation_2d_raw = payload.get("orientation_2d", orientation_raw)
    orientation_3d_raw = payload.get("orientation_3d", {})
    orientation_3d = (
        orientation_3d_raw if isinstance(orientation_3d_raw, Mapping) else {}
    )

    (
        angle,
        orientation_class,
        quality,
        source,
        coordinate_frame,
        semantics,
    ) = _orientation_fields(orientation_raw)
    angle_2d, class_2d, quality_2d, _, _, _ = _orientation_fields(
        orientation_2d_raw
    )
    axis = axis_from_mapping(
        orientation_3d.get(
            "axis_base",
            orientation_raw.get("axis_base")
            if isinstance(orientation_raw, Mapping)
            else None,
        )
    )
    available_3d = bool(orientation_3d.get("available", False)) and axis is not None

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
        depth_std_m=max(
            0.0,
            _finite(payload.get("depth_std_m", 0.0), "depth_std_m"),
        ),
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
        orientation_source=source,
        orientation_coordinate_frame=coordinate_frame,
        orientation_semantics=semantics,
        orientation_axis_base=axis,
        orientation_3d_available=available_3d,
        orientation_2d_deg=angle_2d,
        orientation_2d_class=class_2d,
        orientation_2d_quality=quality_2d,
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
        return min(
            (float(value) % 180.0 for value in values),
            key=lambda candidate: sum(
                axial_error_deg(candidate, item) for item in values
            ),
        )
    return (0.5 * math.degrees(math.atan2(sine, cosine))) % 180.0


def _median_point(samples: Sequence[CameraReferenceSample]) -> Vector3:
    return (
        float(median(sample.point_base[0] for sample in samples)),
        float(median(sample.point_base[1] for sample in samples)),
        float(median(sample.point_base[2] for sample in samples)),
    )


def _orientation_class(angle_deg: float) -> str:
    angle = float(angle_deg) % 180.0
    if angle <= 25.0 or angle >= 155.0:
        return "horizontal"
    if 65.0 <= angle <= 115.0:
        return "vertical"
    return "diagonal"


def _aggregate_axis(
    samples: Sequence[CameraReferenceSample],
) -> tuple[Vector3, float]:
    usable = [
        sample
        for sample in samples
        if sample.orientation_axis_base is not None
    ]
    if not usable:
        raise ValueError("no 3-D orientation axes are available")
    anchor = max(usable, key=lambda sample: sample.orientation_quality)
    anchor_axis = canonical_axis(anchor.orientation_axis_base or (1.0, 0.0, 0.0))
    total = [0.0, 0.0, 0.0]
    for sample in usable:
        axis = canonical_axis(sample.orientation_axis_base or anchor_axis)
        dot = sum(first * second for first, second in zip(axis, anchor_axis))
        if dot < 0.0:
            axis = tuple(-value for value in axis)
        weight = max(1e-6, float(sample.orientation_quality))
        for index in range(3):
            total[index] += weight * axis[index]
    mean_axis = canonical_axis(total)
    return mean_axis, axial_yaw_deg(mean_axis)


def _two_d_angle(sample: CameraReferenceSample) -> float:
    if sample.orientation_2d_class != "unknown" or sample.orientation_2d_quality > 0.0:
        return float(sample.orientation_2d_deg) % 180.0
    return float(sample.orientation_deg) % 180.0


def _two_d_class(sample: CameraReferenceSample) -> str:
    if sample.orientation_2d_class != "unknown":
        return sample.orientation_2d_class
    return sample.orientation_class


def _two_d_quality(sample: CameraReferenceSample) -> float:
    if sample.orientation_2d_class != "unknown" or sample.orientation_2d_quality > 0.0:
        return float(sample.orientation_2d_quality)
    return float(sample.orientation_quality)


def _choose_orientation_samples(
    window: Sequence[CameraReferenceSample],
    *,
    mode: str,
    minimum_orientation_quality: float,
    minimum_3d_count: int,
    minimum_2d_count: int,
) -> tuple[list[CameraReferenceSample], str]:
    mode = str(mode).strip().casefold()
    if mode not in {"auto", "3d", "2d"}:
        raise ValueError("orientation_mode must be auto, 3d, or 2d")

    # Keep each measured 3-D domain separate.  In particular, an old
    # long-axis profile must never be averaged with the upright-face normal
    # introduced for vertically standing objects.
    three_d_groups: dict[tuple[str, str, str], list[CameraReferenceSample]] = {}
    for sample in window:
        if (
            sample.orientation_quality >= float(minimum_orientation_quality)
            and is_measured_base_axis_orientation(
                source=sample.orientation_source,
                coordinate_frame=sample.orientation_coordinate_frame,
                semantics=sample.orientation_semantics,
                axis=sample.orientation_axis_base,
            )
        ):
            key = (
                sample.orientation_source,
                sample.orientation_coordinate_frame,
                sample.orientation_semantics,
            )
            three_d_groups.setdefault(key, []).append(sample)

    required_3d = max(1, int(minimum_3d_count))
    eligible_3d = [
        (key, samples)
        for key, samples in three_d_groups.items()
        if len(samples) >= required_3d
    ]
    if mode in {"auto", "3d"} and eligible_3d:
        # All demonstration objects are upright, so prefer the visible-face
        # plane domain.  Fall back to the old depth-axis domain only for
        # compatibility with previously recorded data.
        _, selected = max(
            eligible_3d,
            key=lambda item: (
                item[0][0] == "upright_face_plane_3d",
                len(item[1]),
                item[1][-1].published_stamp_sec,
            ),
        )
        return selected, "3d"
    if mode == "3d":
        counts = {
            f"{source}:{frame}:{semantics}": len(samples)
            for (source, frame, semantics), samples in three_d_groups.items()
        }
        raise ValueError(
            "not_enough_3d_orientation_samples: "
            f"domains={counts} required={required_3d}"
        )

    # Every localized payload keeps the raw image-axis estimate separately.
    # It remains an explicit auto/2-D fallback and is never mixed with 3-D.
    two_d = [
        sample
        for sample in window
        if _two_d_class(sample) != "unknown"
        and _two_d_quality(sample) >= float(minimum_orientation_quality)
    ]
    required_2d = max(1, int(minimum_2d_count))
    if len(two_d) >= required_2d:
        return two_d, "2d"
    raise ValueError(
        "not_enough_orientation_samples: "
        f"3d_domains={{{', '.join(f'{key!r}: {len(value)}' for key, value in three_d_groups.items())}}}, "
        f"2d={len(two_d)}/{required_2d}"
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
    orientation_mode: str = "auto",
    minimum_3d_orientation_samples: int = 3,
    minimum_2d_orientation_samples: int = 3,
) -> CameraTeachingReference:
    # Position acceptance deliberately does not require orientation.  A brief
    # 3-D fit dropout must not discard an otherwise valid RGB-D position sample.
    accepted = [
        sample
        for sample in samples
        if sample.localization_quality >= float(minimum_localization_quality)
        and sample.depth_std_m <= float(maximum_depth_std_m)
        and sample.center_std_px <= float(maximum_center_std_px)
    ]
    required = max(1, int(minimum_count))
    if len(accepted) < required:
        raise ValueError(
            "not_enough_camera_reference_samples: "
            f"accepted={len(accepted)} required={required}"
        )

    window = accepted[-required:]
    center = _median_point(window)
    radius = max(math.dist(sample.point_base, center) for sample in window)
    if radius > float(maximum_point_radius_m):
        raise ValueError(
            "camera_reference_position_unstable: "
            f"radius={radius:.6f} limit={float(maximum_point_radius_m):.6f}"
        )

    orientation_samples, selected_mode = _choose_orientation_samples(
        window,
        mode=orientation_mode,
        minimum_orientation_quality=minimum_orientation_quality,
        minimum_3d_count=minimum_3d_orientation_samples,
        minimum_2d_count=minimum_2d_orientation_samples,
    )
    if selected_mode == "3d":
        axis, angle = _aggregate_axis(orientation_samples)
        raw_qualities = [sample.orientation_quality for sample in orientation_samples]
        source = orientation_samples[-1].orientation_source
        coordinate_frame = orientation_samples[-1].orientation_coordinate_frame
        semantics = orientation_samples[-1].orientation_semantics
        classes = [_orientation_class(sample.orientation_deg) for sample in orientation_samples]
        sample_angles = [sample.orientation_deg for sample in orientation_samples]
    else:
        axis = None
        angle = axial_mean_deg(
            [_two_d_angle(sample) for sample in orientation_samples]
        )
        raw_qualities = [_two_d_quality(sample) for sample in orientation_samples]
        source = "image_axis_2d"
        coordinate_frame = "camera_image"
        semantics = "axial_angle"
        classes = [_two_d_class(sample) for sample in orientation_samples]
        sample_angles = [_two_d_angle(sample) for sample in orientation_samples]

    spread = max(axial_error_deg(value, angle) for value in sample_angles)
    if spread > float(maximum_orientation_spread_deg):
        raise ValueError(
            "camera_reference_orientation_unstable: "
            f"mode={selected_mode} spread={spread:.3f} "
            f"limit={float(maximum_orientation_spread_deg):.3f}"
        )

    raw_quality = float(median(raw_qualities))
    coherence = max(
        0.0,
        1.0 - spread / max(float(maximum_orientation_spread_deg), 1e-6),
    )
    combined_quality = max(
        0.0,
        min(1.0, raw_quality * (0.5 + 0.5 * coherence)),
    )
    orientation_class = max(sorted(set(classes)), key=classes.count)
    return CameraTeachingReference(
        point_base=center,
        point_radius_m=radius,
        orientation_deg=angle,
        orientation_class=orientation_class,
        orientation_quality=combined_quality,
        orientation_spread_deg=spread,
        localization_quality=float(
            median(sample.localization_quality for sample in window)
        ),
        depth_std_m=float(median(sample.depth_std_m for sample in window)),
        center_std_px=float(median(sample.center_std_px for sample in window)),
        score=float(median(sample.score for sample in window)),
        sample_count=len(window),
        orientation_source=source,
        orientation_coordinate_frame=coordinate_frame,
        orientation_semantics=semantics,
        orientation_axis_base=axis,
        orientation_sample_count=len(orientation_samples),
        orientation_mode=selected_mode,
    )
