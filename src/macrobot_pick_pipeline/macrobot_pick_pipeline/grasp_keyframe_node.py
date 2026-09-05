"""Record and execute semantic, object-relative grasp keyframes."""

from __future__ import annotations

import json
import math
from pathlib import Path
import time
from typing import Any, Dict, Optional, Tuple

from ament_index_python.packages import get_package_share_directory
from .serial2r_model_config import build_arm_model
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, String
import yaml

from .grasp_keyframe_core import (
    REQUIRED_STAGES,
    GraspKeyframeProfile,
    SafeRegionLookup,
    SemanticGraspPlan,
    build_semantic_grasp_plan,
    build_semantic_place_plan,
    capture_stage,
)
from .grasp_keyframe_store import GraspKeyframeStore
from .alignment_core import axial_orientation_error_deg
from .planner import Q, Vector3


def _params(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    root = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(root, dict):
        return {}
    for value in root.values():
        if isinstance(value, dict) and isinstance(value.get("ros__parameters"), dict):
            return dict(value["ros__parameters"])
    return dict(root.get("ros__parameters", root)) if isinstance(root, dict) else {}


def _q_close(first: Q, second: Q, tolerance: float = 1e-5) -> bool:
    return all(abs(float(a) - float(b)) <= tolerance for a, b in zip(first, second))


def _point(value: Any) -> Optional[Vector3]:
    if isinstance(value, dict):
        try:
            point = (float(value["x"]), float(value["y"]), float(value["z"]))
        except Exception:
            return None
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        point = tuple(float(item) for item in value)
    else:
        return None
    return point if all(math.isfinite(item) for item in point) else None  # type: ignore[return-value]


class GraspKeyframeNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_grasp_keyframes")
        description_share = Path(get_package_share_directory("macrobot_description"))
        default_kinematics = description_share / "config" / "kinematics.yaml"
        defaults = {
            "command_topic": "/macrobot/grasp_keyframes/command",
            "cancel_topic": "/macrobot/grasp_keyframes/cancel",
            "status_topic": "/macrobot/grasp_keyframes/status",
            "result_topic": "/macrobot/grasp_keyframes/result",
            "localized_detection_topic": "/macrobot/perception/localized_detection",
            "logical_state_topic": "/macrobot/arm/logical_joint_states",
            "joint_goal_topic": "/macrobot/arm/joint_goal",
            "validation_status_topic": "/macrobot/arm/validation_status",
            "bridge_status_topic": "/macrobot/arm/servo_bridge/status",
            "arm_stop_topic": "/macrobot/arm/stop",
            "profile_file": "~/MacRobot/data/grasp_keyframes/profiles.yaml",
            "kinematics_file": str(default_kinematics),
            "safe_region_csv": "",
            "require_safe_region_preflight": True,
            "safe_region_max_distance_rad": 0.06,
            "preflight_interpolation_step_rad": 0.025,
            "detection_max_age_sec": 1.0,
            "minimum_localization_quality": 0.15,
            "maximum_depth_std_m": 0.035,
            "maximum_center_std_px": 20.0,
            "lateral_tolerance_m": 0.020,
            "require_orientation_match": False,
            "auto_require_orientation_quality": 0.65,
            "minimum_orientation_quality": 0.25,
            "orientation_tolerance_deg": 25.0,
            "motion_timeout_sec": 20.0,
            "cancel_confirm_timeout_sec": 4.0,
            "default_settle_sec": 0.10,
            "timer_hz": 20.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        parameters = _params(
            Path(str(self.get_parameter("kinematics_file").value)).expanduser().resolve()
        )
        self.model = build_arm_model(parameters)
        self.store = GraspKeyframeStore(str(self.get_parameter("profile_file").value))
        self.safe_region: Optional[SafeRegionLookup] = None
        safe_path = str(self.get_parameter("safe_region_csv").value).strip()
        if safe_path:
            try:
                self.safe_region = SafeRegionLookup.from_csv(
                    safe_path,
                    max_distance_rad=float(
                        self.get_parameter("safe_region_max_distance_rad").value
                    ),
                )
            except Exception as error:
                if bool(self.get_parameter("require_safe_region_preflight").value):
                    raise RuntimeError(f"safe-region preflight unavailable: {error}") from error
                self.get_logger().warning(f"Safe-region preflight disabled: {error}")

        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 20
        )
        self.result_pub = self.create_publisher(
            String, str(self.get_parameter("result_topic").value), 20
        )
        self.joint_goal_pub = self.create_publisher(
            JointState, str(self.get_parameter("joint_goal_topic").value), 10
        )
        self.stop_pub = self.create_publisher(
            Empty, str(self.get_parameter("arm_stop_topic").value), 10
        )
        self.create_subscription(
            String,
            str(self.get_parameter("command_topic").value),
            self._command_callback,
            20,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("cancel_topic").value),
            self._cancel_callback,
            20,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("localized_detection_topic").value),
            self._detection_callback,
            50,
        )
        self.create_subscription(
            JointState,
            str(self.get_parameter("logical_state_topic").value),
            self._state_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("validation_status_topic").value),
            self._validation_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("bridge_status_topic").value),
            self._bridge_callback,
            50,
        )

        self.current_q: Q = (0.0, 0.0, 0.0)
        self.latest_detection: Optional[dict[str, Any]] = None
        self.state = "IDLE"
        self.command_id = ""
        self.plan: Optional[SemanticGraspPlan] = None
        self.step_index = -1
        self.pending_q: Optional[Q] = None
        self.pending_step = ""
        self.pending_validated = False
        self.motion_deadline = 0.0
        self.next_step_not_before = 0.0
        self.cancel_deadline = 0.0
        self.cancel_reason = ""
        self.last_result_payload: Optional[dict[str, Any]] = None
        self.create_timer(
            1.0 / max(2.0, float(self.get_parameter("timer_hz").value)),
            self._timer_callback,
        )
        self._status("ready")

    def _json_publish(self, publisher, payload: dict[str, Any]) -> None:
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        publisher.publish(message)

    def _status(self, event: str, ok: bool = True, **details: Any) -> None:
        self._json_publish(
            self.status_pub,
            {
                "ok": ok,
                "event": event,
                "state": self.state,
                "command_id": self.command_id,
                "current_q": list(self.current_q),
                **details,
            },
        )

    def _result(self, event: str, ok: bool, **details: Any) -> None:
        payload = {
            "ok": ok,
            "event": event,
            "state": self.state,
            "command_id": self.command_id,
            **details,
        }
        self.last_result_payload = dict(payload)
        self._json_publish(self.result_pub, payload)

    def _state_callback(self, message: JointState) -> None:
        mapping = {name: float(value) for name, value in zip(message.name, message.position)}
        names = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")
        if all(name in mapping and math.isfinite(mapping[name]) for name in names):
            self.current_q = tuple(mapping[name] for name in names)  # type: ignore[assignment]

    def _detection_callback(self, message: String) -> None:
        try:
            payload = json.loads(message.data)
        except Exception:
            return
        if not isinstance(payload, dict) or payload.get("event") != "localized_object":
            return
        point = _point(payload.get("point_base"))
        if point is None:
            return
        payload = dict(payload)
        payload["_point"] = point
        self.latest_detection = payload

    def _fresh_detection(self, object_name: str, direct_point: Optional[Vector3] = None) -> tuple[Vector3, dict[str, Any]]:
        if direct_point is not None:
            return direct_point, {}
        payload = self.latest_detection
        if payload is None:
            raise ValueError("localized_object_unavailable")
        if str(payload.get("object_name", "")).casefold() != object_name.casefold():
            raise ValueError("localized_object_name_mismatch")
        stamp = float(payload.get("stamp_sec", 0.0))
        if stamp <= 0.0 or time.time() - stamp > float(
            self.get_parameter("detection_max_age_sec").value
        ):
            raise ValueError("localized_object_stale")
        localization = payload.get("localization", {})
        quality = float(localization.get("quality", 0.0)) if isinstance(localization, dict) else 0.0
        if quality < float(self.get_parameter("minimum_localization_quality").value):
            raise ValueError("localization_quality_below_threshold")
        depth_std = float(payload.get("depth_std_m", 0.0) or 0.0)
        if depth_std > float(self.get_parameter("maximum_depth_std_m").value):
            raise ValueError("depth_uncertainty_too_high")
        return payload["_point"], payload

    def _command_callback(self, message: String) -> None:
        action = ""
        try:
            data = json.loads(message.data)
            if not isinstance(data, dict):
                raise ValueError("command must be a JSON object")
            action = str(data.get("action", "")).strip().lower()
            incoming_id = str(data.get("command_id", "")).strip()
            if incoming_id and incoming_id == self.command_id:
                if self.state in {"PREFLIGHT", "RUNNING", "CANCEL_REQUESTED"}:
                    self._status(
                        "grasp_keyframe_command_duplicate_running",
                        action=action,
                        duplicate=True,
                    )
                    return
                if self.last_result_payload is not None:
                    self._json_publish(self.result_pub, self.last_result_payload)
                    return
            if action == "capture":
                self._capture(data)
            elif action == "finalize":
                self._finalize(data)
            elif action in {"play", "preflight", "place", "preflight_place"}:
                operation = "place" if action in {"place", "preflight_place"} else "pick"
                execute = action in {"play", "place"}
                self._start_plan(data, execute=execute, operation=operation)
            elif action == "list":
                self._result("grasp_keyframe_profiles", True, profiles=self.store.mappings())
            elif action == "delete":
                deleted = self.store.delete(str(data.get("profile", "")))
                self._result("grasp_keyframe_profile_deleted", deleted)
            elif action == "reload":
                self.store.reload()
                self._result("grasp_keyframe_profiles_reloaded", True)
            elif action in {"stop", "cancel"}:
                self._stop("user_cancel")
            else:
                raise ValueError("unsupported action")
        except Exception as error:
            if action in {"play", "preflight", "place", "preflight_place"} and self.state == "PREFLIGHT":
                self.state = "FAILED"
            self._result("grasp_keyframe_command_rejected", False, reason=str(error))

    def _capture(self, data: dict[str, Any]) -> None:
        profile_name = str(data.get("profile", "")).strip()
        object_name = str(data.get("object_name", profile_name)).strip()
        stage_name = str(data.get("stage", "")).strip().upper()
        if not profile_name or not object_name:
            raise ValueError("profile and object_name are required")
        point: Optional[Vector3] = None
        detection: dict[str, Any] = {}
        if stage_name not in {"OPEN", "CLOSE"}:
            point, detection = self._fresh_detection(object_name, _point(data.get("object_point_base")))
        stage = capture_stage(
            stage_name=stage_name,
            current_q=self.current_q,
            object_point_base=point,
            model=self.model,
            settle_sec=float(data.get("settle_sec", self.get_parameter("default_settle_sec").value)),
        )
        orientation = detection.get("orientation", {}) if isinstance(detection, dict) else {}
        profile = self.store.upsert_stage(
            profile_name=profile_name,
            object_name=object_name,
            stage=stage,
            orientation_deg=float(orientation.get("angle_deg", 0.0)) if isinstance(orientation, dict) else 0.0,
            orientation_class=str(orientation.get("class", "unknown")) if isinstance(orientation, dict) else "unknown",
            orientation_quality=float(orientation.get("quality", 0.0)) if isinstance(orientation, dict) else 0.0,
        )
        self._result(
            "grasp_keyframe_captured",
            True,
            profile=profile_name,
            object_name=object_name,
            stage=stage_name,
            captured_stages=sorted(profile.stages),
            profile_file=str(self.store.path),
        )

    def _finalize(self, data: dict[str, Any]) -> None:
        profile = self.store.get(str(data.get("profile", "")))
        profile.validate()
        self._result(
            "grasp_keyframe_profile_finalized",
            True,
            profile=profile.name,
            stages=list(REQUIRED_STAGES),
            profile_file=str(self.store.path),
        )

    def _start_plan(
        self,
        data: dict[str, Any],
        *,
        execute: bool,
        operation: str = "pick",
    ) -> None:
        if self.state not in {"IDLE", "SUCCEEDED", "FAILED", "CANCELED"}:
            raise ValueError("grasp_keyframe_executor_busy")
        self.command_id = str(data.get("command_id", "")).strip() or (
            f"grasp-keyframes-{int(time.time() * 1000)}"
        )
        self.last_result_payload = None
        self.state = "PREFLIGHT"
        profile = self.store.get(str(data.get("profile", "")))
        profile.validate()
        object_name = str(data.get("object_name", profile.object_name)).strip()
        point, detection = self._fresh_detection(object_name, _point(data.get("object_point_base")))
        require_orientation_match = operation != "place" and (
            bool(self.get_parameter("require_orientation_match").value)
            or profile.reference_orientation_quality
            >= float(self.get_parameter("auto_require_orientation_quality").value)
        )
        if require_orientation_match:
            orientation = detection.get("orientation", {}) if isinstance(detection, dict) else {}
            current_class = str(orientation.get("class", "unknown")) if isinstance(orientation, dict) else "unknown"
            current_quality = float(orientation.get("quality", 0.0)) if isinstance(orientation, dict) else 0.0
            current_angle = float(orientation.get("angle_deg", 0.0)) if isinstance(orientation, dict) else 0.0
            if current_quality < float(self.get_parameter("minimum_orientation_quality").value):
                raise ValueError("object_orientation_unreliable")
            if profile.reference_orientation_class != "unknown" and current_class != profile.reference_orientation_class:
                raise ValueError("object_orientation_class_mismatch")
            if axial_orientation_error_deg(current_angle, profile.reference_orientation_deg) > float(
                self.get_parameter("orientation_tolerance_deg").value
            ):
                raise ValueError("object_orientation_angle_mismatch")
        if operation == "place":
            plan = build_semantic_place_plan(
                self.model,
                profile,
                point,
                self.current_q,
                lateral_tolerance_m=float(
                    self.get_parameter("lateral_tolerance_m").value
                ),
            )
        else:
            plan = build_semantic_grasp_plan(
                self.model,
                profile,
                point,
                self.current_q,
                lateral_tolerance_m=float(
                    self.get_parameter("lateral_tolerance_m").value
                ),
            )
        preflight = self._preflight(plan)
        if not preflight[0]:
            self.state = "FAILED"
            self._result(
                (
                    "grasp_keyframe_place_preflight_failed"
                    if operation == "place"
                    else "grasp_keyframe_preflight_failed"
                ),
                False,
                profile=profile.name,
                failed_stage=preflight[1],
                unsafe_q=(None if preflight[2] is None else list(preflight[2])),
                nearest_safe_distance_rad=preflight[3],
                reason="safe_region_path_rejected",
            )
            return
        plan_mapping = {
            step.name: {
                "q": list(step.q),
                "target_point_base": (
                    None if step.target_point_base is None else list(step.target_point_base)
                ),
            }
            for step in plan.steps
        }
        if not execute:
            self.state = "SUCCEEDED"
            self._result(
                (
                    "grasp_keyframe_place_preflight_succeeded"
                    if operation == "place"
                    else "grasp_keyframe_preflight_succeeded"
                ),
                True,
                operation=operation,
                profile=profile.name,
                object_point_base=list(point),
                steps=plan_mapping,
            )
            return
        self.plan = plan
        self.step_index = 0
        self.state = "RUNNING"
        self._status(
            (
                "grasp_keyframe_place_started"
                if operation == "place"
                else "grasp_keyframe_execution_started"
            ),
            operation=operation,
            profile=profile.name,
            object_point_base=list(point),
            steps=plan_mapping,
        )
        self._send_step()

    def _preflight(self, plan: SemanticGraspPlan):
        required = bool(self.get_parameter("require_safe_region_preflight").value)
        if self.safe_region is None:
            if required:
                raise ValueError("safe_region_preflight_unavailable")
            return True, "", None, 0.0
        return self.safe_region.validate_plan(
            self.current_q,
            plan,
            interpolation_step_rad=float(
                self.get_parameter("preflight_interpolation_step_rad").value
            ),
        )

    def _send_step(self) -> None:
        if self.plan is None or self.step_index >= len(self.plan.steps):
            self.state = "SUCCEEDED"
            operation = self.plan.operation if self.plan else "pick"
            event = (
                "grasp_keyframe_place_completed"
                if operation == "place"
                else "grasp_keyframe_execution_completed"
            )
            self._result(
                event,
                True,
                operation=operation,
                profile=(self.plan.profile_name if self.plan else ""),
                final_q=list(self.current_q),
            )
            self._status(event, operation=operation)
            self.plan = None
            return
        step = self.plan.steps[self.step_index]
        self.pending_q = step.q
        self.pending_step = step.name
        self.pending_validated = False
        self.motion_deadline = time.monotonic() + float(
            self.get_parameter("motion_timeout_sec").value
        )
        goal = JointState()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.name = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
        goal.position = list(step.q)
        self.joint_goal_pub.publish(goal)
        self._status(
            "grasp_keyframe_step_commanded",
            step=step.name,
            step_index=self.step_index,
            q=list(step.q),
        )

    def _validation_callback(self, message: String) -> None:
        if self.state != "RUNNING" or self.pending_q is None:
            return
        try:
            payload = json.loads(message.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if event == "goal_rejected":
            self._fail("arm_goal_rejected", validator=payload)
        elif event == "goal_validated":
            goal = payload.get("goal")
            if isinstance(goal, list) and len(goal) == 3:
                q = tuple(float(value) for value in goal)
                if _q_close(q, self.pending_q):
                    self.pending_validated = True
                    self._status("grasp_keyframe_step_validated", step=self.pending_step)

    def _bridge_callback(self, message: String) -> None:
        try:
            payload = json.loads(message.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if self.state == "CANCEL_REQUESTED":
            if event == "trajectory_stopped":
                self.state = "CANCELED"
                self.pending_q = None
                self.pending_step = ""
                self.plan = None
                self._result(
                    "grasp_keyframe_execution_cancelled",
                    True,
                    reason=self.cancel_reason,
                    stop_confirmed=True,
                )
                self._status(
                    "grasp_keyframe_execution_cancelled",
                    reason=self.cancel_reason,
                    stop_confirmed=True,
                )
            return
        if self.state != "RUNNING" or self.pending_q is None:
            return
        if event in {
            "runtime_interpolation_rejected",
            "defense_in_depth_rejection",
            "pico_error",
            "invalid_validated_goal",
        }:
            self._fail("servo_bridge_error", bridge=payload)
            return
        if event != "trajectory_completed":
            return
        goal = payload.get("goal")
        if isinstance(goal, list) and len(goal) == 3:
            q = tuple(float(value) for value in goal)
            if not _q_close(q, self.pending_q):
                return
        completed = self.pending_step
        self.current_q = self.pending_q
        step = self.plan.steps[self.step_index] if self.plan else None
        self.pending_q = None
        self.pending_step = ""
        self.step_index += 1
        self.next_step_not_before = time.monotonic() + (step.settle_sec if step else 0.0)
        self._status("grasp_keyframe_step_completed", step=completed)

    def _timer_callback(self) -> None:
        now = time.monotonic()
        if self.state == "CANCEL_REQUESTED":
            if now >= self.cancel_deadline:
                self.state = "FAILED"
                self.pending_q = None
                self.pending_step = ""
                self.plan = None
                self._result(
                    "grasp_keyframe_cancel_failed",
                    False,
                    reason="SAFE_STOP_UNCONFIRMED",
                    cancel_reason=self.cancel_reason,
                )
                self._status(
                    "grasp_keyframe_cancel_failed",
                    False,
                    reason="SAFE_STOP_UNCONFIRMED",
                )
            return
        if self.state != "RUNNING":
            return
        if self.pending_q is not None and now >= self.motion_deadline:
            self._fail("grasp_keyframe_motion_timeout")
            return
        if self.pending_q is None and now >= self.next_step_not_before:
            self._send_step()

    def _cancel_callback(self, message: String) -> None:
        self._stop(message.data.strip() or "user_cancel")

    def _stop(self, reason: str) -> None:
        if self.state == "CANCEL_REQUESTED":
            self._status("grasp_keyframe_cancel_already_requested", reason=self.cancel_reason)
            return
        if self.state != "RUNNING":
            self._result("grasp_keyframe_cancel_ignored", True, reason="not_running")
            return
        self.cancel_reason = reason
        if self.pending_q is None:
            # Between keyframes the bridge has already reported the previous
            # trajectory complete, so no physical motion remains to confirm.
            self.state = "CANCELED"
            self.plan = None
            self._result(
                "grasp_keyframe_execution_cancelled",
                True,
                reason=reason,
                stop_confirmed=True,
            )
            self._status(
                "grasp_keyframe_execution_cancelled",
                reason=reason,
                stop_confirmed=True,
            )
            return
        self.state = "CANCEL_REQUESTED"
        self.cancel_deadline = time.monotonic() + float(
            self.get_parameter("cancel_confirm_timeout_sec").value
        )
        self.stop_pub.publish(Empty())
        self._status(
            "grasp_keyframe_cancel_requested",
            reason=reason,
            waiting_for="trajectory_stopped",
        )

    def _fail(self, reason: str, **details: Any) -> None:
        self.stop_pub.publish(Empty())
        operation = self.plan.operation if self.plan is not None else "pick"
        self.state = "FAILED"
        self.pending_q = None
        self.plan = None
        event = (
            "grasp_keyframe_place_failed"
            if operation == "place"
            else "grasp_keyframe_execution_failed"
        )
        self._result(event, False, operation=operation, reason=reason, **details)
        self._status(event, False, operation=operation, reason=reason)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GraspKeyframeNode()
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
