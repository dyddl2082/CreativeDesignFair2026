from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import math
from pathlib import Path
import tempfile
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import yaml


Vector3 = Tuple[float, float, float]


def _finite_float(value: Any, field: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def _vector3(value: Any, field: str) -> Vector3:
    if isinstance(value, Mapping):
        items = (value.get("x"), value.get("y"), value.get("z"))
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        items = value
    else:
        raise ValueError(f"{field} must be a 3-vector or x/y/z mapping")
    return tuple(_finite_float(item, field) for item in items)  # type: ignore[return-value]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def wrap_angle_rad(value: float) -> float:
    return math.atan2(math.sin(value), math.cos(value))


@dataclass(frozen=True)
class PlanarObservation:
    forward_m: float
    lateral_m: float
    range_m: float
    bearing_rad: float
    height_m: float


@dataclass(frozen=True)
class AlignmentErrors:
    current: PlanarObservation
    reference: PlanarObservation
    bearing_error_rad: float
    range_error_m: float
    height_error_m: float

    @property
    def bearing_error_deg(self) -> float:
        return math.degrees(self.bearing_error_rad)


@dataclass(frozen=True)
class AlignmentDecision:
    action: str
    amount: float = 0.0
    reason: str = ""


@dataclass(frozen=True)
class AlignmentProfile:
    name: str
    object_name: str
    pick_profile: str
    reference_point_base: Vector3
    recorded_at: str
    frame_id: str = "base_link"
    minimum_score: float = 0.0
    stability_count: int = 5
    stability_window_sec: float = 1.5
    stability_radius_m: float = 0.012
    bearing_tolerance_deg: float = 2.0
    range_tolerance_m: float = 0.015
    height_tolerance_m: float = 0.030
    max_turn_step_deg: float = 4.0
    max_move_step_m: float = 0.040
    turn_speed: int = 150
    move_speed: int = 80
    motion_timeout_sec: float = 8.0
    settle_sec: float = 0.45
    max_iterations: int = 20
    max_total_turn_deg: float = 90.0
    max_total_move_m: float = 0.50
    minimum_localization_quality: float = 0.15
    maximum_depth_std_m: float = 0.035
    maximum_center_std_px: float = 20.0
    require_orientation_match: bool = False
    reference_orientation_deg: float = 0.0
    reference_orientation_class: str = "unknown"
    reference_orientation_quality: float = 0.0
    minimum_orientation_quality: float = 0.25
    orientation_tolerance_deg: float = 25.0

    @classmethod
    def from_mapping(
        cls,
        name: str,
        mapping: Mapping[str, Any],
        *,
        defaults: Optional["AlignmentProfile"] = None,
    ) -> "AlignmentProfile":
        base = defaults or cls(
            name=name,
            object_name=str(mapping.get("object_name", name)),
            pick_profile=str(mapping.get("pick_profile", name)),
            reference_point_base=_vector3(
                mapping.get("reference_point_base", (0.0, 0.0, 0.0)),
                "reference_point_base",
            ),
            recorded_at=str(mapping.get("recorded_at", utc_now_iso())),
        )
        kwargs: Dict[str, Any] = {
            "name": str(name),
            "object_name": str(mapping.get("object_name", base.object_name)).strip(),
            "pick_profile": str(mapping.get("pick_profile", base.pick_profile)).strip(),
            "reference_point_base": _vector3(
                mapping.get("reference_point_base", base.reference_point_base),
                "reference_point_base",
            ),
            "recorded_at": str(mapping.get("recorded_at", base.recorded_at)),
            "frame_id": str(mapping.get("frame_id", base.frame_id)),
            "require_orientation_match": bool(
                mapping.get("require_orientation_match", base.require_orientation_match)
            ),
            "reference_orientation_class": str(
                mapping.get("reference_orientation_class", base.reference_orientation_class)
            ).strip() or "unknown",
        }
        float_fields = (
            "minimum_score",
            "stability_window_sec",
            "stability_radius_m",
            "bearing_tolerance_deg",
            "range_tolerance_m",
            "height_tolerance_m",
            "max_turn_step_deg",
            "max_move_step_m",
            "motion_timeout_sec",
            "settle_sec",
            "max_total_turn_deg",
            "max_total_move_m",
            "minimum_localization_quality",
            "maximum_depth_std_m",
            "maximum_center_std_px",
            "reference_orientation_deg",
            "reference_orientation_quality",
            "minimum_orientation_quality",
            "orientation_tolerance_deg",
        )
        for field in float_fields:
            kwargs[field] = _finite_float(mapping.get(field, getattr(base, field)), field)
        int_fields = (
            "stability_count",
            "turn_speed",
            "move_speed",
            "max_iterations",
        )
        for field in int_fields:
            kwargs[field] = int(mapping.get(field, getattr(base, field)))
        profile = cls(**kwargs)
        profile.validate()
        return profile

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("profile name is empty")
        if not self.object_name.strip():
            raise ValueError("object_name is empty")
        if self.frame_id != "base_link":
            raise ValueError("alignment reference must currently use base_link")
        if self.stability_count < 1:
            raise ValueError("stability_count must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        if not (0.0 <= self.minimum_score <= 1.0):
            raise ValueError("minimum_score must be within [0, 1]")
        positive_fields = (
            self.stability_window_sec,
            self.stability_radius_m,
            self.bearing_tolerance_deg,
            self.range_tolerance_m,
            self.height_tolerance_m,
            self.max_turn_step_deg,
            self.max_move_step_m,
            self.motion_timeout_sec,
            self.max_total_turn_deg,
            self.max_total_move_m,
        )
        if any(value <= 0.0 for value in positive_fields):
            raise ValueError("alignment tolerances and limits must be positive")
        if self.settle_sec < 0.0:
            raise ValueError("settle_sec must be non-negative")
        if not (1 <= self.turn_speed <= 255 and 1 <= self.move_speed <= 255):
            raise ValueError("motor speed must be within 1..255")
        if not (0.0 <= self.minimum_localization_quality <= 1.0):
            raise ValueError("minimum_localization_quality must be within [0, 1]")
        if self.maximum_depth_std_m <= 0.0 or self.maximum_center_std_px <= 0.0:
            raise ValueError("localization uncertainty limits must be positive")
        if not (0.0 <= self.minimum_orientation_quality <= 1.0):
            raise ValueError("minimum_orientation_quality must be within [0, 1]")
        if self.orientation_tolerance_deg <= 0.0 or self.orientation_tolerance_deg > 90.0:
            raise ValueError("orientation_tolerance_deg must be within (0, 90]")
        if self.reference_orientation_class not in {
            "unknown", "horizontal", "vertical", "diagonal"
        }:
            raise ValueError("unsupported reference_orientation_class")

    def with_reference(
        self,
        point_base: Vector3,
        *,
        object_name: Optional[str] = None,
        pick_profile: Optional[str] = None,
        orientation_deg: Optional[float] = None,
        orientation_class: Optional[str] = None,
        orientation_quality: Optional[float] = None,
        require_orientation_match: Optional[bool] = None,
    ) -> "AlignmentProfile":
        result = replace(
            self,
            object_name=(object_name or self.object_name).strip(),
            pick_profile=(pick_profile or self.pick_profile).strip(),
            reference_point_base=tuple(float(v) for v in point_base),  # type: ignore[arg-type]
            recorded_at=utc_now_iso(),
            reference_orientation_deg=(
                self.reference_orientation_deg
                if orientation_deg is None
                else float(orientation_deg) % 180.0
            ),
            reference_orientation_class=(
                self.reference_orientation_class
                if orientation_class is None
                else (str(orientation_class).strip() or "unknown")
            ),
            reference_orientation_quality=(
                self.reference_orientation_quality
                if orientation_quality is None
                else float(orientation_quality)
            ),
            require_orientation_match=(
                self.require_orientation_match
                if require_orientation_match is None
                else bool(require_orientation_match)
            ),
        )
        result.validate()
        return result

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "object_name": self.object_name,
            "pick_profile": self.pick_profile,
            "frame_id": self.frame_id,
            "reference_point_base": {
                "x": self.reference_point_base[0],
                "y": self.reference_point_base[1],
                "z": self.reference_point_base[2],
            },
            "recorded_at": self.recorded_at,
            "minimum_score": self.minimum_score,
            "stability_count": self.stability_count,
            "stability_window_sec": self.stability_window_sec,
            "stability_radius_m": self.stability_radius_m,
            "bearing_tolerance_deg": self.bearing_tolerance_deg,
            "range_tolerance_m": self.range_tolerance_m,
            "height_tolerance_m": self.height_tolerance_m,
            "max_turn_step_deg": self.max_turn_step_deg,
            "max_move_step_m": self.max_move_step_m,
            "turn_speed": self.turn_speed,
            "move_speed": self.move_speed,
            "motion_timeout_sec": self.motion_timeout_sec,
            "settle_sec": self.settle_sec,
            "max_iterations": self.max_iterations,
            "max_total_turn_deg": self.max_total_turn_deg,
            "max_total_move_m": self.max_total_move_m,
            "minimum_localization_quality": self.minimum_localization_quality,
            "maximum_depth_std_m": self.maximum_depth_std_m,
            "maximum_center_std_px": self.maximum_center_std_px,
            "require_orientation_match": self.require_orientation_match,
            "reference_orientation_deg": self.reference_orientation_deg,
            "reference_orientation_class": self.reference_orientation_class,
            "reference_orientation_quality": self.reference_orientation_quality,
            "minimum_orientation_quality": self.minimum_orientation_quality,
            "orientation_tolerance_deg": self.orientation_tolerance_deg,
        }


class AlignmentProfileStore:
    SCHEMA = "macrobot.base_alignment/v1"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self._profiles: Dict[str, AlignmentProfile] = {}
        self.reload()

    def reload(self) -> None:
        self._profiles = {}
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as stream:
            root = yaml.safe_load(stream) or {}
        if not isinstance(root, Mapping):
            raise ValueError("alignment profile root must be a mapping")
        schema = str(root.get("schema", self.SCHEMA))
        if schema != self.SCHEMA:
            raise ValueError(f"unsupported alignment profile schema: {schema}")
        profiles = root.get("profiles", {})
        if not isinstance(profiles, Mapping):
            raise ValueError("profiles must be a mapping")
        for name, mapping in profiles.items():
            if not isinstance(mapping, Mapping):
                continue
            self._profiles[str(name)] = AlignmentProfile.from_mapping(str(name), mapping)

    def names(self) -> Tuple[str, ...]:
        return tuple(sorted(self._profiles))

    def get(self, name: str = "", object_name: str = "") -> AlignmentProfile:
        name = name.strip()
        if name and name in self._profiles:
            return self._profiles[name]
        key = object_name.strip().casefold()
        matches = [
            profile
            for profile in self._profiles.values()
            if profile.object_name.casefold() == key
        ]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise KeyError(name or object_name)
        raise KeyError(f"multiple alignment profiles match object {object_name!r}; specify profile")

    def upsert(self, profile: AlignmentProfile) -> None:
        profile.validate()
        self._profiles[profile.name] = profile
        self.save()

    def delete(self, name: str) -> bool:
        if name not in self._profiles:
            return False
        del self._profiles[name]
        self.save()
        return True

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        root = {
            "schema": self.SCHEMA,
            "updated_at": utc_now_iso(),
            "profiles": {
                name: profile.to_mapping()
                for name, profile in sorted(self._profiles.items())
            },
        }
        text = yaml.safe_dump(root, allow_unicode=True, sort_keys=False)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=str(self.path.parent),
            prefix=self.path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as stream:
            stream.write(text)
            temp_path = Path(stream.name)
        temp_path.replace(self.path)

    def mappings(self) -> Dict[str, Dict[str, Any]]:
        return {name: profile.to_mapping() for name, profile in self._profiles.items()}


def planar_observation(
    point_base: Vector3,
    *,
    forward_axis_sign: float = 1.0,
    lateral_axis_sign: float = 1.0,
) -> PlanarObservation:
    if forward_axis_sign == 0.0 or lateral_axis_sign == 0.0:
        raise ValueError("axis signs must be non-zero")
    x, y, z = (float(value) for value in point_base)
    forward = math.copysign(1.0, forward_axis_sign) * x
    lateral = math.copysign(1.0, lateral_axis_sign) * y
    planar_range = math.hypot(forward, lateral)
    if planar_range < 1e-6:
        raise ValueError("object point is too close to the base origin")
    return PlanarObservation(
        forward_m=forward,
        lateral_m=lateral,
        range_m=planar_range,
        bearing_rad=math.atan2(lateral, forward),
        height_m=z,
    )


def alignment_errors(
    current_point_base: Vector3,
    reference_point_base: Vector3,
    *,
    forward_axis_sign: float = 1.0,
    lateral_axis_sign: float = 1.0,
) -> AlignmentErrors:
    current = planar_observation(
        current_point_base,
        forward_axis_sign=forward_axis_sign,
        lateral_axis_sign=lateral_axis_sign,
    )
    reference = planar_observation(
        reference_point_base,
        forward_axis_sign=forward_axis_sign,
        lateral_axis_sign=lateral_axis_sign,
    )
    return AlignmentErrors(
        current=current,
        reference=reference,
        bearing_error_rad=wrap_angle_rad(current.bearing_rad - reference.bearing_rad),
        range_error_m=current.range_m - reference.range_m,
        height_error_m=current.height_m - reference.height_m,
    )



def pico_turn_command_deg(
    physical_left_positive_deg: float,
    *,
    pico_positive_is_right: bool = True,
) -> float:
    """Convert physical yaw convention (left positive) to Pico TURN_DEG."""
    value = float(physical_left_positive_deg)
    return -value if pico_positive_is_right else value


def pico_move_command_cm(
    physical_forward_positive_m: float,
    *,
    pico_positive_is_forward: bool = True,
) -> float:
    """Convert physical forward motion in metres to Pico MOVE_CM."""
    value_cm = 100.0 * float(physical_forward_positive_m)
    return value_cm if pico_positive_is_forward else -value_cm

def axial_orientation_error_deg(current_deg: float, reference_deg: float) -> float:
    """Smallest unsigned error between image-plane axes in degrees."""
    delta = abs((float(current_deg) - float(reference_deg)) % 180.0)
    return min(delta, 180.0 - delta)


def observation_constraint_decision(
    profile: AlignmentProfile,
    *,
    localization_quality: float,
    depth_std_m: float,
    center_std_px: float,
    orientation_deg: float = 0.0,
    orientation_class: str = "unknown",
    orientation_quality: float = 0.0,
) -> AlignmentDecision:
    if float(localization_quality) < profile.minimum_localization_quality:
        return AlignmentDecision("reject", reason="localization_quality_below_threshold")
    if float(depth_std_m) > profile.maximum_depth_std_m:
        return AlignmentDecision("reject", reason="localized_depth_uncertainty_too_high")
    if float(center_std_px) > profile.maximum_center_std_px:
        return AlignmentDecision("reject", reason="localized_center_uncertainty_too_high")
    if profile.require_orientation_match:
        if float(orientation_quality) < profile.minimum_orientation_quality:
            return AlignmentDecision("reject", reason="object_orientation_unreliable")
        if (
            profile.reference_orientation_class != "unknown"
            and str(orientation_class).strip() != profile.reference_orientation_class
        ):
            return AlignmentDecision("reject", reason="object_orientation_class_mismatch")
        if axial_orientation_error_deg(orientation_deg, profile.reference_orientation_deg) > profile.orientation_tolerance_deg:
            return AlignmentDecision("reject", reason="object_orientation_angle_mismatch")
    return AlignmentDecision("ok", reason="observation_constraints_passed")


def choose_alignment_action(
    errors: AlignmentErrors,
    profile: AlignmentProfile,
) -> AlignmentDecision:
    if errors.current.forward_m <= 0.0:
        return AlignmentDecision("reject", reason="object_not_in_front_half_plane")
    if abs(errors.height_error_m) > profile.height_tolerance_m:
        return AlignmentDecision("reject", reason="height_error_not_correctable_by_planar_base")
    if abs(errors.bearing_error_deg) > profile.bearing_tolerance_deg:
        amount = max(
            -profile.max_turn_step_deg,
            min(profile.max_turn_step_deg, errors.bearing_error_deg),
        )
        return AlignmentDecision("turn", amount=amount, reason="bearing_error")
    if abs(errors.range_error_m) > profile.range_tolerance_m:
        amount = max(
            -profile.max_move_step_m,
            min(profile.max_move_step_m, errors.range_error_m),
        )
        return AlignmentDecision("move", amount=amount, reason="range_error")
    return AlignmentDecision("aligned", reason="within_recorded_pose_tolerance")
