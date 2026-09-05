from __future__ import annotations

from dataclasses import dataclass, field
import threading
from typing import Any, Protocol

from .api_types import ObjectId


@dataclass(frozen=True)
class BridgeOutcome:
    success: bool
    error_code: str | None = None
    error_message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    canceled: bool = False
    timed_out: bool = False
    started: bool = True


class HardwareBridge(Protocol):
    def execute_base_move(
        self,
        distance_m: float,
        *,
        speed: int,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome: ...

    def execute_base_turn(
        self,
        angle_deg: float,
        *,
        speed: int,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome: ...

    def stop_base(self, timeout_s: float) -> BridgeOutcome: ...

    def execute_arm_goal(
        self,
        q_rad: tuple[float, float, float],
        *,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome: ...

    def stop_arm(self, timeout_s: float) -> BridgeOutcome: ...

    def execute_align_pick(
        self,
        object_id: ObjectId,
        *,
        alignment_profile: str,
        pick_profile: str,
        execute_pick: bool,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome: ...

    def cancel_align_pick(self) -> None: ...

    def execute_place_nextto(
        self,
        reference_object_id: ObjectId,
        *,
        reference_profile: str,
        held_object_id: ObjectId,
        placement_offset_base: tuple[float, float, float],
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome: ...

    def cancel_place_nextto(self) -> None: ...

    def system_health(self) -> dict[str, Any]: ...


class DryRunBridge:
    """Deterministic bridge used by unit tests and no-hardware validation."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []

    def execute_base_move(self, distance_m, *, speed, timeout_s, cancel_event):
        self.calls.append(("MOVE_BASE", distance_m))
        if cancel_event.is_set():
            return BridgeOutcome(False, "RUN_CANCELED", "cancelled", canceled=True)
        return BridgeOutcome(True, details={"speed": speed, "timeout_s": timeout_s})

    def execute_base_turn(self, angle_deg, *, speed, timeout_s, cancel_event):
        self.calls.append(("TURN_BASE", angle_deg))
        if cancel_event.is_set():
            return BridgeOutcome(False, "RUN_CANCELED", "cancelled", canceled=True)
        return BridgeOutcome(True, details={"speed": speed, "timeout_s": timeout_s})

    def stop_base(self, timeout_s):
        self.calls.append(("STOP_BASE", timeout_s))
        return BridgeOutcome(True)

    def execute_arm_goal(self, q_rad, *, timeout_s, cancel_event):
        self.calls.append(("ARM", q_rad))
        if cancel_event.is_set():
            return BridgeOutcome(False, "RUN_CANCELED", "cancelled", canceled=True)
        return BridgeOutcome(True)

    def stop_arm(self, timeout_s):
        self.calls.append(("STOP_ARM", timeout_s))
        return BridgeOutcome(True)

    def execute_align_pick(
        self,
        object_id,
        *,
        alignment_profile,
        pick_profile,
        execute_pick,
        timeout_s,
        cancel_event,
    ):
        self.calls.append(("PICK" if execute_pick else "ALIGN", object_id.value))
        if cancel_event.is_set():
            return BridgeOutcome(False, "RUN_CANCELED", "cancelled", canceled=True)
        return BridgeOutcome(
            True,
            details={
                "iterations": 0,
                "pick_steps": 5 if execute_pick else 0,
                "alignment_profile": alignment_profile,
                "pick_profile": pick_profile,
                "timeout_s": timeout_s,
            },
        )

    def cancel_align_pick(self):
        self.calls.append(("CANCEL_ALIGN_PICK", None))

    def execute_place_nextto(
        self,
        reference_object_id,
        *,
        reference_profile,
        held_object_id,
        placement_offset_base,
        timeout_s,
        cancel_event,
    ):
        self.calls.append(
            (
                "PLACE",
                {
                    "reference_object": reference_object_id.value,
                    "held_object": held_object_id.value,
                    "reference_profile": reference_profile,
                    "placement_offset_base": tuple(placement_offset_base),
                },
            )
        )
        if cancel_event.is_set():
            return BridgeOutcome(False, "RUN_CANCELED", "cancelled", canceled=True)
        return BridgeOutcome(
            True,
            details={
                "internal_motion_steps": 4,
                "reference_profile": reference_profile,
                "placement_offset_base": list(placement_offset_base),
                "timeout_s": timeout_s,
            },
        )

    def cancel_place_nextto(self):
        self.calls.append(("CANCEL_PLACE", None))

    def system_health(self):
        return {"dry_run": True, "ok": True}
