from __future__ import annotations

from collections import deque
import json
import math
from pathlib import Path
import time
from typing import Any, Deque, Dict, Mapping, Optional, Tuple

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, JointState
from std_msgs.msg import Empty, Float64, String
from std_srvs.srv import Trigger
from visualization_msgs.msg import Marker, MarkerArray
import yaml

from macrobot_arm_kinematics.model import ArmGeometry

from .grasp_frame_fit import GeometryReference, fit_grasp_frame
from .planner import DetectionSample, StablePointFilter
from .teach_core import (
    PROFILE_STAGES,
    ProfileDraft,
    RecordedStage,
    Vector3,
    add3,
    derive_pick_profile,
    pick_profile_overlay,
    q3,
    vector3,
)
from .teach_store import AtomicYamlStore, utc_now


Q = Tuple[float, float, float]


def _ros_params(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        root = yaml.safe_load(stream) or {}
    if isinstance(root, Mapping):
        wildcard = root.get("/**", {})
        if isinstance(wildcard, Mapping):
            params = wildcard.get("ros__parameters", {})
            if isinstance(params, Mapping):
                return dict(params)
        for value in root.values():
            if isinstance(value, Mapping):
                params = value.get("ros__parameters", {})
                if isinstance(params, Mapping):
                    return dict(params)
    return {}


def _point_payload(value: Any) -> Optional[Vector3]:
    if not isinstance(value, Mapping):
        return None
    try:
        point = (float(value["x"]), float(value["y"]), float(value["z"]))
    except (KeyError, TypeError, ValueError):
        return None
    return point if all(math.isfinite(item) for item in point) else None


def _q_close(a: Q, b: Q, tolerance: float = 1e-4) -> bool:
    return max(abs(a[index] - b[index]) for index in range(3)) <= tolerance


class CameraTeachNode(Node):
    """Camera-assisted recorder for commissioning menus 5, 6 and 7.

    The node never sends raw Pico / PWM commands. Every test motion is sent to
    ``/macrobot/arm/joint_goal`` and therefore remains behind the existing
    validator, safe-region gate and servo bridge.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_camera_teach")

        description = Path(get_package_share_directory("macrobot_description"))
        package = Path(get_package_share_directory("macrobot_pick_pipeline"))
        default_report = (
            Path.home()
            / "MacRobot"
            / "data"
            / "commissioning"
            / "arm_commissioning_report.yaml"
        )
        default_overlay = (
            Path.home()
            / "MacRobot"
            / "data"
            / "commissioning"
            / "pick_profiles_recorded.yaml"
        )

        self.declare_parameter("command_topic", "/macrobot/pick/teach/command")
        self.declare_parameter("status_topic", "/macrobot/pick/teach/status")
        self.declare_parameter("result_topic", "/macrobot/pick/teach/result")
        self.declare_parameter("marker_topic", "/macrobot/pick/teach/markers")
        self.declare_parameter(
            "localized_detection_topic", "/macrobot/perception/localized_detection"
        )
        self.declare_parameter(
            "camera_info_topic", "/camera/camera/color/camera_info"
        )
        self.declare_parameter("require_camera_health", True)
        self.declare_parameter("camera_health_timeout_sec", 3.0)
        self.declare_parameter(
            "logical_state_topic", "/macrobot/arm/logical_joint_states"
        )
        self.declare_parameter("tool_pose_topic", "/macrobot/arm/tool_pose")
        self.declare_parameter("gripper_gap_topic", "/macrobot/gripper/gap")
        self.declare_parameter("joint_goal_topic", "/macrobot/arm/joint_goal")
        self.declare_parameter(
            "validation_status_topic", "/macrobot/arm/validation_status"
        )
        self.declare_parameter(
            "bridge_status_topic", "/macrobot/arm/servo_bridge/status"
        )
        self.declare_parameter("arm_stop_topic", "/macrobot/arm/stop")
        self.declare_parameter("pick_goal_topic", "/macrobot/pick/goal")
        self.declare_parameter("pick_result_topic", "/macrobot/pick/result")
        self.declare_parameter("active_target_topic", "/macrobot/pick/active_target")
        self.declare_parameter("finder_goal_topic", "/object_finder/goal")
        self.declare_parameter("finder_cancel_topic", "/object_finder/cancel")
        self.declare_parameter(
            "reload_profiles_service", "/macrobot/pick/reload_profiles"
        )

        self.declare_parameter("report_path", str(default_report))
        self.declare_parameter("generated_profile_file", str(default_overlay))
        self.declare_parameter(
            "kinematics_file", str(description / "config" / "kinematics.yaml")
        )
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("use_finder", True)
        self.declare_parameter("allow_motion_commands", True)
        self.declare_parameter("target_min_score", 0.0)
        self.declare_parameter("target_stability_count", 5)
        self.declare_parameter("target_stability_window_sec", 1.5)
        self.declare_parameter("target_stability_radius_m", 0.012)
        self.declare_parameter("target_lock_timeout_sec", 30.0)
        self.declare_parameter("motion_timeout_sec", 25.0)
        self.declare_parameter("timer_rate_hz", 20.0)

        self.base_frame = str(self.get_parameter("base_frame").value)
        self.use_finder = bool(self.get_parameter("use_finder").value)
        self.allow_motion_commands = bool(
            self.get_parameter("allow_motion_commands").value
        )
        self.report = AtomicYamlStore(str(self.get_parameter("report_path").value))
        self.generated_profile_file = Path(
            str(self.get_parameter("generated_profile_file").value)
        ).expanduser().resolve()

        params = _ros_params(
            Path(str(self.get_parameter("kinematics_file").value))
            .expanduser()
            .resolve()
        )
        self.geometry = ArmGeometry(
            pivot_x=float(params.get("pivot_x", 0.02095)),
            pivot_y=float(params.get("pivot_y", 0.06340)),
            pivot_z=float(params.get("pivot_z", 0.064595)),
            main_link_length=float(params.get("main_link_length", 0.10000)),
            tool_offset_x=float(params.get("tool_offset_x", -0.184756)),
            tool_offset_z=float(params.get("tool_offset_z", -0.006000)),
            tool_y=float(params.get("tool_y", 0.064500)),
            gripper_link_length=float(params.get("gripper_link_length", 0.03000)),
            gripper_base_separation=float(
                params.get("gripper_base_separation", 0.01000)
            ),
        )

        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 20
        )
        self.result_pub = self.create_publisher(
            String, str(self.get_parameter("result_topic").value), 20
        )
        self.marker_pub = self.create_publisher(
            MarkerArray, str(self.get_parameter("marker_topic").value), 10
        )
        self.joint_goal_pub = self.create_publisher(
            JointState, str(self.get_parameter("joint_goal_topic").value), 10
        )
        self.stop_pub = self.create_publisher(
            Empty, str(self.get_parameter("arm_stop_topic").value), 10
        )
        self.pick_goal_pub = self.create_publisher(
            String, str(self.get_parameter("pick_goal_topic").value), 10
        )
        self.active_target_pub = self.create_publisher(
            String, str(self.get_parameter("active_target_topic").value), 10
        )
        self.finder_goal_pub = self.create_publisher(
            String, str(self.get_parameter("finder_goal_topic").value), 10
        )
        self.finder_cancel_pub = self.create_publisher(
            String, str(self.get_parameter("finder_cancel_topic").value), 10
        )

        self.create_subscription(
            String,
            str(self.get_parameter("command_topic").value),
            self._command_callback,
            20,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("localized_detection_topic").value),
            self._detection_callback,
            50,
        )
        self.create_subscription(
            CameraInfo,
            str(self.get_parameter("camera_info_topic").value),
            self._camera_info_callback,
            10,
        )
        self.create_subscription(
            JointState,
            str(self.get_parameter("logical_state_topic").value),
            self._state_callback,
            50,
        )
        self.create_subscription(
            PoseStamped,
            str(self.get_parameter("tool_pose_topic").value),
            self._tool_pose_callback,
            50,
        )
        self.create_subscription(
            Float64,
            str(self.get_parameter("gripper_gap_topic").value),
            self._gap_callback,
            20,
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
        self.create_subscription(
            String,
            str(self.get_parameter("pick_result_topic").value),
            self._pick_result_callback,
            20,
        )

        self.reload_client = self.create_client(
            Trigger, str(self.get_parameter("reload_profiles_service").value)
        )

        self.require_camera_health = bool(
            self.get_parameter("require_camera_health").value
        )
        self.camera_last_seen_monotonic = 0.0
        self.camera_frame_id = ""
        self.current_q: Q = (0.0, 0.0, 0.0)
        self.tool_point: Optional[Vector3] = None
        self.gripper_gap_m: Optional[float] = None
        self.filter = StablePointFilter()
        self.active_target = ""
        self.target_lock_command_id = ""
        self.target_lock_started = 0.0
        self.target_lock_timeout = float(
            self.get_parameter("target_lock_timeout_sec").value
        )
        self.locked_target: Optional[Dict[str, Any]] = None
        self.grasp_samples: Deque[Dict[str, Any]] = deque(maxlen=50)
        calibration_section = self.report.section("grasp_frame_calibration")
        saved_samples = calibration_section.get("samples", [])
        if isinstance(saved_samples, list):
            for sample in saved_samples[-50:]:
                if isinstance(sample, Mapping):
                    self.grasp_samples.append(dict(sample))

        self.profile_draft: Optional[ProfileDraft] = None
        profile_section = self.report.section("grasp_profiles")
        raw_draft = profile_section.get("draft")
        if isinstance(raw_draft, Mapping):
            try:
                self.profile_draft = ProfileDraft.from_mapping(raw_draft)
            except Exception as exc:
                self.get_logger().warning(
                    f"Ignoring invalid saved profile draft: {exc}"
                )

        self.pending_motion_q: Optional[Q] = None
        self.pending_motion_label = ""
        self.pending_motion_command_id = ""
        self.pending_motion_started = 0.0
        self.pending_motion_validated = False
        self.pending_pick_command_id = ""
        self.pending_pick_object = ""

        rate = max(2.0, float(self.get_parameter("timer_rate_hz").value))
        self.create_timer(1.0 / rate, self._timer_callback)
        self._status(
            "camera_teach_ready",
            report_path=str(self.report.path),
            generated_profile_file=str(self.generated_profile_file),
            allow_motion_commands=self.allow_motion_commands,
        )

    def _publish_json(self, publisher, payload: Mapping[str, Any]) -> None:
        message = String()
        message.data = json.dumps(dict(payload), ensure_ascii=False)
        publisher.publish(message)

    def _status(self, event: str, ok: bool = True, **details: Any) -> None:
        payload = {
            **details,
            "ok": ok,
            "event": event,
            "current_q": list(self.current_q),
            "active_target": self.active_target,
            "locked_target": self.locked_target,
            "profile_draft": (
                self.profile_draft.object_name if self.profile_draft else ""
            ),
            "camera_ready": self._camera_ready(),
            "camera_frame_id": self.camera_frame_id,
        }
        self._publish_json(self.status_pub, payload)
        if ok:
            self.get_logger().info(json.dumps(payload, ensure_ascii=False))
        else:
            self.get_logger().warning(json.dumps(payload, ensure_ascii=False))

    def _result(
        self,
        command_id: str,
        event: str,
        ok: bool = True,
        **details: Any,
    ) -> None:
        self._publish_json(
            self.result_pub,
            {**details, "ok": ok, "event": event, "command_id": command_id},
        )

    def _command_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
            if not isinstance(payload, dict):
                raise ValueError("teach command must be a JSON object")
            action = str(payload.get("action", "")).strip().lower()
            command_id = str(
                payload.get("command_id", f"teach-{int(time.time() * 1000)}")
            )
            if not action:
                raise ValueError("missing action")
            handler = getattr(self, f"_action_{action}", None)
            if handler is None:
                raise ValueError(f"unsupported action: {action}")
            handler(command_id, payload)
        except Exception as exc:
            command_id = ""
            try:
                command_id = str(payload.get("command_id", ""))  # type: ignore[name-defined]
            except Exception:
                pass
            self._result(command_id, "teach_command_failed", False, error=str(exc))

    def _action_status(self, command_id: str, _: Mapping[str, Any]) -> None:
        snapshot = self.report.snapshot()
        self._result(
            command_id,
            "teach_status",
            report_path=str(self.report.path),
            sections={
                name: (value.get("status") if isinstance(value, Mapping) else None)
                for name, value in snapshot.get("sections", {}).items()
            },
            current_q=list(self.current_q),
            tool_point_base=list(self.tool_point) if self.tool_point else None,
            gripper_gap_m=self.gripper_gap_m,
            locked_target=self.locked_target,
            profile_draft=(self.profile_draft.as_dict() if self.profile_draft else None),
            grasp_sample_count=len(self.grasp_samples),
            camera_ready=self._camera_ready(),
            camera_frame_id=self.camera_frame_id,
            camera_age_sec=(
                max(0.0, time.monotonic() - self.camera_last_seen_monotonic)
                if self.camera_last_seen_monotonic > 0.0
                else None
            ),
            camera_required_for=["grasp_frame_calibration", "grasp_profile"],
            camera_independent_recorder="arm_demo_recorder_node",
        )

    def _action_lock_target(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        if not self._camera_ready():
            raise ValueError(
                "camera workflow unavailable: no recent CameraInfo. "
                "Use arm_demo_recorder_node for camera-independent primitive recording."
            )
        object_name = str(payload.get("object_name", "")).strip()
        if not object_name:
            raise ValueError("object_name is required")
        self.active_target = object_name
        self.target_lock_command_id = command_id
        self.target_lock_started = time.monotonic()
        self.target_lock_timeout = float(
            payload.get(
                "timeout_sec",
                self.get_parameter("target_lock_timeout_sec").value,
            )
        )
        self.locked_target = None
        self.filter.clear()

        target = String()
        target.data = object_name
        self.active_target_pub.publish(target)
        if self.use_finder:
            self._publish_json(
                self.finder_goal_pub,
                {
                    "object_name": object_name,
                    "timeout_sec": float(
                        payload.get(
                            "timeout_sec",
                            self.target_lock_timeout,
                        )
                    ),
                    "continuous": True,
                },
            )
        self._status("target_lock_started", command_id=command_id, object_name=object_name)

    def _action_unlock_target(
        self, command_id: str, _: Mapping[str, Any]
    ) -> None:
        self._cancel_finder("teach_unlock")
        self.active_target = ""
        self.locked_target = None
        self.target_lock_command_id = ""
        self.filter.clear()
        target = String()
        target.data = ""
        self.active_target_pub.publish(target)
        self._result(command_id, "target_unlocked")

    def _action_move_to_q(self, command_id: str, payload: Mapping[str, Any]) -> None:
        q = q3(payload.get("q"), name="move_to_q.q")
        self._start_motion(command_id, q, str(payload.get("label", "teach_move")))

    def _action_capture_grasp_sample(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        target = self._require_locked_target()
        tool = self._require_tool_point()
        contact_offset = vector3(
            payload.get("contact_offset_base", [0.0, 0.0, 0.0]),
            name="contact_offset_base",
        )
        measured = add3(vector3(target["point_base"]), contact_offset)
        sample: Dict[str, Any] = {
            "label": str(payload.get("label", f"sample_{len(self.grasp_samples) + 1}")),
            "q1": self.current_q[0],
            "q2": self.current_q[1],
            "q3": self.current_q[2],
            "measurement_frame": "base_link",
            "measured_x": measured[0],
            "measured_y": measured[1],
            "measured_z": measured[2],
            "measured_gap": self.gripper_gap_m,
            "model_tool_pose": {
                "x": tool[0],
                "y": tool[1],
                "z": tool[2],
            },
            "target": target,
            "contact_offset_base": list(contact_offset),
            "captured_at": utc_now(),
            "notes": str(payload.get("notes", "")),
        }
        self.grasp_samples.append(sample)
        self.report.update_section(
            "grasp_frame_calibration",
            {
                "source": "camera_arm_teach",
                "measurement_method": "camera_locked_calibration_target",
                "samples": list(self.grasp_samples),
            },
            status="in_progress",
        )
        self._publish_teach_markers()
        self._result(
            command_id,
            "grasp_sample_captured",
            sample=sample,
            sample_count=len(self.grasp_samples),
        )

    def _action_clear_grasp_samples(
        self, command_id: str, _: Mapping[str, Any]
    ) -> None:
        self.grasp_samples.clear()
        self.report.update_section(
            "grasp_frame_calibration",
            {
                "source": "camera_arm_teach",
                "measurement_method": "camera_locked_calibration_target",
                "samples": [],
            },
            status="in_progress",
        )
        self._result(command_id, "grasp_samples_cleared")

    def _action_fit_grasp_frame(
        self, command_id: str, _: Mapping[str, Any]
    ) -> None:
        if len(self.grasp_samples) < 3:
            raise ValueError("at least three camera-aligned samples are required")
        reference = GeometryReference(
            pivot_x=self.geometry.pivot_x,
            pivot_z=self.geometry.pivot_z,
            main_link_length=self.geometry.main_link_length,
        )
        fit_samples = [
            {key: value for key, value in sample.items() if value is not None}
            for sample in self.grasp_samples
        ]
        fitted = fit_grasp_frame(fit_samples, reference)
        recommended = {
            key: fitted[key]
            for key in (
                "tool_offset_x",
                "tool_offset_z",
                "gripper_link_length",
                "gripper_base_separation",
            )
            if key in fitted
        }
        self.report.complete_section(
            "grasp_frame_calibration",
            {
                "source": "camera_arm_teach",
                "measurement_method": "camera_locked_calibration_target",
                "reference_geometry": reference.__dict__,
                "samples": list(self.grasp_samples),
                "fit": fitted,
                "recommended_kinematics_parameters": recommended,
                "warning": (
                    "This fit includes camera extrinsic and object-centre error. "
                    "Use a small fixed calibration target and verify in RViz before applying."
                ),
            },
        )
        recommendation_file = self.report.path.parent / "grasp_frame_recommendation.yaml"
        recommendation_file.parent.mkdir(parents=True, exist_ok=True)
        with recommendation_file.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(
                {"recommended_kinematics_parameters": recommended, "fit": fitted},
                stream,
                allow_unicode=True,
                sort_keys=False,
            )
        self._result(
            command_id,
            "grasp_frame_fit_completed",
            recommended_kinematics_parameters=recommended,
            fit=fitted,
            recommendation_file=str(recommendation_file),
        )

    def _action_record_primitive(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        raise ValueError(
            "primitive recording moved to arm_demo_recorder_node / arm_demo_cli"
        )

    def _action_test_primitive(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        raise ValueError(
            "primitive playback moved to arm_demo_recorder_node / arm_demo_cli"
        )

    def _action_start_profile(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        target = self._require_locked_target()
        object_name = str(payload.get("object_name", self.active_target)).strip()
        if not object_name:
            raise ValueError("object_name is required")
        if object_name.casefold() != str(target["object_name"]).casefold():
            raise ValueError("locked target does not match requested object")
        self.profile_draft = ProfileDraft(
            object_name=object_name,
            target_point_base=vector3(target["point_base"]),
            started_at=utc_now(),
            speed_scale=max(
                0.05, min(1.0, float(payload.get("speed_scale", 0.5)))
            ),
            notes=str(payload.get("notes", "")),
        )
        self._save_profile_draft()
        self._result(
            command_id,
            "profile_recording_started",
            draft=self.profile_draft.as_dict(),
        )

    def _action_capture_profile_stage(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        if self.profile_draft is None:
            raise ValueError("start_profile must be called first")
        stage_name = str(payload.get("stage", "")).strip().upper()
        if stage_name not in PROFILE_STAGES:
            raise ValueError(f"unsupported stage: {stage_name}")
        tool = self._require_tool_point()
        target = self.locked_target
        score = None
        if target and str(target.get("object_name", "")).casefold() == self.profile_draft.object_name.casefold():
            score = float(target.get("score", 0.0))
        stage = RecordedStage(
            name=stage_name,
            q=self.current_q,
            tool_point_base=tool,
            target_point_base=self.profile_draft.target_point_base,
            captured_at=utc_now(),
            notes=str(payload.get("notes", "")),
            score=score,
            gripper_gap_m=self.gripper_gap_m,
        )
        self.profile_draft.capture(stage)
        self._save_profile_draft()
        self._publish_teach_markers()
        self._result(
            command_id,
            "profile_stage_captured",
            stage=stage_name,
            record=stage.as_dict(),
            draft=self.profile_draft.as_dict(),
        )

    def _action_save_profile(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        if self.profile_draft is None:
            raise ValueError("no active profile draft")
        if "speed_scale" in payload:
            self.profile_draft.speed_scale = max(
                0.05, min(1.0, float(payload["speed_scale"]))
            )
        if "notes" in payload:
            self.profile_draft.notes = str(payload["notes"])
        profile = derive_pick_profile(self.profile_draft)
        profile["created_at"] = utc_now()
        profile["created_by"] = "camera_arm_teach"

        section = self.report.section("grasp_profiles")
        profiles = dict(section.get("profiles", {})) if isinstance(section.get("profiles"), Mapping) else {}
        profiles[self.profile_draft.object_name] = profile
        self.report.complete_section(
            "grasp_profiles",
            {
                "source": "camera_arm_teach",
                "profiles": profiles,
                "last_recorded": self.profile_draft.object_name,
                "draft": None,
            },
        )
        self._write_profile_overlay(profiles)
        self._request_profile_reload()
        object_name = self.profile_draft.object_name
        self.profile_draft = None
        self._result(
            command_id,
            "grasp_profile_saved",
            object_name=object_name,
            profile=profile,
            report_path=str(self.report.path),
            generated_profile_file=str(self.generated_profile_file),
        )

    def _action_test_profile(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        if self.pending_pick_command_id:
            raise ValueError("another profile test is already active")
        object_name = str(payload.get("object_name", self.active_target)).strip()
        if not object_name:
            raise ValueError("object_name is required")
        self.pending_pick_command_id = command_id
        self.pending_pick_object = object_name
        self._request_profile_reload()
        self._publish_json(
            self.pick_goal_pub,
            {
                "object_name": object_name,
                "profile": str(payload.get("profile", object_name)),
                "execute": True,
                "search_timeout_sec": float(payload.get("search_timeout_sec", 30.0)),
            },
        )
        self._status(
            "profile_test_started",
            command_id=command_id,
            object_name=object_name,
        )

    def _action_cancel(self, command_id: str, _: Mapping[str, Any]) -> None:
        self.stop_pub.publish(Empty())
        self.pending_motion_q = None
        self.pending_pick_command_id = ""
        self.pending_pick_object = ""
        self._cancel_finder("teach_cancel")
        self._result(command_id, "teach_cancelled")

    def _require_locked_target(self) -> Dict[str, Any]:
        if self.locked_target is None:
            raise ValueError("no stable camera target is locked")
        return dict(self.locked_target)

    def _require_tool_point(self) -> Vector3:
        if self.tool_point is None:
            raise ValueError("no /macrobot/arm/tool_pose has been received")
        return self.tool_point

    def _camera_context(self) -> Optional[Dict[str, Any]]:
        if self.locked_target is None or self.tool_point is None:
            return None
        target = vector3(self.locked_target["point_base"])
        offset = tuple(self.tool_point[index] - target[index] for index in range(3))
        return {
            "object_name": self.locked_target.get("object_name"),
            "target_point_base": list(target),
            "target_score": self.locked_target.get("score"),
            "grasp_frame_point_base": list(self.tool_point),
            "grasp_frame_offset_from_target": list(offset),
            "gripper_gap_m": self.gripper_gap_m,
        }

    def _save_profile_draft(self) -> None:
        if self.profile_draft is None:
            return
        section = self.report.section("grasp_profiles")
        profiles = section.get("profiles", {})
        if not isinstance(profiles, Mapping):
            profiles = {}
        self.report.update_section(
            "grasp_profiles",
            {
                "source": "camera_arm_teach",
                "profiles": dict(profiles),
                "draft": self.profile_draft.as_dict(),
            },
            status="in_progress",
        )

    def _write_profile_overlay(self, profiles: Mapping[str, Any]) -> None:
        root: Dict[str, Any] = {"defaults": {}, "objects": {}}
        if self.generated_profile_file.exists():
            with self.generated_profile_file.open("r", encoding="utf-8") as stream:
                loaded = yaml.safe_load(stream) or {}
            if isinstance(loaded, Mapping):
                root = dict(loaded)
                root.setdefault("defaults", {})
                root.setdefault("objects", {})
        objects = root.get("objects", {})
        if not isinstance(objects, dict):
            objects = {}
        for object_name, raw in profiles.items():
            if isinstance(raw, Mapping):
                objects[str(object_name)] = pick_profile_overlay(raw)
        root["objects"] = objects
        root["generated_by"] = "macrobot_pick_teach"
        root["generated_at"] = utc_now()
        self.generated_profile_file.parent.mkdir(parents=True, exist_ok=True)
        with self.generated_profile_file.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(root, stream, allow_unicode=True, sort_keys=False)

    def _request_profile_reload(self) -> None:
        if not self.reload_client.service_is_ready():
            self.reload_client.wait_for_service(timeout_sec=0.2)
        if self.reload_client.service_is_ready():
            self.reload_client.call_async(Trigger.Request())
        else:
            self.get_logger().warning(
                "Profile reload service is unavailable; restart pick_coordinator before testing."
            )

    def _start_motion(self, command_id: str, q: Q, label: str) -> None:
        if not self.allow_motion_commands:
            raise ValueError("motion commands are disabled")
        if self.pending_motion_q is not None:
            raise ValueError("another teach motion is active")
        if not all(math.isfinite(value) for value in q):
            raise ValueError("motion q contains a non-finite value")
        goal = JointState()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.name = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
        goal.position = list(q)
        self.pending_motion_q = q
        self.pending_motion_label = label
        self.pending_motion_command_id = command_id
        self.pending_motion_started = time.monotonic()
        self.pending_motion_validated = False
        self.joint_goal_pub.publish(goal)
        self._status(
            "teach_motion_commanded",
            command_id=command_id,
            label=label,
            q=list(q),
        )

    def _camera_info_callback(self, msg: CameraInfo) -> None:
        self.camera_last_seen_monotonic = time.monotonic()
        self.camera_frame_id = str(msg.header.frame_id)

    def _camera_ready(self) -> bool:
        if not self.require_camera_health:
            return True
        if self.camera_last_seen_monotonic <= 0.0:
            return False
        timeout = max(0.2, float(self.get_parameter("camera_health_timeout_sec").value))
        return time.monotonic() - self.camera_last_seen_monotonic <= timeout

    def _state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        names = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")
        if all(name in values for name in names):
            candidate = tuple(float(values[name]) for name in names)
            if all(math.isfinite(value) for value in candidate):
                self.current_q = candidate  # type: ignore[assignment]

    def _tool_pose_callback(self, msg: PoseStamped) -> None:
        p = msg.pose.position
        point = (float(p.x), float(p.y), float(p.z))
        if all(math.isfinite(value) for value in point):
            self.tool_point = point

    def _gap_callback(self, msg: Float64) -> None:
        if math.isfinite(float(msg.data)):
            self.gripper_gap_m = float(msg.data)

    def _detection_callback(self, msg: String) -> None:
        if not self.active_target:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, Mapping) or payload.get("event") != "localized_object":
            return
        object_name = str(payload.get("object_name", "")).strip()
        if object_name.casefold() != self.active_target.casefold():
            return
        point = _point_payload(payload.get("point_base"))
        if point is None:
            return
        try:
            score = float(payload.get("score", 0.0))
            stamp = float(payload.get("stamp_sec", time.time()))
        except (TypeError, ValueError):
            return
        self.filter.add(
            DetectionSample(
                stamp_sec=stamp,
                object_name=object_name,
                score=score,
                point_base=point,
                source=str(payload.get("source", "")),
            )
        )

    def _validation_callback(self, msg: String) -> None:
        if self.pending_motion_q is None:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, Mapping):
            return
        event = str(payload.get("event", ""))
        if event == "goal_rejected":
            command_id = self.pending_motion_command_id
            label = self.pending_motion_label
            self.pending_motion_q = None
            self._result(
                command_id,
                "teach_motion_rejected",
                False,
                label=label,
                validator=dict(payload),
            )
            return
        if event == "goal_validated":
            raw_goal = payload.get("goal")
            if isinstance(raw_goal, list) and len(raw_goal) == 3:
                goal = tuple(float(item) for item in raw_goal)
                if _q_close(goal, self.pending_motion_q):
                    self.pending_motion_validated = True

    def _bridge_callback(self, msg: String) -> None:
        if self.pending_motion_q is None:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, Mapping):
            return
        event = str(payload.get("event", ""))
        if event in {
            "runtime_interpolation_rejected",
            "defense_in_depth_rejection",
            "pico_error",
            "invalid_validated_goal",
        }:
            command_id = self.pending_motion_command_id
            label = self.pending_motion_label
            self.pending_motion_q = None
            self._result(
                command_id,
                "teach_motion_failed",
                False,
                label=label,
                bridge=dict(payload),
            )
            return
        if event != "trajectory_completed":
            return
        raw_goal = payload.get("goal")
        if isinstance(raw_goal, list) and len(raw_goal) == 3:
            goal = tuple(float(item) for item in raw_goal)
            if not _q_close(goal, self.pending_motion_q):
                return
        command_id = self.pending_motion_command_id
        label = self.pending_motion_label
        q = self.pending_motion_q
        self.current_q = q
        self.pending_motion_q = None
        self._result(
            command_id,
            "teach_motion_completed",
            label=label,
            q=list(q),
            validated=self.pending_motion_validated,
        )

    def _pick_result_callback(self, msg: String) -> None:
        if not self.pending_pick_command_id:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, Mapping):
            return
        object_name = str(payload.get("object_name", ""))
        if object_name and object_name.casefold() != self.pending_pick_object.casefold():
            return
        command_id = self.pending_pick_command_id
        self.pending_pick_command_id = ""
        self.pending_pick_object = ""
        self._result(
            command_id,
            "profile_test_completed" if payload.get("ok") else "profile_test_failed",
            bool(payload.get("ok")),
            pick_result=dict(payload),
        )

    def _timer_callback(self) -> None:
        if self.active_target and self.target_lock_command_id:
            timeout = self.target_lock_timeout
            if time.monotonic() - self.target_lock_started > timeout:
                command_id = self.target_lock_command_id
                self.target_lock_command_id = ""
                self._cancel_finder("teach_target_lock_timeout")
                timed_out_target = self.active_target
                self.active_target = ""
                target = String()
                target.data = ""
                self.active_target_pub.publish(target)
                self._result(
                    command_id,
                    "target_lock_timeout",
                    False,
                    object_name=timed_out_target,
                )
            else:
                stable = self.filter.stable(
                    now_sec=time.time(),
                    object_name=self.active_target,
                    minimum_score=float(self.get_parameter("target_min_score").value),
                    minimum_count=int(
                        self.get_parameter("target_stability_count").value
                    ),
                    window_sec=float(
                        self.get_parameter("target_stability_window_sec").value
                    ),
                    radius_m=float(
                        self.get_parameter("target_stability_radius_m").value
                    ),
                )
                if stable is not None:
                    self.locked_target = {
                        "object_name": self.active_target,
                        "point_base": list(stable.point_base),
                        "score": stable.score,
                        "radius_m": stable.radius_m,
                        "locked_at": utc_now(),
                    }
                    command_id = self.target_lock_command_id
                    self.target_lock_command_id = ""
                    self._cancel_finder("teach_target_locked")
                    self._publish_teach_markers()
                    self._result(
                        command_id,
                        "target_locked",
                        target=self.locked_target,
                    )

        if self.pending_motion_q is not None:
            timeout = float(self.get_parameter("motion_timeout_sec").value)
            if time.monotonic() - self.pending_motion_started > timeout:
                command_id = self.pending_motion_command_id
                label = self.pending_motion_label
                self.stop_pub.publish(Empty())
                self.pending_motion_q = None
                self._result(
                    command_id,
                    "teach_motion_timeout",
                    False,
                    label=label,
                )

    def _cancel_finder(self, reason: str) -> None:
        message = String()
        message.data = reason
        self.finder_cancel_pub.publish(message)

    def _publish_teach_markers(self) -> None:
        markers = MarkerArray()
        now = self.get_clock().now().to_msg()

        def sphere(marker_id: int, point: Vector3, scale: float, color, text: str) -> None:
            marker = Marker()
            marker.header.frame_id = self.base_frame
            marker.header.stamp = now
            marker.ns = "macrobot_pick_teach"
            marker.id = marker_id
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.orientation.w = 1.0
            marker.pose.position.x = point[0]
            marker.pose.position.y = point[1]
            marker.pose.position.z = point[2]
            marker.scale.x = scale
            marker.scale.y = scale
            marker.scale.z = scale
            marker.color.r = color[0]
            marker.color.g = color[1]
            marker.color.b = color[2]
            marker.color.a = 0.9
            markers.markers.append(marker)

            label = Marker()
            label.header = marker.header
            label.ns = "macrobot_pick_teach_labels"
            label.id = 1000 + marker_id
            label.type = Marker.TEXT_VIEW_FACING
            label.action = Marker.ADD
            label.pose = marker.pose
            label.pose.position.z += 0.018
            label.scale.z = 0.018
            label.color.r = 1.0
            label.color.g = 1.0
            label.color.b = 1.0
            label.color.a = 1.0
            label.text = text
            markers.markers.append(label)

        if self.locked_target is not None:
            sphere(
                1,
                vector3(self.locked_target["point_base"]),
                0.016,
                (1.0, 0.15, 0.15),
                f"target: {self.locked_target['object_name']}",
            )
        if self.tool_point is not None:
            sphere(2, self.tool_point, 0.012, (0.15, 1.0, 0.25), "grasp_frame")
        if self.profile_draft is not None:
            colors = {
                "PRE_GRASP": (1.0, 0.8, 0.0),
                "GRASP": (0.0, 1.0, 0.3),
                "CLOSE": (0.0, 0.7, 1.0),
                "LIFT": (0.2, 0.4, 1.0),
                "PLACE": (0.8, 0.2, 1.0),
            }
            for index, (name, stage) in enumerate(self.profile_draft.stages.items(), 10):
                sphere(index, stage.tool_point_base, 0.010, colors.get(name, (1.0, 1.0, 1.0)), name)
        self.marker_pub.publish(markers)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CameraTeachNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
