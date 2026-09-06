"""Reboot-resilient, vision-led pick/place orchestration for MacRobot.

This node is a drop-in replacement for :mod:`stored_object_pick_node`.  It keeps
its public topics and profile format, while changing the execution policy:

* object-relative grasp skills remain persistent across reboots;
* odometry locations are optional, epoch-scoped hints rather than truth;
* search begins from the current camera view, conditionally backs away from a
  too-close central obstacle, then uses a bounded yaw-only acquisition sweep;
* every base command is a short atomic chunk; perception continues in parallel;
* delayed localized detections are transformed from camera time to the current
  base pose at the next chunk boundary;
* approach uses visual re-observation after small turns/moves and never depends
  on reproducing an exact stored yaw;
* PLACE executes the safe Cartesian reverse of the recorded semantic grasp.

The policy improves robustness without claiming that wheel odometry becomes a
persistent global map.  Whole-room recovery after arbitrary relocation still
requires a stable external reference such as a visual landmark, dock, or SLAM.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
import math
from pathlib import Path
import time
from typing import Any, Deque, Dict, Mapping, Optional, Tuple

import rclpy
from std_msgs.msg import String

from .alignment_core import (
    alignment_errors,
    choose_alignment_action,
    observation_constraint_decision,
    planar_observation,
)
from .object_memory import ObjectMemoryStore, ObjectObservationMemory
from .planner import DetectionSample, StableDetection
from .pose_history import PoseHistory
from .runtime_epoch import RuntimeEpoch, read_host_boot_id
from .search_policy import (
    RotationFirstSearchConfig,
    SearchAction,
    build_rotation_first_search,
    total_motion_budget,
)
from .stored_object_core import (
    OdomPose,
    planar_range_m,
    point_base_to_odom,
    point_odom_to_base,
    wrap_angle_deg,
)
from .stored_object_pick_node import (
    BASE_MOTION_EVENTS,
    TERMINAL_STATES,
    StoredObjectPickNode,
    _as_bool,
    _json_object,
    _point_from_payload,
)


Vector3 = Tuple[float, float, float]


@dataclass(frozen=True)
class PendingDetection:
    payload: Dict[str, Any]
    point_base: Vector3
    source_stamp_sec: float
    published_stamp_sec: float
    received_stamp_sec: float


def _vector3(value: object, field: str) -> Vector3:
    if isinstance(value, Mapping):
        raw = (value.get("x"), value.get("y"), value.get("z"))
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        raw = value
    else:
        raise ValueError(f"{field} must be a three-vector")
    result = tuple(float(item) for item in raw)
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{field} contains a non-finite value")
    return result  # type: ignore[return-value]


class ResilientObjectTaskNode(StoredObjectPickNode):
    """Vision-led pick/place node retaining the existing Gateway contract."""

    def __init__(self) -> None:
        # These values are needed by dynamically dispatched publication/reset
        # helpers while the parent constructor is still running.
        self.task_kind = "pick"
        self.place_reference_object = ""
        self.held_object_name = ""
        self.held_runtime_profile = ""
        self.place_keyframe_profile = ""
        self.place_offset_base: Vector3 = (0.0, 0.12, 0.0)
        self.direct_placement_point: Optional[Vector3] = None
        self.placement_point_base: Optional[Vector3] = None
        self.host_boot_id = read_host_boot_id()
        self.object_memory: Optional[ObjectMemoryStore] = None
        self.pose_history = PoseHistory(nearest_tolerance_sec=8.0)
        self.pending_detections: Deque[PendingDetection] = deque(maxlen=64)
        self.search_actions: Deque[SearchAction] = deque()
        self.search_observe_until = 0.0
        self.search_total_move_m = 0.0
        self.search_total_turn_deg = 0.0
        self.search_corridor_forward_m = 0.0
        self.last_clearance: Dict[str, Any] = {}
        self.latest_detection_metadata: Dict[str, Any] = {}
        self.cached_stable_detection: Optional[StableDetection] = None
        self.last_visual_object_odom: Optional[Vector3] = None
        self.last_visual_wall_sec = 0.0
        self.deadreckon_since_visual_m = 0.0
        self.require_fresh_after_turn = False
        self.reobserve_not_before = 0.0
        self.align_wait_started = 0.0
        self.motion_started_wall_sec = 0.0
        self.pending_detection_drop_count = 0
        self.location_hint_state = "missing"
        self.location_hint_reason = ""
        self.next_state_heartbeat_monotonic = 0.0
        self._resilient_ready = False

        super().__init__()

        self.pose_history = PoseHistory(
            nearest_tolerance_sec=float(
                self.get_parameter("pose_history_stationary_tolerance_sec").value
            )
        )
        memory_path = str(self.get_parameter("object_memory_file").value)
        try:
            self.object_memory = ObjectMemoryStore(memory_path)
        except Exception as error:
            path = Path(memory_path).expanduser().resolve()
            if path.exists():
                backup = path.with_suffix(path.suffix + f".invalid-{int(time.time())}")
                path.replace(backup)
                self.get_logger().error(
                    f"Invalid object memory moved to {backup}: {error}"
                )
            self.object_memory = ObjectMemoryStore(path)

        self.create_subscription(
            String,
            str(self.get_parameter("forward_clearance_topic").value),
            self._clearance_callback,
            20,
        )
        self._resilient_ready = True
        self._refresh_held_epoch_state()
        self._publish_status(
            "resilient_object_tasks_ready",
            execution_policy="rotation_first_vision_led_replanning",
            object_memory_file=str(self.object_memory.path),
            host_boot_id=self.host_boot_id,
        )
        self.get_logger().info(
            "Resilient object tasks ready: current-view/backoff/yaw search -> visual distance alignment -> pick/place"
        )

    # ------------------------------------------------------------------
    # Parameters and common state
    # ------------------------------------------------------------------
    def _declare_parameters(self) -> None:
        super()._declare_parameters()
        defaults: Dict[str, Any] = {
            "object_memory_file": str(
                Path.home() / "MacRobot" / "data" / "object_memory" / "memory.yaml"
            ),
            "forward_clearance_topic": "/macrobot/perception/forward_clearance",
            "require_depth_clearance": True,
            "clearance_max_age_sec": 0.75,
            "clearance_stop_margin_m": 0.12,
            "search_forward_step_m": 0.0,  # deprecated; forward search is disabled
            "search_forward_steps": 0,  # deprecated; forward search is disabled
            "search_initial_observation_sec": 4.0,
            "search_observation_sec": 3.0,
            "search_close_obstacle_backoff_enabled": True,
            "search_close_obstacle_threshold_m": 0.38,
            "search_close_obstacle_backoff_step_m": 0.04,
            "search_close_obstacle_backoff_steps": 2,
            "search_yaw_step_deg": 10.0,
            "search_yaw_levels": 3,
            "search_max_total_move_m": 0.12,
            "search_max_total_turn_deg": 100.0,
            "use_same_epoch_location_hint": True,
            "location_hint_max_age_sec": 900.0,
            "location_hint_max_bearing_deg": 40.0,
            "location_hint_turn_step_deg": 10.0,
            "resilient_stability_count": 2,
            "delayed_detection_max_age_sec": 8.0,
            "pose_history_stationary_tolerance_sec": 8.0,
            "visual_move_chunk_m": 0.04,
            "visual_turn_chunk_deg": 4.0,
            "visual_reobserve_sec": 0.65,
            "visual_lost_timeout_sec": 8.0,
            "near_visual_handoff_range_m": 0.36,
            "maximum_near_deadreckon_m": 0.10,
            "resilient_alignment_confirmation_count": 1,
            "place_default_offset_base": [0.0, 0.12, 0.0],
            "place_min_horizontal_offset_m": 0.08,
            "place_max_horizontal_offset_m": 0.25,
            "place_max_vertical_offset_m": 0.05,
            "state_heartbeat_sec": 2.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _status_payload(
        self, event: str, ok: bool, details: Mapping[str, Any]
    ) -> Dict[str, Any]:
        payload = super()._status_payload(event, ok, details)
        held = None
        if self.object_memory is not None:
            held = self.object_memory.held_for_epoch(self._current_epoch()).to_mapping()
        payload.update(
            {
                "task": self.task_kind,
                "search_policy": "rotation_first_visual_replanning",
                "location_hint_state": self.location_hint_state,
                "location_hint_reason": self.location_hint_reason,
                "pending_delayed_detections": len(self.pending_detections),
                "held_object": held,
            }
        )
        return payload

    def _reset_action_state(self) -> None:
        super()._reset_action_state()
        self.task_kind = "pick"
        self.place_reference_object = ""
        self.held_object_name = ""
        self.held_runtime_profile = ""
        self.place_keyframe_profile = ""
        self.place_offset_base = tuple(
            float(item)
            for item in self.get_parameter("place_default_offset_base").value
        )  # type: ignore[assignment]
        self.direct_placement_point = None
        self.placement_point_base = None
        self.pose_history.clear()
        self.pending_detections.clear()
        self.search_actions.clear()
        self.search_observe_until = 0.0
        self.search_total_move_m = 0.0
        self.search_total_turn_deg = 0.0
        self.search_corridor_forward_m = 0.0
        self.latest_detection_metadata = {}
        self.cached_stable_detection = None
        self.last_visual_object_odom = None
        self.last_visual_wall_sec = 0.0
        self.deadreckon_since_visual_m = 0.0
        self.require_fresh_after_turn = False
        self.reobserve_not_before = 0.0
        self.align_wait_started = 0.0
        self.motion_started_wall_sec = 0.0
        self.location_hint_state = "missing"
        self.location_hint_reason = ""
        self.next_state_heartbeat_monotonic = 0.0

    def _current_epoch(self) -> RuntimeEpoch:
        return RuntimeEpoch.current(
            self.last_pico_payload,
            host_boot_id=self.host_boot_id,
        )

    def _refresh_held_epoch_state(self) -> None:
        if self.object_memory is None:
            return
        effective = self.object_memory.held_for_epoch(self._current_epoch())
        if self.object_memory.held.state == "holding" and effective.state == "unknown":
            self.object_memory.set_unknown(source="runtime_epoch_changed")

    # ------------------------------------------------------------------
    # Public goals and administration
    # ------------------------------------------------------------------
    def _goal_callback(self, msg: String) -> None:
        try:
            request = _json_object(msg.data)
        except Exception:
            super()._goal_callback(msg)
            return
        task = str(request.get("task", request.get("action", "pick"))).strip().casefold()
        if task in {"place", "put", "place_nextto_object"}:
            self._start_place_goal(request)
            return
        if not self._is_busy():
            self.task_kind = "pick"
        super()._goal_callback(msg)

    def _start_place_goal(self, request: Mapping[str, Any]) -> None:
        request_id = str(
            request.get("request_id", f"stored-place-{int(time.time() * 1000)}")
        )
        reference_object = str(
            request.get("reference_object", request.get("object_name", ""))
        ).strip()
        reference_profile_name = str(
            request.get("reference_profile", request.get("alignment_profile", reference_object))
        ).strip()
        try:
            if self._is_busy():
                if request_id == self.request_id and self.task_kind == "place":
                    self._publish_status(
                        "stored_object_command_acknowledged",
                        command="place",
                        duplicate=True,
                    )
                    return
                raise RuntimeError("another stored-object action is active")

            direct_point = request.get("placement_point_base")
            direct_placement = (
                None
                if direct_point is None
                else _vector3(direct_point, "placement_point_base")
            )
            if not reference_object and direct_placement is None:
                raise ValueError(
                    "reference_object or placement_point_base is required"
                )

            offset_raw = request.get(
                "placement_offset_base",
                request.get("offset_base", self.get_parameter("place_default_offset_base").value),
            )
            offset = _vector3(offset_raw, "placement_offset_base")
            if direct_placement is None:
                horizontal_offset = math.hypot(offset[0], offset[1])
                minimum_offset = max(
                    0.0,
                    float(self.get_parameter("place_min_horizontal_offset_m").value),
                )
                maximum_offset = max(
                    minimum_offset,
                    float(self.get_parameter("place_max_horizontal_offset_m").value),
                )
                maximum_vertical = max(
                    0.0,
                    float(self.get_parameter("place_max_vertical_offset_m").value),
                )
                if not (minimum_offset <= horizontal_offset <= maximum_offset):
                    raise ValueError(
                        "placement horizontal offset must be within "
                        f"[{minimum_offset:.3f}, {maximum_offset:.3f}] m"
                    )
                if abs(offset[2]) > maximum_vertical:
                    raise ValueError(
                        "placement vertical offset exceeds "
                        f"{maximum_vertical:.3f} m"
                    )

            held = (
                self.object_memory.held_for_epoch(self._current_epoch())
                if self.object_memory is not None
                else None
            )
            confirm_held = _as_bool(request.get("confirm_held"), False)
            held_object = str(request.get("held_object", "")).strip()
            requested_keyframes = str(
                request.get("grasp_keyframe_profile", "")
            ).strip()
            if held is not None and held.state == "holding":
                held_object = held_object or held.object_name
                requested_keyframes = requested_keyframes or held.grasp_profile
            elif confirm_held and held_object:
                # Explicit operator confirmation is required after a reboot,
                # because encoder/commanded state cannot prove possession.
                pass
            elif held is not None and held.state == "unknown":
                raise ValueError(
                    "held-object state is unknown after restart; use confirm_held=true "
                    "with held_object before PLACE"
                )
            else:
                raise ValueError("robot is not known to be holding an object")

            held_runtime_name = str(
                request.get("held_runtime_profile", request.get("held_profile", ""))
            ).strip()
            held_runtime = self.profile_store.get(held_runtime_name, held_object)
            held_runtime.validate_for_execution(
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            keyframe_profile = requested_keyframes or held_runtime.grasp_keyframe_profile
            if not keyframe_profile:
                raise ValueError("held object has no semantic keyframe profile")
            self.keyframe_store.reload()
            self.keyframe_store.get(keyframe_profile).validate()

            if direct_placement is None:
                reference_profile = self.profile_store.get(
                    reference_profile_name, reference_object
                )
                reference_profile.validate_for_execution(
                    forward_axis_sign=self.forward_axis_sign,
                    lateral_axis_sign=self.lateral_axis_sign,
                )
            else:
                # Direct placement still needs a non-null profile for inherited
                # safety/time parameters.  The held profile is sufficient.
                reference_profile = held_runtime
                reference_object = reference_object or "direct_placement"
                reference_profile_name = reference_profile.name

            timeout_sec = float(
                request.get("timeout_sec", self.get_parameter("overall_timeout_sec").value)
            )
            if not math.isfinite(timeout_sec) or timeout_sec <= 0.0:
                raise ValueError("timeout_sec must be positive and finite")
            start_finder = _as_bool(
                request.get("start_finder"), direct_placement is None
            )
            rebuild_banks = _as_bool(request.get("rebuild_banks"), False)
        except Exception as error:
            self._publish_command_rejection(
                event="stored_place_rejected",
                legacy_event="place_failed",
                request_id=request_id,
                object_name=reference_object,
                profile=reference_profile_name,
                mode="place",
                execute_pick=False,
                error_code=(
                    "RESOURCE_BUSY" if isinstance(error, RuntimeError) else "INVALID_ARGUMENT"
                ),
                reason=str(error),
            )
            return

        self._reset_action_state()
        self.task_kind = "place"
        self.request_id = request_id
        self.object_name = reference_object
        self.place_reference_object = reference_object
        self.profile_name = reference_profile.name
        self.profile = reference_profile
        self.mode = "place"
        self.execute_pick = False
        self.start_finder_for_goal = start_finder
        self.rebuild_banks_for_goal = rebuild_banks
        self.held_object_name = held_object
        self.held_runtime_profile = held_runtime.name
        self.place_keyframe_profile = keyframe_profile
        self.place_offset_base = offset
        self.direct_placement_point = direct_placement
        self.state = "RUNNING"
        self.phase = "starting"
        self.goal_started = time.monotonic()
        self.goal_deadline = self.goal_started + timeout_sec

        if confirm_held and self.object_memory is not None:
            self.object_memory.set_holding(
                held_object,
                keyframe_profile,
                self._current_epoch(),
                source="operator_confirmation",
            )

        self._publish_status(
            "stored_object_command_acknowledged",
            command="place",
            duplicate=False,
        )
        self._publish_status(
            "stored_place_started",
            reference_object=reference_object,
            held_object=held_object,
            held_keyframe_profile=keyframe_profile,
            placement_offset_base=list(offset),
            direct_placement_point=(
                None if direct_placement is None else list(direct_placement)
            ),
            place_sequence=[
                "PLACE_ABOVE",
                "PLACE_DESCEND",
                "PLACE_RELEASE",
                "PLACE_RETREAT",
            ],
        )
        if direct_placement is not None:
            self.placement_point_base = direct_placement
            self._start_place_preflight()
        else:
            # Do not stow a held object.  Search starts with the current arm in
            # its post-pick LIFT pose and only short base motions are allowed.
            self._request_odom("resilient_search_start")

    def _admin_callback(self, msg: String) -> None:
        try:
            request = _json_object(msg.data)
            action = str(request.get("action", msg.data)).strip().casefold()
        except Exception:
            super()._admin_callback(msg)
            return
        if action not in {
            "memory",
            "memory_status",
            "forget_location",
            "confirm_held",
            "clear_held",
            "held_unknown",
        }:
            super()._admin_callback(msg)
            return
        try:
            assert self.object_memory is not None
            if action in {"memory", "memory_status"}:
                self._publish_status(
                    "object_memory",
                    memory=self.object_memory.to_mapping(),
                    memory_file=str(self.object_memory.path),
                )
            elif action == "forget_location":
                name = str(request.get("object_name", request.get("name", ""))).strip()
                if not name:
                    raise ValueError("object_name is required")
                deleted = self.object_memory.forget(name)
                self._publish_status(
                    "object_location_forgotten" if deleted else "object_location_not_found",
                    deleted,
                    object_name=name,
                )
            elif action == "confirm_held":
                name = str(request.get("object_name", "")).strip()
                profile = str(
                    request.get("grasp_keyframe_profile", request.get("profile", ""))
                ).strip()
                if not name or not profile:
                    raise ValueError(
                        "object_name and grasp_keyframe_profile are required"
                    )
                self.object_memory.set_holding(
                    name, profile, self._current_epoch(), source="operator_confirmation"
                )
                self._publish_status(
                    "held_object_confirmed",
                    object_name=name,
                    grasp_keyframe_profile=profile,
                )
            elif action == "clear_held":
                self.object_memory.set_empty(source="operator_clear")
                self._publish_status("held_object_cleared")
            else:
                self.object_memory.set_unknown(source="operator_mark_unknown")
                self._publish_status("held_object_marked_unknown")
        except Exception as error:
            self._publish_status("object_memory_admin_failed", False, error=str(error))

    # ------------------------------------------------------------------
    # Perception and delayed-result compensation
    # ------------------------------------------------------------------
    def _clearance_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if isinstance(payload, dict) and payload.get("event") == "forward_clearance":
            self.last_clearance = dict(payload)

    def _parse_detection(self, msg: String) -> Optional[PendingDetection]:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return None
        if not isinstance(payload, dict) or payload.get("event") != "localized_object":
            return None
        if str(payload.get("object_name", "")).strip().casefold() != self.object_name.casefold():
            return None
        point = _point_from_payload(payload.get("point_base"))
        if point is None:
            return None
        now = time.time()
        try:
            source = float(payload.get("stamp_sec", now) or now)
            published = float(payload.get("published_at_sec", now) or now)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(source) or source <= 0.0:
            source = published if published > 0.0 else now
        if not math.isfinite(published) or published <= 0.0:
            published = now
        return PendingDetection(dict(payload), point, source, published, now)

    def _detection_callback(self, msg: String) -> None:
        if self.mode.startswith("record") or self.phase == "record_wait_detection":
            super()._detection_callback(msg)
            return
        if not self._is_busy() or self.task_kind not in {"pick", "place"}:
            return
        if self.phase not in {
            "search",
            "align",
            "align_settle",
            "resilient_search_move",
            "resilient_search_turn",
            "resilient_approach_move",
            "resilient_approach_turn",
        }:
            return
        detection = self._parse_detection(msg)
        if detection is None:
            return
        self._mark_identity_confirmed("localized_object")
        if self.base_active:
            self.pending_detections.append(detection)
            return
        self._ingest_detection(detection)

    def _robot_moved_since(self, wall_sec: float) -> bool:
        return any(segment.end_wall_sec >= wall_sec for segment in self.pose_history.segments)

    def _ingest_detection(self, detection: PendingDetection) -> bool:
        now = time.time()
        age = max(0.0, now - detection.source_stamp_sec)
        maximum_age = max(
            0.1, float(self.get_parameter("delayed_detection_max_age_sec").value)
        )
        if age > maximum_age:
            self.pending_detection_drop_count += 1
            return False

        point = detection.point_base
        compensated = False
        if self._robot_moved_since(detection.source_stamp_sec):
            point_now = self.pose_history.compensate_point(
                point,
                capture_wall_sec=detection.source_stamp_sec,
                current_pose=self.last_odom,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            if point_now is None:
                self.pending_detection_drop_count += 1
                return False
            point = point_now
            compensated = True

        payload = detection.payload
        localization = payload.get("localization", {})
        orientation = payload.get("orientation", {})
        if not isinstance(localization, Mapping):
            localization = {}
        if not isinstance(orientation, Mapping):
            orientation = {}
        try:
            sample = DetectionSample(
                stamp_sec=now,
                object_name=self.object_name,
                score=float(payload.get("score", 0.0) or 0.0),
                point_base=point,
                source=str(payload.get("source", "")),
                localization_method=str(localization.get("method", "")),
                localization_quality=float(localization.get("quality", 0.0) or 0.0),
                center_std_px=float(payload.get("center_std_px", 0.0) or 0.0),
                depth_std_m=float(payload.get("depth_std_m", 0.0) or 0.0),
                orientation_deg=float(orientation.get("angle_deg", 0.0) or 0.0),
                orientation_class=str(orientation.get("class", "unknown")),
                orientation_quality=float(orientation.get("quality", 0.0) or 0.0),
            )
        except (TypeError, ValueError):
            return False
        if not all(
            math.isfinite(value)
            for value in (
                sample.score,
                *sample.point_base,
                sample.localization_quality,
                sample.center_std_px,
                sample.depth_std_m,
                sample.orientation_deg,
                sample.orientation_quality,
            )
        ):
            return False
        self._mark_localized_progress()
        self.last_object_point = point
        self.latest_detection_metadata = {
            "source_stamp_sec": detection.source_stamp_sec,
            "received_stamp_sec": detection.received_stamp_sec,
            "latency_sec": age,
            "compensated_for_motion": compensated,
            "payload": payload,
        }
        self.filter.add(sample)
        if compensated:
            self._publish_status(
                "delayed_detection_retargeted",
                source_stamp_sec=detection.source_stamp_sec,
                result_latency_sec=age,
                compensated_point_base=list(point),
                current_odom=(None if self.last_odom is None else self.last_odom.to_mapping()),
            )
        return True

    def _process_pending_detections(self) -> None:
        if not self.pending_detections:
            return
        pending = list(self.pending_detections)
        self.pending_detections.clear()
        accepted = 0
        for item in pending:
            accepted += int(self._ingest_detection(item))
        self._publish_status(
            "motion_boundary_perception_processed",
            queued=len(pending),
            accepted=accepted,
            dropped=len(pending) - accepted,
            policy="short_motion_atomic_then_replan",
        )

    def _stable_detection(self):
        if self.mode.startswith("record") or self.phase == "record_wait_detection":
            return super()._stable_detection()
        if self.profile is None:
            return None
        alignment = self.profile.alignment
        minimum_count = min(
            alignment.stability_count,
            max(1, int(self.get_parameter("resilient_stability_count").value)),
        )
        return self.filter.stable(
            now_sec=time.time(),
            object_name=self.object_name,
            minimum_score=alignment.minimum_score,
            minimum_count=minimum_count,
            window_sec=max(alignment.stability_window_sec, 2.0),
            radius_m=alignment.stability_radius_m,
            minimum_localization_quality=alignment.minimum_localization_quality,
            maximum_depth_std_m=alignment.maximum_depth_std_m,
            maximum_center_std_px=alignment.maximum_center_std_px,
            required_orientation_class=(
                alignment.reference_orientation_class
                if alignment.require_orientation_match
                else ""
            ),
            minimum_orientation_quality=alignment.minimum_orientation_quality,
        )

    # ------------------------------------------------------------------
    # Search: current view, conditional close-obstacle backoff, then yaw sweep
    # ------------------------------------------------------------------
    def _after_stow(self) -> None:
        self._request_odom("resilient_search_start")

    def _start_resilient_search(self) -> None:
        assert self.profile is not None
        self.filter.clear()
        self.phase = "search"
        now = time.monotonic()
        timeout = (
            float(self.get_parameter("visible_test_timeout_sec").value)
            if self.mode == "visible_test"
            else float(self.get_parameter("full_search_timeout_sec").value)
        )
        self.phase_deadline = min(self.goal_deadline, now + timeout)
        self.search_total_move_m = 0.0
        self.search_total_turn_deg = 0.0
        self.search_corridor_forward_m = 0.0
        self.search_observe_until = 0.0

        config = RotationFirstSearchConfig(
            initial_observation_sec=float(
                self.get_parameter("search_initial_observation_sec").value
            ),
            observation_sec=max(
                float(self.get_parameter("search_observation_sec").value),
                float(
                    self.get_parameter("search_post_turn_detection_wait_sec").value
                ),
            ),
            backoff_step_m=min(
                0.04,
                max(
                    0.0,
                    float(
                        self.get_parameter(
                            "search_close_obstacle_backoff_step_m"
                        ).value
                    ),
                ),
            ),
            backoff_steps=min(
                2,
                max(
                    0,
                    int(
                        self.get_parameter(
                            "search_close_obstacle_backoff_steps"
                        ).value
                    ),
                ),
            ),
            yaw_step_deg=min(
                10.0,
                max(
                    0.0,
                    float(self.get_parameter("search_yaw_step_deg").value),
                ),
            ),
            yaw_levels=int(self.get_parameter("search_yaw_levels").value),
            include_conditional_backoff=bool(
                self.get_parameter("search_close_obstacle_backoff_enabled").value
            ),
        )
        actions = list(build_rotation_first_search(config))

        self.location_hint_state = "missing"
        self.location_hint_reason = "no_location_memory"
        hint_point = None
        if (
            self.object_memory is not None
            and self.last_odom is not None
            and bool(self.get_parameter("use_same_epoch_location_hint").value)
        ):
            state, reason, record = self.object_memory.classify(
                self.object_name,
                self._current_epoch(),
                current_wall_sec=time.time(),
                maximum_age_sec=float(
                    self.get_parameter("location_hint_max_age_sec").value
                ),
                pico_time_tolerance_ms=int(
                    self.get_parameter("pico_reboot_tolerance_ms").value
                ),
            )
            self.location_hint_state = state
            self.location_hint_reason = reason
            if state == "fresh" and record is not None:
                try:
                    hint_point = point_odom_to_base(
                        record.object_point_odom,
                        self.last_odom,
                        forward_axis_sign=self.forward_axis_sign,
                        lateral_axis_sign=self.lateral_axis_sign,
                    )
                    observation = planar_observation(
                        hint_point,
                        forward_axis_sign=self.forward_axis_sign,
                        lateral_axis_sign=self.lateral_axis_sign,
                    )
                    max_bearing = float(
                        self.get_parameter("location_hint_max_bearing_deg").value
                    )
                    if abs(math.degrees(observation.bearing_rad)) <= max_bearing:
                        turn = max(
                            -float(self.get_parameter("location_hint_turn_step_deg").value),
                            min(
                                float(self.get_parameter("location_hint_turn_step_deg").value),
                                math.degrees(observation.bearing_rad),
                            ),
                        )
                        if abs(turn) >= self.profile.alignment.bearing_tolerance_deg:
                            # Keep the current-view and close-obstacle checks first.
                            # The odometry hint only chooses the first yaw view; it
                            # never authorizes translation toward the old location.
                            first_turn = next(
                                (
                                    index
                                    for index, item in enumerate(actions)
                                    if item.kind == "turn"
                                ),
                                len(actions),
                            )
                            actions.insert(
                                first_turn,
                                SearchAction(
                                    "turn", turn, "same_epoch_hint_view"
                                ),
                            )
                            actions.insert(
                                first_turn + 1,
                                SearchAction(
                                    "observe",
                                    label="same_epoch_hint_observe",
                                    observe_sec=config.observation_sec,
                                ),
                            )
                except Exception as error:
                    self.location_hint_state = "stale"
                    self.location_hint_reason = f"hint_transform_failed:{error}"

        self.search_actions = deque(actions)
        if self.start_finder_for_goal:
            if not self.finder_active:
                self._start_finder(max(1.0, self.goal_deadline - now))
            else:
                self._set_active_target(self.object_name)
        else:
            self._set_active_target(self.object_name)
        move_budget, turn_budget = total_motion_budget(actions)
        self._publish_status(
            "resilient_object_search_started",
            location_hint_state=self.location_hint_state,
            location_hint_reason=self.location_hint_reason,
            location_hint_point_base=(None if hint_point is None else list(hint_point)),
            odom_used_as="same_epoch_optional_hint_only",
            reboot_behavior="discard_coordinates_keep_recognition_and_grasp_skill",
            planned_actions=[action.__dict__ for action in actions],
            planned_move_budget_m=move_budget,
            planned_turn_budget_deg=turn_budget,
        )

    def _try_search_or_align(self) -> None:
        stable = self._stable_detection()
        if stable is not None:
            self._begin_visual_approach(stable)
            return
        now = time.monotonic()
        if self.start_finder_for_goal and not self.finder_target_ready:
            return
        if self.search_observe_until > 0.0 and now < self.search_observe_until:
            return
        self.search_observe_until = 0.0
        if not self.search_actions:
            self._fail(
                "OBJECT_NOT_FOUND",
                reason="bounded rotation-first visual search exhausted",
                search_total_move_m=self.search_total_move_m,
                search_total_turn_deg=self.search_total_turn_deg,
            )
            return
        action = self.search_actions.popleft()
        if action.kind == "observe":
            self.filter.clear()
            self.search_observe_until = now + action.observe_sec
            self._publish_status(
                "search_observation_started",
                label=action.label,
                observation_sec=action.observe_sec,
                remaining_actions=len(self.search_actions),
            )
            return
        if action.kind == "move":
            requested_amount = float(action.amount)
            if action.label.startswith("close_obstacle_backoff"):
                close, reason, clearance = self._close_obstacle_state()
                if not bool(
                    self.get_parameter(
                        "search_close_obstacle_backoff_enabled"
                    ).value
                ):
                    self._publish_status(
                        "search_close_obstacle_backoff_skipped",
                        label=action.label,
                        reason="backoff_disabled",
                    )
                    return
                if not close:
                    self._publish_status(
                        "search_close_obstacle_backoff_skipped",
                        label=action.label,
                        reason=reason,
                        clearance=clearance,
                    )
                    return
                self._publish_status(
                    "search_close_obstacle_backoff_started",
                    label=action.label,
                    requested_move_m=requested_amount,
                    clearance=clearance,
                    rear_clearance_verified=False,
                    safety_note="rear corridor must be kept clear by the operator",
                )
            # A reverse corridor step is only allowed for distance that was
            # actually travelled forward.  This prevents an unsafe blind
            # reverse when a forward probe was skipped by the depth gate.
            if requested_amount < 0.0 and action.label.startswith("corridor_reverse"):
                available = max(0.0, self.search_corridor_forward_m)
                if available <= 1e-4:
                    self._publish_status(
                        "search_reverse_skipped",
                        label=action.label,
                        reason="no_completed_forward_corridor_distance",
                    )
                    return
                requested_amount = -min(abs(requested_amount), available)
            if (
                self.search_total_move_m + abs(requested_amount)
                > float(self.get_parameter("search_max_total_move_m").value)
            ):
                self._fail("SAFETY_BLOCKED", reason="search translation budget exceeded")
                return
            if requested_amount > 0.0 and not self._clearance_allows(requested_amount):
                self._publish_status(
                    "search_forward_probe_skipped",
                    label=action.label,
                    requested_move_m=requested_amount,
                    reason="depth_clearance_unavailable_or_blocked",
                    clearance=self.last_clearance,
                )
                return
            self.search_total_move_m += abs(requested_amount)
            self.filter.clear()
            purpose = (
                "resilient_search_backoff"
                if action.label.startswith("close_obstacle_backoff")
                else "resilient_search_move"
            )
            self._send_move(requested_amount, purpose)
            return
        if (
            self.search_total_turn_deg + abs(action.amount)
            > float(self.get_parameter("search_max_total_turn_deg").value)
        ):
            self._fail("SAFETY_BLOCKED", reason="search turn budget exceeded")
            return
        self.search_total_turn_deg += abs(action.amount)
        self.filter.clear()
        self._send_turn(action.amount, "resilient_search_turn")

    # ------------------------------------------------------------------
    # Short-motion execution and pose-history updates
    # ------------------------------------------------------------------
    def _simulate_end_pose(
        self, start: OdomPose, expected_event: str, amount: float
    ) -> OdomPose:
        if expected_event == "turn_deg_result":
            return OdomPose(
                start.x_m,
                start.y_m,
                wrap_angle_deg(start.yaw_deg + amount),
                True,
                start.pico_time_ms,
            )
        yaw = math.radians(start.yaw_deg)
        return OdomPose(
            start.x_m + amount * math.cos(yaw),
            start.y_m + amount * math.sin(yaw),
            start.yaw_deg,
            True,
            start.pico_time_ms,
        )

    def _start_base_command(
        self,
        command: str,
        expected_event: str,
        purpose: str,
        physical_amount: float,
    ) -> None:
        if not purpose.startswith("resilient_"):
            super()._start_base_command(
                command, expected_event, purpose, physical_amount
            )
            return
        if self.last_odom is None or not self.last_odom.reliable:
            self._fail(
                "POSE_ESTIMATE_UNRELIABLE",
                reason="reliable odometry is required to compensate perception during motion",
            )
            return
        self.base_active = True
        self.base_expected_event = expected_event
        self.base_command = command
        self.base_purpose = purpose
        self.base_physical_amount = physical_amount
        self.phase = purpose
        self.phase_deadline = time.monotonic() + float(
            self.get_parameter("base_motion_timeout_sec").value
        ) + 1.0
        self.motion_started_wall_sec = time.time()
        if self.pose_history.pending:
            self.pose_history.abort_motion()
        self.pose_history.begin_motion(
            purpose,
            self.motion_started_wall_sec,
            self.last_odom,
            physical_amount,
        )
        if self.dry_run_base:
            end = self._simulate_end_pose(
                self.last_odom, expected_event, physical_amount
            )
            self.base_active = False
            self.last_odom = end
            self.pose_history.complete_motion(time.time(), end)
            self.steps[purpose] = {
                "ok": True,
                "event": expected_event,
                "status": "done",
                "dry_run": True,
                "odometry": end.to_mapping(),
            }
            self._process_pending_detections()
            self._after_resilient_motion(purpose, physical_amount)
            return
        self._send_pico(command)
        self._publish_status(
            "base_motion_commanded",
            purpose=purpose,
            physical_amount=physical_amount,
            pico_command=command,
            perception_policy="continue_inference_buffer_until_motion_boundary",
        )

    def _pico_response_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            super()._pico_response_callback(msg)
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        pending_purpose = self.pending_odom_purpose

        if event == "odometry" and pending_purpose == "resilient_search_start":
            self.last_pico_payload = dict(payload)
            odom = self._odom_from_payload(payload)
            self.pending_odom_purpose = ""
            if odom is None or not odom.reliable:
                self._fail(
                    "POSE_ESTIMATE_UNRELIABLE",
                    reason="reliable odometry unavailable at visual-search start",
                )
                return
            self.last_odom = odom
            self.pose_history.add_snapshot(time.time(), odom)
            self._refresh_held_epoch_state()
            self._start_resilient_search()
            return

        if (
            event in BASE_MOTION_EVENTS
            and self.base_active
            and self.base_purpose.startswith("resilient_")
        ):
            self.last_pico_payload = dict(payload)
            if event != self.base_expected_event:
                return
            purpose = self.base_purpose
            self.base_active = False
            self.last_base_response = dict(payload)
            status = str(payload.get("status", ""))
            if self.state == "CANCEL_REQUESTED":
                self.pose_history.abort_motion()
                if status in {
                    "stopped",
                    "done",
                    "timeout",
                    "stall",
                    "encoder_direction_error",
                }:
                    self.cancel_wait_base = False
                    self._try_finish_cancel()
                return
            if payload.get("ok") is not True or status != "done":
                self.pose_history.abort_motion()
                self._fail(
                    "MOTION_EXECUTION_FAILED",
                    reason=f"base motion ended with status={status or 'unknown'}",
                    pico_response=payload,
                )
                return
            odom = self._odom_from_payload(payload)
            if odom is None or not odom.reliable:
                self.pose_history.abort_motion()
                self._fail(
                    "POSE_ESTIMATE_UNRELIABLE",
                    reason="motion result did not include reliable odometry",
                    pico_response=payload,
                )
                return
            self.last_odom = odom
            self.pose_history.complete_motion(time.time(), odom)
            self.steps[purpose] = dict(payload)
            completed_amount = float(self.base_physical_amount)
            self.base_purpose = ""
            self._process_pending_detections()
            self._after_resilient_motion(purpose, completed_amount)
            return

        record_point = self.record_point
        record_stable = self.record_stable_detection
        record_purpose = pending_purpose
        super()._pico_response_callback(msg)
        if event == "odometry":
            odom = self._odom_from_payload(payload)
            if odom is not None:
                self.pose_history.add_snapshot(time.time(), odom)
                self._refresh_held_epoch_state()
                if (
                    record_purpose in {"record", "record_search", "record_grasp"}
                    and self.state == "SUCCEEDED"
                    and record_point is not None
                ):
                    self._remember_observation_point(
                        record_point, odom, record_stable, source="registration"
                    )

    def _after_resilient_motion(self, purpose: str, physical_amount: float) -> None:
        if purpose.startswith("resilient_search"):
            if purpose == "resilient_search_move":
                if physical_amount > 0.0:
                    self.search_corridor_forward_m += physical_amount
                elif physical_amount < 0.0:
                    self.search_corridor_forward_m = max(
                        0.0, self.search_corridor_forward_m - abs(physical_amount)
                    )
            self.phase = "search"
            self.search_observe_until = 0.0
            self._publish_status(
                "search_motion_completed",
                purpose=purpose,
                completed_amount=physical_amount,
                corridor_forward_remaining_m=self.search_corridor_forward_m,
                next="stationary_camera_observation",
            )
            return
        self.phase = "align_settle"
        if purpose == "resilient_approach_turn":
            self.require_fresh_after_turn = True
        assert self.profile is not None
        self.settle_until = time.monotonic() + self.profile.alignment.settle_sec
        self.reobserve_not_before = self.settle_until + float(
            self.get_parameter("visual_reobserve_sec").value
        )
        self._publish_status(
            "visual_servo_motion_completed",
            purpose=purpose,
            next="fresh_detection_or_bounded_near_projection",
        )

    def _close_obstacle_state(self) -> tuple[bool, str, Dict[str, Any]]:
        """Return whether fresh central depth indicates a too-close object.

        This check authorizes only a short configured reverse step.  It does
        not prove rear clearance because MacRobot currently has no rear depth
        sensor; demonstrations must keep the rear corridor clear.
        """

        payload = self.last_clearance
        if not payload or not bool(payload.get("available", False)):
            return False, "forward_clearance_unavailable", dict(payload)
        try:
            stamp = float(payload.get("published_at_sec", 0.0) or 0.0)
            clearance = float(payload.get("clearance_m", 0.0) or 0.0)
        except (TypeError, ValueError):
            return False, "forward_clearance_invalid", dict(payload)
        age = time.time() - stamp
        if not math.isfinite(age) or age < -1.0 or age > float(
            self.get_parameter("clearance_max_age_sec").value
        ):
            return False, "forward_clearance_stale", {**dict(payload), "age_sec": age}
        threshold = max(
            0.0,
            float(
                self.get_parameter("search_close_obstacle_threshold_m").value
            ),
        )
        close = math.isfinite(clearance) and clearance > 0.0 and clearance < threshold
        return close, ("close_obstacle" if close else "front_not_close"), {
            **dict(payload),
            "age_sec": age,
            "threshold_m": threshold,
        }

    def _clearance_allows(self, forward_distance_m: float) -> bool:
        if forward_distance_m <= 0.0:
            return True
        if not bool(self.get_parameter("require_depth_clearance").value):
            return True
        payload = self.last_clearance
        if not payload or not bool(payload.get("available", False)):
            return False
        try:
            stamp = float(payload.get("published_at_sec", 0.0) or 0.0)
            clearance = float(payload.get("clearance_m", 0.0) or 0.0)
        except (TypeError, ValueError):
            return False
        if time.time() - stamp > float(
            self.get_parameter("clearance_max_age_sec").value
        ):
            return False
        required = float(forward_distance_m) + float(
            self.get_parameter("clearance_stop_margin_m").value
        )
        return math.isfinite(clearance) and clearance >= required

    # ------------------------------------------------------------------
    # Visual-servo approach with only bounded near dead reckoning
    # ------------------------------------------------------------------
    def _begin_visual_approach(self, stable: StableDetection) -> None:
        assert self.profile is not None
        self.cached_stable_detection = stable
        self.filter.clear()
        self.phase = "align"
        self.align_wait_started = time.monotonic()
        self.aligned_confirmations = 0
        self._update_visual_anchor(stable)
        self._publish_status(
            "visual_servo_approach_started",
            point_base=list(stable.point_base),
            finder_kept_active=self.finder_active,
            exact_stored_yaw_required=False,
            bearing_corrected_before_translation=True,
            move_chunk_m=float(self.get_parameter("visual_move_chunk_m").value),
            turn_chunk_deg=float(self.get_parameter("visual_turn_chunk_deg").value),
        )

    def _update_visual_anchor(self, stable: StableDetection) -> None:
        self.last_object_point = stable.point_base
        self.last_visual_wall_sec = time.time()
        self.deadreckon_since_visual_m = 0.0
        self.require_fresh_after_turn = False
        if self.last_odom is not None and self.last_odom.reliable:
            try:
                self.last_visual_object_odom = point_base_to_odom(
                    stable.point_base,
                    self.last_odom,
                    forward_axis_sign=self.forward_axis_sign,
                    lateral_axis_sign=self.lateral_axis_sign,
                )
                self._remember_observation_point(
                    stable.point_base,
                    self.last_odom,
                    stable,
                    source="visual_servo",
                )
            except Exception as error:
                self.get_logger().warning(f"Could not update object memory: {error}")

    def _remember_observation_point(
        self,
        point_base: Vector3,
        odom: OdomPose,
        stable: Optional[StableDetection],
        *,
        source: str,
    ) -> None:
        if self.object_memory is None or not odom.reliable:
            return
        object_odom = point_base_to_odom(
            point_base,
            odom,
            forward_axis_sign=self.forward_axis_sign,
            lateral_axis_sign=self.lateral_axis_sign,
        )
        metadata = self.latest_detection_metadata
        source_stamp = float(metadata.get("source_stamp_sec", time.time()))
        score = stable.score if stable is not None else 0.0
        quality = stable.localization_quality if stable is not None else 0.0
        depth_std = stable.depth_std_m if stable is not None else 0.0
        confidence = max(0.0, min(1.0, 0.5 * score + 0.5 * quality))
        self.object_memory.remember(
            ObjectObservationMemory(
                object_name=self.object_name,
                object_point_odom=object_odom,
                observer_pose_odom=odom,
                source_stamp_sec=source_stamp,
                recorded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                epoch=self._current_epoch(),
                score=max(0.0, min(1.0, score)),
                localization_quality=max(0.0, min(1.0, quality)),
                depth_std_m=max(0.0, depth_std),
                confidence=confidence,
                source=source,
            )
        )

    def _predicted_point(self) -> Optional[Vector3]:
        if self.last_visual_object_odom is None or self.last_odom is None:
            return None
        try:
            return point_odom_to_base(
                self.last_visual_object_odom,
                self.last_odom,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
        except Exception:
            return None

    def _try_alignment_step(self) -> None:
        if self.profile is None:
            return
        now = time.monotonic()
        stable = self._stable_detection()
        fresh_visual = stable is not None
        if stable is None and self.cached_stable_detection is not None:
            stable = self.cached_stable_detection
            self.cached_stable_detection = None
            fresh_visual = True
        if stable is not None:
            point = stable.point_base
            constraint = observation_constraint_decision(
                self.profile.alignment,
                localization_quality=stable.localization_quality,
                depth_std_m=stable.depth_std_m,
                center_std_px=stable.center_std_px,
                orientation_deg=stable.orientation_deg,
                orientation_class=stable.orientation_class,
                orientation_quality=stable.orientation_quality,
            )
            if constraint.action == "reject":
                self._fail("TARGET_NOT_GRASPABLE", reason=constraint.reason)
                return
            self._update_visual_anchor(stable)
            self.filter.clear()
        else:
            if now < self.reobserve_not_before:
                return
            if self.last_visual_wall_sec <= 0.0 or (
                time.time() - self.last_visual_wall_sec
                > float(self.get_parameter("visual_lost_timeout_sec").value)
            ):
                self._fail(
                    "OBJECT_LOST",
                    reason="no fresh or compensatable visual observation during approach",
                )
                return
            if self.require_fresh_after_turn:
                # Tracked-base yaw is floor-dependent.  A turn may change the
                # camera view, but its odometry result is never trusted to
                # authorize a following translation without a new visual point.
                return
            point = self._predicted_point()
            if point is None:
                return
            if self.deadreckon_since_visual_m > float(
                self.get_parameter("maximum_near_deadreckon_m").value
            ):
                self._fail(
                    "POSE_ESTIMATE_UNRELIABLE",
                    reason="near-range visual handoff translation budget exceeded",
                )
                return

        self.last_object_point = point
        try:
            errors = alignment_errors(
                point,
                self.profile.alignment.reference_point_base,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            decision = choose_alignment_action(errors, self.profile.alignment)
        except Exception as error:
            self._fail("TARGET_NOT_GRASPABLE", reason=str(error))
            return
        self.last_errors = errors
        self._publish_status(
            "visual_servo_observation",
            point_base=list(point),
            fresh_visual=fresh_visual,
            deadreckon_since_visual_m=self.deadreckon_since_visual_m,
            errors=self._error_mapping(errors),
            decision={
                "action": decision.action,
                "amount": decision.amount,
                "reason": decision.reason,
            },
        )
        if decision.action == "reject":
            self._fail("TARGET_NOT_GRASPABLE", reason=decision.reason)
            return
        if decision.action == "aligned":
            self.aligned_confirmations += 1
            required = max(
                1,
                int(
                    self.get_parameter(
                        "resilient_alignment_confirmation_count"
                    ).value
                ),
            )
            if self.aligned_confirmations >= required:
                self._alignment_complete()
            return

        self.aligned_confirmations = 0
        self.alignment_iterations += 1
        if self.alignment_iterations > self.profile.alignment.max_iterations:
            self._fail("ALIGNMENT_TIMEOUT", reason="visual servo iteration limit")
            return

        if decision.action == "turn":
            # A turn based only on dead reckoning amplifies the floor-dependent
            # yaw error.  Wait for a new camera result instead.
            if not fresh_visual:
                return
            amount = max(
                -float(self.get_parameter("visual_turn_chunk_deg").value),
                min(
                    float(self.get_parameter("visual_turn_chunk_deg").value),
                    decision.amount,
                ),
            )
            if self.total_turn_deg + abs(amount) > self.profile.alignment.max_total_turn_deg:
                self._fail("SAFETY_BLOCKED", reason="visual-servo turn budget exceeded")
                return
            self.total_turn_deg += abs(amount)
            self.filter.clear()
            self._send_turn(amount, "resilient_approach_turn")
            return

        amount = max(
            -float(self.get_parameter("visual_move_chunk_m").value),
            min(float(self.get_parameter("visual_move_chunk_m").value), decision.amount),
        )
        current_range = planar_range_m(
            point,
            forward_axis_sign=self.forward_axis_sign,
            lateral_axis_sign=self.lateral_axis_sign,
        )
        if not fresh_visual and current_range > float(
            self.get_parameter("near_visual_handoff_range_m").value
        ):
            return
        if amount > 0.0 and not self._clearance_allows(amount):
            self._fail(
                "SAFETY_BLOCKED",
                reason="forward visual-servo chunk blocked by aligned-depth clearance",
                clearance=self.last_clearance,
            )
            return
        if self.total_move_m + abs(amount) > self.profile.alignment.max_total_move_m:
            self._fail("SAFETY_BLOCKED", reason="visual-servo translation budget exceeded")
            return
        if not fresh_visual and (
            self.deadreckon_since_visual_m + abs(amount)
            > float(self.get_parameter("maximum_near_deadreckon_m").value)
        ):
            self._fail(
                "POSE_ESTIMATE_UNRELIABLE",
                reason="near-range dead-reckoning budget would be exceeded",
            )
            return
        self.total_move_m += abs(amount)
        self.deadreckon_since_visual_m += abs(amount)
        self.filter.clear()
        self._send_move(amount, "resilient_approach_move")

    # ------------------------------------------------------------------
    # Pick/place terminal manipulation
    # ------------------------------------------------------------------
    def _alignment_complete(self) -> None:
        if self.task_kind != "place":
            super()._alignment_complete()
            return
        self._cancel_finder("place_reference_aligned")
        self._clear_active_target()
        if self.last_object_point is None:
            self._fail("OBJECT_LOST", reason="reference object point unavailable for PLACE")
            return
        self.steps["alignment"] = {
            "iterations": self.alignment_iterations,
            "errors": self._error_mapping(self.last_errors),
            "reference_point_base": list(self.last_object_point),
        }
        self.placement_point_base = tuple(
            self.last_object_point[index] + self.place_offset_base[index]
            for index in range(3)
        )  # type: ignore[assignment]
        self._publish_status(
            "place_target_resolved",
            reference_object=self.place_reference_object,
            reference_point_base=list(self.last_object_point),
            placement_offset_base=list(self.place_offset_base),
            placement_point_base=list(self.placement_point_base),
        )
        self._start_place_preflight()

    def _start_place_preflight(self) -> None:
        if self.placement_point_base is None:
            self._fail("INVALID_ARGUMENT", reason="placement point is unavailable")
            return
        self.phase = "place_preflight"
        self.keyframe_command_id = f"stored-place-preflight-{self.request_id}"
        self.keyframe_preflight_only = True
        self.arm_active = True
        self.phase_deadline = self.goal_deadline
        self._publish_json(
            self.keyframe_command_pub,
            {
                "action": "preflight_place",
                "command_id": self.keyframe_command_id,
                "profile": self.place_keyframe_profile,
                "object_name": self.held_object_name,
                "object_point_base": list(self.placement_point_base),
            },
        )
        self._publish_status(
            "semantic_place_preflight_started",
            held_object=self.held_object_name,
            grasp_keyframe_profile=self.place_keyframe_profile,
            placement_point_base=list(self.placement_point_base),
        )

    def _start_place_execution(self) -> None:
        assert self.placement_point_base is not None
        self.phase = "place"
        self.keyframe_command_id = f"stored-place-keyframes-{self.request_id}"
        self.keyframe_preflight_only = False
        self.arm_active = True
        self.phase_deadline = self.goal_deadline
        self._publish_json(
            self.keyframe_command_pub,
            {
                "action": "place",
                "command_id": self.keyframe_command_id,
                "profile": self.place_keyframe_profile,
                "object_name": self.held_object_name,
                "object_point_base": list(self.placement_point_base),
            },
        )
        self._publish_status(
            "semantic_place_execution_started",
            reverse_pick_sequence=True,
        )

    def _keyframe_result_callback(self, msg: String) -> None:
        if self.task_kind != "place":
            super()._keyframe_result_callback(msg)
            return
        if not self.keyframe_command_id or self.state in TERMINAL_STATES:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if str(payload.get("command_id", "")) != self.keyframe_command_id:
            return
        event = str(payload.get("event", ""))
        if self.state == "CANCEL_REQUESTED":
            if event in {
                "grasp_keyframe_place_failed",
                "grasp_keyframe_cancel_failed",
            }:
                self.cancel_terminal = "FAILED"
                self.cancel_error_code = "SAFE_STOP_UNCONFIRMED"
            if event in {
                "grasp_keyframe_execution_cancelled",
                "grasp_keyframe_place_failed",
                "grasp_keyframe_cancel_failed",
                "grasp_keyframe_place_preflight_succeeded",
                "grasp_keyframe_place_preflight_failed",
                "grasp_keyframe_command_rejected",
            }:
                self.cancel_wait_arm = False
                self.arm_active = False
                self.keyframe_command_id = ""
                self._try_finish_cancel()
            return
        if event == "grasp_keyframe_place_preflight_succeeded" and payload.get("ok") is True:
            self.arm_active = False
            self.keyframe_command_id = ""
            self.keyframe_preflight_only = False
            self.steps["place_preflight"] = dict(payload)
            self._start_place_execution()
            return
        if event == "grasp_keyframe_place_completed" and payload.get("ok") is True:
            self.arm_active = False
            self.keyframe_command_id = ""
            self.steps["place"] = dict(payload)
            self._succeed()
            return
        if event in {
            "grasp_keyframe_place_preflight_failed",
            "grasp_keyframe_place_failed",
            "grasp_keyframe_command_rejected",
        } or payload.get("ok") is False:
            self.arm_active = False
            self.keyframe_command_id = ""
            self._fail(
                "ARM_PATH_UNSAFE" if "preflight" in event else "PLACE_FAILED",
                reason=event or "semantic place failed",
                keyframe_result=payload,
            )

    def _succeed(self) -> None:
        if self.object_memory is not None:
            if self.task_kind == "place":
                self.object_memory.set_empty(source="place_result")
            elif self.execute_pick and self.profile is not None:
                self.object_memory.set_holding(
                    self.object_name,
                    self.profile.grasp_keyframe_profile,
                    self._current_epoch(),
                    source="pick_result",
                )
        if self.task_kind != "place":
            super()._succeed()
            return
        self._cancel_finder("stored_place_complete")
        self._clear_active_target()
        self.state = "SUCCEEDED"
        self.phase = "terminal"
        self._publish_result(
            "stored_place_completed",
            True,
            "place_completed",
            held_object=self.held_object_name,
            reference_object=self.place_reference_object,
            placement_point_base=(
                None
                if self.placement_point_base is None
                else list(self.placement_point_base)
            ),
        )
        self._publish_status("stored_place_completed")

    def _try_finish_cancel(self) -> None:
        if self.task_kind != "place":
            super()._try_finish_cancel()
            return
        if self.state != "CANCEL_REQUESTED":
            return
        if self.cancel_wait_base or self.cancel_wait_arm:
            return
        if self.cancel_terminal == "TIMED_OUT":
            self.state = "TIMED_OUT"
            event = "stored_place_timed_out"
        elif self.cancel_terminal == "FAILED":
            self.state = "FAILED"
            event = "stored_place_failed"
        else:
            self.state = "CANCELED"
            event = "stored_place_cancelled"
        self.phase = "terminal"
        self._publish_result(
            event,
            False,
            "place_failed" if self.state != "CANCELED" else "place_cancelled",
            reason=self.cancel_reason,
            error_code=self.cancel_error_code,
            **self.cancel_details,
        )
        self._publish_status(
            event,
            False,
            reason=self.cancel_reason,
            error_code=self.cancel_error_code,
        )

    def _timer_callback(self) -> None:
        heartbeat_interval = max(
            0.0, float(self.get_parameter("state_heartbeat_sec").value)
        )
        heartbeat_now = time.monotonic()
        if (
            heartbeat_interval > 0.0
            and heartbeat_now >= self.next_state_heartbeat_monotonic
        ):
            self.next_state_heartbeat_monotonic = heartbeat_now + heartbeat_interval
            self._publish_status(
                "resilient_state_heartbeat",
                active=self._is_busy(),
                execution_policy="rotation_first_vision_led_replanning",
            )

        # Preserve delayed detections buffered during a short base motion.
        # The parent clears the stability filter at the end of align_settle;
        # doing so would discard exactly the compensated result needed for
        # motion-boundary replanning.
        if (
            self.phase == "align_settle"
            and not self.base_active
            and self.state not in TERMINAL_STATES
        ):
            now = time.monotonic()
            if now >= self.settle_until:
                self.phase = "align"
            return
        if (
            self.task_kind == "place"
            and self.phase in {"place_preflight", "place"}
            and self.state not in TERMINAL_STATES
            and self.goal_deadline > 0.0
            and time.monotonic() >= self.goal_deadline
        ):
            self._request_cancel("PLACE action timeout", terminal="TIMED_OUT")
            return
        super()._timer_callback()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ResilientObjectTaskNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
