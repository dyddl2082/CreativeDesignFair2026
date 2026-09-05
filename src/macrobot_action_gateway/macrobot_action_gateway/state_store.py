from __future__ import annotations

from dataclasses import dataclass
import math
import re
import threading
import time
from typing import Any

from .api_types import (
    EstimateState,
    ObjectId,
    ObjectState,
    ObjectStateResult,
    RobotPosResult,
    RobotSnapshotState,
    StateSource,
)


_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,31}$")


def unix_ms() -> int:
    return int(time.time() * 1000)


def normalize_yaw_deg(value: float) -> float:
    return ((float(value) + 180.0) % 360.0) - 180.0


@dataclass
class _Estimate:
    values: tuple[float, ...] | None
    state: EstimateState
    source: StateSource
    updated_at_unix_ms: int | None


@dataclass
class _ObjectObservation:
    state: ObjectState
    confidence: float | None
    observed_at_unix_ms: int | None
    received_at_unix_ms: int
    raw_event: str


class RobotStateStore:
    def __init__(self) -> None:
        now = unix_ms()
        self._lock = threading.RLock()
        self._base = _Estimate(
            values=(0.0, 0.0, 0.0),
            state=EstimateState.VALID,
            source=StateSource.COMMAND_HISTORY,
            updated_at_unix_ms=now,
        )
        self._arm = _Estimate(
            values=None,
            state=EstimateState.UNAVAILABLE,
            source=StateSource.COMMANDED_STATE,
            updated_at_unix_ms=None,
        )
        self._gripper = _Estimate(
            values=None,
            state=EstimateState.UNAVAILABLE,
            source=StateSource.COMMANDED_STATE,
            updated_at_unix_ms=None,
        )
        self._objects: dict[ObjectId, _ObjectObservation] = {}
        self._perception_status_at_unix_ms: int | None = None
        self._positions: dict[str, tuple[float, float, float]] = {}
        self._arm_primitives: dict[str, tuple[float, float]] = {}
        self._held_object: ObjectId | None = None
        # Fail safe after Gateway restart. The resilient task node publishes a
        # periodic held-object heartbeat and will explicitly synchronize this
        # to empty, holding, or unknown.
        self._held_object_known = False

    # ------------------------------------------------------------------
    # Base estimate
    # ------------------------------------------------------------------
    def base_snapshot(self) -> _Estimate:
        with self._lock:
            return _Estimate(
                self._base.values,
                self._base.state,
                self._base.source,
                self._base.updated_at_unix_ms,
            )

    def mark_base_transient(self) -> None:
        with self._lock:
            if self._base.values is not None:
                self._base.state = EstimateState.TRANSIENT

    def mark_base_unreliable(self) -> None:
        with self._lock:
            self._base.state = EstimateState.UNRELIABLE
            self._base.updated_at_unix_ms = unix_ms()

    def apply_move(self, distance_m: float) -> None:
        with self._lock:
            if self._base.values is None:
                self._base.state = EstimateState.UNRELIABLE
                self._base.updated_at_unix_ms = unix_ms()
                return
            x_m, y_m, yaw_deg = self._base.values
            yaw_rad = math.radians(yaw_deg)
            x_m += float(distance_m) * math.cos(yaw_rad)
            y_m += float(distance_m) * math.sin(yaw_rad)
            self._base.values = (x_m, y_m, yaw_deg)
            self._base.state = EstimateState.VALID
            self._base.updated_at_unix_ms = unix_ms()

    def apply_turn(self, angle_deg: float) -> None:
        with self._lock:
            if self._base.values is None:
                self._base.state = EstimateState.UNRELIABLE
                self._base.updated_at_unix_ms = unix_ms()
                return
            x_m, y_m, yaw_deg = self._base.values
            self._base.values = (x_m, y_m, normalize_yaw_deg(yaw_deg + angle_deg))
            self._base.state = EstimateState.VALID
            self._base.updated_at_unix_ms = unix_ms()

    # ------------------------------------------------------------------
    # Arm / gripper commanded state
    # ------------------------------------------------------------------
    def update_logical_joint_state(
        self,
        arm_lift_deg: float,
        wrist_pitch_deg: float,
        gripper_deg: float,
        *,
        transient: bool = False,
    ) -> None:
        now = unix_ms()
        state = EstimateState.TRANSIENT if transient else EstimateState.VALID
        with self._lock:
            self._arm = _Estimate(
                values=(float(arm_lift_deg), float(wrist_pitch_deg)),
                state=state,
                source=StateSource.COMMANDED_STATE,
                updated_at_unix_ms=now,
            )
            self._gripper = _Estimate(
                values=(float(gripper_deg),),
                state=state,
                source=StateSource.COMMANDED_STATE,
                updated_at_unix_ms=now,
            )

    def mark_arm_transient(self) -> None:
        with self._lock:
            if self._arm.values is not None:
                self._arm.state = EstimateState.TRANSIENT
            if self._gripper.values is not None:
                self._gripper.state = EstimateState.TRANSIENT

    def mark_arm_unreliable(self) -> None:
        now = unix_ms()
        with self._lock:
            self._arm.state = EstimateState.UNRELIABLE
            self._gripper.state = EstimateState.UNRELIABLE
            self._arm.updated_at_unix_ms = now
            self._gripper.updated_at_unix_ms = now

    def arm_values(self) -> tuple[float, float, float] | None:
        with self._lock:
            if self._arm.values is None or self._gripper.values is None:
                return None
            return (
                float(self._arm.values[0]),
                float(self._arm.values[1]),
                float(self._gripper.values[0]),
            )

    # ------------------------------------------------------------------
    # Object perception state
    # ------------------------------------------------------------------
    def update_perception_status(self) -> None:
        with self._lock:
            self._perception_status_at_unix_ms = unix_ms()

    def update_object_result(
        self,
        object_id: ObjectId,
        *,
        event: str,
        confidence: float | None,
        observed_at_unix_ms: int | None,
    ) -> None:
        event_key = event.strip().lower()
        if event_key == "object_found":
            state = ObjectState.VISIBLE
        elif event_key in {
            "object_not_found",
            "object_lost",
            "search_cancelled",
            "search_timed_out",
        }:
            state = ObjectState.NOT_VISIBLE
        elif event_key in {"object_ambiguous", "ambiguous"}:
            state = ObjectState.AMBIGUOUS
        else:
            state = ObjectState.UNKNOWN
        with self._lock:
            self._objects[object_id] = _ObjectObservation(
                state=state,
                confidence=confidence,
                observed_at_unix_ms=observed_at_unix_ms,
                received_at_unix_ms=unix_ms(),
                raw_event=event,
            )

    def object_state(
        self,
        run_id: str,
        object_id: ObjectId,
        *,
        max_age_ms: int,
        perception_health_max_age_ms: int,
    ) -> ObjectStateResult:
        checked = unix_ms()
        with self._lock:
            health_at = self._perception_status_at_unix_ms
            observation = self._objects.get(object_id)
        if health_at is None or checked - health_at > perception_health_max_age_ms:
            return ObjectStateResult(
                run_id=run_id,
                object_id=object_id,
                state=ObjectState.PERCEPTION_UNAVAILABLE,
                confidence=None if observation is None else observation.confidence,
                observed_at_unix_ms=None if observation is None else observation.observed_at_unix_ms,
                checked_at_unix_ms=checked,
                error_code=None,
                error_message=None,
            )
        if observation is None:
            return ObjectStateResult(
                run_id=run_id,
                object_id=object_id,
                state=ObjectState.NOT_VISIBLE,
                confidence=None,
                observed_at_unix_ms=None,
                checked_at_unix_ms=checked,
                error_code=None,
                error_message=None,
            )
        age_anchor = observation.observed_at_unix_ms or observation.received_at_unix_ms
        if checked - age_anchor > max_age_ms:
            state = ObjectState.STALE
        else:
            state = observation.state
        return ObjectStateResult(
            run_id=run_id,
            object_id=object_id,
            state=state,
            confidence=observation.confidence,
            observed_at_unix_ms=observation.observed_at_unix_ms,
            checked_at_unix_ms=checked,
            error_code=None,
            error_message=None,
        )

    # ------------------------------------------------------------------
    # Session stores
    # ------------------------------------------------------------------
    @staticmethod
    def validate_id(value: str) -> bool:
        return bool(_ID_PATTERN.fullmatch(value)) and not value.startswith("__")

    def save_position(self, position_id: str, overwrite: bool) -> str | None:
        if not self.validate_id(position_id):
            return "POSITION_ID_INVALID"
        with self._lock:
            if self._base.values is None or self._base.state != EstimateState.VALID:
                return "POSE_ESTIMATE_UNRELIABLE"
            if position_id in self._positions and not overwrite:
                return "POSITION_ALREADY_EXISTS"
            self._positions[position_id] = tuple(float(v) for v in self._base.values)
        return None

    def get_position(self, position_id: str) -> tuple[float, float, float] | None:
        with self._lock:
            value = self._positions.get(position_id)
            return None if value is None else tuple(value)

    def save_arm_primitive(self, primitive_id: str, overwrite: bool) -> str | None:
        if not self.validate_id(primitive_id):
            return "PRIMITIVE_ID_INVALID"
        with self._lock:
            if self._arm.values is None:
                return "ARM_STATE_UNAVAILABLE"
            if self._arm.state == EstimateState.TRANSIENT:
                return "ARM_STATE_TRANSIENT"
            if self._arm.state != EstimateState.VALID:
                return "ARM_STATE_UNRELIABLE"
            if primitive_id in self._arm_primitives and not overwrite:
                return "PRIMITIVE_ALREADY_EXISTS"
            self._arm_primitives[primitive_id] = (
                float(self._arm.values[0]),
                float(self._arm.values[1]),
            )
        return None

    def get_arm_primitive(self, primitive_id: str) -> tuple[float, float] | None:
        with self._lock:
            value = self._arm_primitives.get(primitive_id)
            return None if value is None else tuple(value)

    # ------------------------------------------------------------------
    # Held object state
    # ------------------------------------------------------------------
    def set_held_object(self, object_id: ObjectId | None, *, known: bool = True) -> None:
        with self._lock:
            self._held_object = object_id
            self._held_object_known = known

    def held_object(self) -> tuple[ObjectId | None, bool]:
        with self._lock:
            return self._held_object, self._held_object_known

    # ------------------------------------------------------------------
    # Public snapshot
    # ------------------------------------------------------------------
    def robot_snapshot(self, run_id: str) -> RobotPosResult:
        captured = unix_ms()
        with self._lock:
            base = self.base_snapshot()
            arm = _Estimate(
                self._arm.values,
                self._arm.state,
                self._arm.source,
                self._arm.updated_at_unix_ms,
            )
            gripper = _Estimate(
                self._gripper.values,
                self._gripper.state,
                self._gripper.source,
                self._gripper.updated_at_unix_ms,
            )

        available = sum(
            estimate.values is not None
            for estimate in (base, arm, gripper)
        )
        if available == 3:
            snapshot_state = RobotSnapshotState.COMPLETE
            error_code = None
            error_message = None
        elif available > 0:
            snapshot_state = RobotSnapshotState.PARTIAL
            error_code = "ROBOT_STATE_PARTIAL"
            error_message = "일부 로봇 상태만 사용할 수 있습니다."
        else:
            snapshot_state = RobotSnapshotState.UNAVAILABLE
            error_code = "ROBOT_STATE_UNAVAILABLE"
            error_message = "로봇 상태 snapshot을 구성할 수 없습니다."

        base_values = base.values or (None, None, None)
        arm_values = arm.values or (None, None)
        gripper_values = gripper.values or (None,)
        return RobotPosResult(
            run_id=run_id,
            snapshot_state=snapshot_state,
            captured_at_unix_ms=captured,
            x_m=base_values[0],
            y_m=base_values[1],
            yaw_deg=base_values[2],
            base_state=base.state,
            base_source=base.source,
            base_updated_at_unix_ms=base.updated_at_unix_ms,
            arm_lift_deg=arm_values[0],
            wrist_pitch_deg=arm_values[1],
            arm_state=arm.state,
            arm_source=arm.source,
            arm_updated_at_unix_ms=arm.updated_at_unix_ms,
            gripper_deg=gripper_values[0],
            gripper_state=gripper.state,
            gripper_source=gripper.source,
            gripper_updated_at_unix_ms=gripper.updated_at_unix_ms,
            error_code=error_code,
            error_message=error_message,
        )

    def debug_snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "base": {
                    "values": self._base.values,
                    "state": self._base.state.value,
                    "updated_at_unix_ms": self._base.updated_at_unix_ms,
                },
                "arm": {
                    "values": self._arm.values,
                    "state": self._arm.state.value,
                    "updated_at_unix_ms": self._arm.updated_at_unix_ms,
                },
                "gripper": {
                    "values": self._gripper.values,
                    "state": self._gripper.state.value,
                    "updated_at_unix_ms": self._gripper.updated_at_unix_ms,
                },
                "positions": dict(self._positions),
                "arm_primitives": dict(self._arm_primitives),
                "held_object": None if self._held_object is None else self._held_object.value,
                "held_object_known": self._held_object_known,
            }
