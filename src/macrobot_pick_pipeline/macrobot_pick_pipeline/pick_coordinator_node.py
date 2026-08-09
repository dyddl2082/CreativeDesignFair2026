from __future__ import annotations

from collections import deque
import json
import math
from pathlib import Path
import time
from typing import Any, Dict, Optional, Tuple

from ament_index_python.packages import get_package_share_directory
import rclpy
from geometry_msgs.msg import Point, PointStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, String
from visualization_msgs.msg import Marker, MarkerArray
import yaml

from macrobot_arm_kinematics.model import ArmGeometry, JointLimits, MacRobotArmModel

from .planner import DetectionSample, PickPlan, StablePointFilter, build_pick_plan
from .profiles import PickProfile, PickProfileRepository, Q, Vector3


TERMINAL_STATES = {"IDLE", "DONE", "FAILED", "CANCELLED"}


def _ros_params(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        root = yaml.safe_load(stream) or {}
    if isinstance(root, dict):
        wildcard = root.get("/**", {})
        if isinstance(wildcard, dict):
            params = wildcard.get("ros__parameters", {})
            if isinstance(params, dict):
                return params
    return {}


def _point_from_payload(value: Any) -> Optional[Vector3]:
    if not isinstance(value, dict):
        return None
    try:
        result = (float(value["x"]), float(value["y"]), float(value["z"]))
    except (KeyError, TypeError, ValueError):
        return None
    return result if all(math.isfinite(item) for item in result) else None


def _q_close(a: Q, b: Q, tolerance: float = 1e-4) -> bool:
    return max(abs(a[index] - b[index]) for index in range(3)) <= tolerance


def _as_bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().casefold()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    return default


class PickCoordinatorNode(Node):
    """State machine that connects object localization to validated arm goals."""

    def __init__(self) -> None:
        super().__init__("macrobot_pick_coordinator")

        description_pkg = Path(get_package_share_directory("macrobot_description"))
        package_share = Path(get_package_share_directory("macrobot_pick_pipeline"))
        default_kinematics = description_pkg / "config" / "kinematics.yaml"
        default_profiles = package_share / "config" / "pick_profiles.yaml"
        default_report = (
            Path.home()
            / "MacRobot"
            / "data"
            / "commissioning"
            / "arm_commissioning_report.yaml"
        )

        self.declare_parameter("goal_topic", "/macrobot/pick/goal")
        self.declare_parameter("cancel_topic", "/macrobot/pick/cancel")
        self.declare_parameter("status_topic", "/macrobot/pick/status")
        self.declare_parameter("result_topic", "/macrobot/pick/result")
        self.declare_parameter("active_target_topic", "/macrobot/pick/active_target")
        self.declare_parameter(
            "localized_detection_topic", "/macrobot/perception/localized_detection"
        )
        self.declare_parameter("finder_goal_topic", "/object_finder/goal")
        self.declare_parameter("finder_cancel_topic", "/object_finder/cancel")
        self.declare_parameter("joint_goal_topic", "/macrobot/arm/joint_goal")
        self.declare_parameter(
            "validation_status_topic", "/macrobot/arm/validation_status"
        )
        self.declare_parameter(
            "bridge_status_topic", "/macrobot/arm/servo_bridge/status"
        )
        self.declare_parameter(
            "logical_state_topic", "/macrobot/arm/logical_joint_states"
        )
        self.declare_parameter("arm_stop_topic", "/macrobot/arm/stop")
        self.declare_parameter("marker_topic", "/macrobot/pick/markers")
        self.declare_parameter(
            "base_alignment_request_topic", "/macrobot/base/alignment_request"
        )

        self.declare_parameter("kinematics_file", str(default_kinematics))
        self.declare_parameter("profile_file", str(default_profiles))
        self.declare_parameter("commissioning_report", str(default_report))
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("use_finder", True)
        self.declare_parameter("replace_active_goal", True)
        self.declare_parameter("timer_rate_hz", 20.0)
        self.declare_parameter("default_execute", True)

        self.base_frame = str(self.get_parameter("base_frame").value)
        self.use_finder = bool(self.get_parameter("use_finder").value)
        self.replace_active_goal = bool(
            self.get_parameter("replace_active_goal").value
        )
        self.default_execute = bool(self.get_parameter("default_execute").value)

        kinematics_file = Path(
            str(self.get_parameter("kinematics_file").value)
        ).expanduser().resolve()
        params = _ros_params(kinematics_file)
        geometry = ArmGeometry(
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
        limits = JointLimits(
            arm_lift_min=float(params.get("arm_lift_min", -1.0)),
            arm_lift_max=float(params.get("arm_lift_max", 1.0)),
            wrist_pitch_min=float(params.get("wrist_pitch_min", -1.30)),
            wrist_pitch_max=float(params.get("wrist_pitch_max", 1.30)),
            tool_pitch_min=float(params.get("tool_pitch_min", -2.0)),
            tool_pitch_max=float(params.get("tool_pitch_max", 2.0)),
            four_bar_margin=float(params.get("four_bar_margin", math.radians(10.0))),
            gripper_min=float(params.get("gripper_min", 0.0)),
            gripper_max=float(params.get("gripper_max", math.pi / 2.0)),
        )
        self.model = MacRobotArmModel(geometry, limits)
        self.profiles = PickProfileRepository(
            str(self.get_parameter("profile_file").value),
            str(self.get_parameter("commissioning_report").value),
        )

        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 20
        )
        self.result_pub = self.create_publisher(
            String, str(self.get_parameter("result_topic").value), 10
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
        self.joint_goal_pub = self.create_publisher(
            JointState, str(self.get_parameter("joint_goal_topic").value), 10
        )
        self.stop_pub = self.create_publisher(
            Empty, str(self.get_parameter("arm_stop_topic").value), 10
        )
        self.marker_pub = self.create_publisher(
            MarkerArray, str(self.get_parameter("marker_topic").value), 10
        )
        self.alignment_pub = self.create_publisher(
            String,
            str(self.get_parameter("base_alignment_request_topic").value),
            10,
        )

        self.create_subscription(
            String,
            str(self.get_parameter("goal_topic").value),
            self._goal_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("cancel_topic").value),
            self._cancel_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("localized_detection_topic").value),
            self._detection_callback,
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
        self.create_subscription(
            JointState,
            str(self.get_parameter("logical_state_topic").value),
            self._state_callback,
            50,
        )

        self.state = "IDLE"
        self.current_q: Q = (0.0, 0.0, 0.0)
        self.filter = StablePointFilter()
        self.object_name = ""
        self.profile_name = ""
        self.profile: Optional[PickProfile] = None
        self.execute_pick = True
        self.search_started = 0.0
        self.plan: Optional[PickPlan] = None
        self.step_index = -1
        self.pending_q: Optional[Q] = None
        self.pending_step = ""
        self.pending_started = 0.0
        self.pending_validated = False
        self.request_id = ""

        rate = max(2.0, float(self.get_parameter("timer_rate_hz").value))
        self.create_timer(1.0 / rate, self._timer_callback)
        self.get_logger().info(
            "Pick coordinator ready: SEARCH -> STABLE 3D TARGET -> IK PLAN -> VALIDATED PICK"
        )

    def _publish_json(self, publisher, payload: Dict[str, object]) -> None:
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        publisher.publish(message)

    def _status(self, event: str, ok: bool = True, **details: object) -> None:
        payload: Dict[str, object] = {
            **details,
            "ok": ok,
            "event": event,
            "state": self.state,
            "request_id": self.request_id,
            "object_name": self.object_name,
        }
        self._publish_json(self.status_pub, payload)
        if ok:
            self.get_logger().info(json.dumps(payload, ensure_ascii=False))
        else:
            self.get_logger().warning(json.dumps(payload, ensure_ascii=False))

    def _parse_goal(self, text: str) -> Dict[str, object]:
        text = text.strip()
        if not text:
            raise ValueError("empty_object_name")
        if text.startswith("{"):
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError("goal_json_must_be_object")
            object_name = str(data.get("object_name", data.get("name", ""))).strip()
            if not object_name:
                raise ValueError("empty_object_name")
            return {
                "object_name": object_name,
                "profile": str(data.get("profile", "")).strip(),
                "execute": _as_bool(data.get("execute"), self.default_execute),
                "search_timeout_sec": data.get("search_timeout_sec"),
            }
        return {
            "object_name": text,
            "profile": "",
            "execute": self.default_execute,
            "search_timeout_sec": None,
        }

    def _goal_callback(self, msg: String) -> None:
        try:
            request = self._parse_goal(msg.data)
        except Exception as exc:
            self._status("invalid_pick_goal", False, error=str(exc))
            return
        if self.state not in TERMINAL_STATES and not self.replace_active_goal:
            self._status("pick_busy", False)
            return
        if self.state not in TERMINAL_STATES:
            self._cancel("replaced_by_new_goal")

        self.object_name = str(request["object_name"])
        self.profile_name = str(request["profile"])
        self.execute_pick = bool(request["execute"])
        self.profile = self.profiles.get(self.object_name, self.profile_name)
        if request["search_timeout_sec"] is not None:
            self.profile = PickProfile.from_mapping(
                self.profile.name,
                {"search_timeout_sec": float(request["search_timeout_sec"])},
                base=self.profile,
            )
        if self.profile.close_q3 < self.model.limits.gripper_min or self.profile.close_q3 > self.model.limits.gripper_max:
            self._status(
                "profile_gripper_limit_error",
                False,
                close_q3=self.profile.close_q3,
                limits=[self.model.limits.gripper_min, self.model.limits.gripper_max],
            )
            return

        self.request_id = f"pick-{int(time.time() * 1000)}"
        self.filter.clear()
        self.plan = None
        self.step_index = -1
        self.pending_q = None
        self.pending_step = ""
        self.pending_validated = False
        self.search_started = time.monotonic()
        self.state = "SEARCHING"

        target = String()
        target.data = self.object_name
        self.active_target_pub.publish(target)
        if self.use_finder:
            finder_goal = {
                "object_name": self.object_name,
                "timeout_sec": self.profile.search_timeout_sec,
                "continuous": True,
            }
            self._publish_json(self.finder_goal_pub, finder_goal)
        self._status(
            "pick_started",
            profile=self.profile.name,
            execute=self.execute_pick,
            use_finder=self.use_finder,
        )

    def _cancel_callback(self, msg: String) -> None:
        self._cancel(msg.data.strip() or "user_cancel")

    def _cancel(self, reason: str) -> None:
        self.stop_pub.publish(Empty())
        cancel = String()
        cancel.data = reason
        self.finder_cancel_pub.publish(cancel)
        self._clear_active_target()
        self.state = "CANCELLED"
        self.pending_q = None
        self._status("pick_cancelled", False, reason=reason)

    def _clear_active_target(self) -> None:
        message = String()
        message.data = ""
        self.active_target_pub.publish(message)

    def _state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        names = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")
        if all(name in values for name in names):
            q = tuple(float(values[name]) for name in names)
            if all(math.isfinite(value) for value in q):
                self.current_q = q  # type: ignore[assignment]

    def _detection_callback(self, msg: String) -> None:
        if self.state != "SEARCHING":
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict) or payload.get("event") != "localized_object":
            return
        object_name = str(payload.get("object_name", "")).strip()
        if object_name.casefold() != self.object_name.casefold():
            return
        point = _point_from_payload(payload.get("point_base"))
        if point is None:
            return
        score = float(payload.get("score", 0.0))
        stamp = float(payload.get("stamp_sec", time.time()))
        self.filter.add(
            DetectionSample(
                stamp_sec=stamp,
                object_name=object_name,
                score=score,
                point_base=point,
                source=str(payload.get("source", "")),
            )
        )

    def _timer_callback(self) -> None:
        if self.state == "SEARCHING" and self.profile is not None:
            if time.monotonic() - self.search_started > self.profile.search_timeout_sec:
                self._fail("search_timeout")
                return
            stable = self.filter.stable(
                now_sec=time.time(),
                object_name=self.object_name,
                minimum_score=self.profile.min_score,
                minimum_count=self.profile.stability_count,
                window_sec=self.profile.stability_window_sec,
                radius_m=self.profile.stability_radius_m,
            )
            if stable is not None:
                self._accept_stable_target(stable.point_base, stable.score, stable.radius_m)

        if self.state == "WAITING_MOTION" and self.profile is not None:
            if time.monotonic() - self.pending_started > self.profile.motion_timeout_sec:
                self._fail(
                    "motion_timeout",
                    step=self.pending_step,
                    pending_q=list(self.pending_q) if self.pending_q else None,
                )

    def _accept_stable_target(
        self, point: Vector3, score: float, radius_m: float
    ) -> None:
        assert self.profile is not None
        grasp_y = point[1] + self.profile.grasp_offset_base[1]
        lateral_error = grasp_y - self.model.geometry.tool_y
        if abs(lateral_error) > self.profile.lateral_tolerance_m:
            request = {
                "ok": False,
                "event": "base_alignment_required",
                "object_name": self.object_name,
                "target_point_base": {"x": point[0], "y": point[1], "z": point[2]},
                "arm_plane_y": self.model.geometry.tool_y,
                "lateral_error_m": lateral_error,
                "reason": "target_outside_arm_plane",
            }
            self._publish_json(self.alignment_pub, request)
            self._fail(
                "base_alignment_required",
                target_point_base=request["target_point_base"],
                arm_plane_y=request["arm_plane_y"],
                lateral_error_m=request["lateral_error_m"],
            )
            return

        # Plan with the ideal arm-plane Y after checking that chassis alignment
        # is already close enough. The reduced arm IK is planar in base X/Z.
        planning_point: Vector3 = (point[0], self.model.geometry.tool_y, point[2])
        try:
            self.plan = build_pick_plan(
                self.model,
                self.profile,
                self.object_name,
                planning_point,
                self.current_q,
            )
        except ValueError as exc:
            request = {
                "ok": False,
                "event": "base_alignment_required",
                "object_name": self.object_name,
                "target_point_base": {"x": point[0], "y": point[1], "z": point[2]},
                "reason": str(exc),
            }
            self._publish_json(self.alignment_pub, request)
            self._fail(
                "pick_plan_unreachable",
                target_point_base=request["target_point_base"],
                planning_reason=request["reason"],
            )
            return

        self._cancel_finder("stable_target_acquired")
        self._publish_markers(self.plan)
        self._status(
            "target_locked",
            score=score,
            stability_radius_m=radius_m,
            object_point_base=list(point),
            plan={step.name: list(step.q) for step in self.plan.steps},
        )
        if not self.execute_pick:
            self.state = "DONE"
            self._publish_result("localized_only")
            self._clear_active_target()
            return
        self.step_index = 0
        self._send_current_step()

    def _cancel_finder(self, reason: str) -> None:
        cancel = String()
        cancel.data = reason
        self.finder_cancel_pub.publish(cancel)

    def _send_current_step(self) -> None:
        if self.plan is None or self.step_index >= len(self.plan.steps):
            self.state = "DONE"
            self._publish_result("pick_completed")
            self._clear_active_target()
            return
        step = self.plan.steps[self.step_index]
        self.pending_q = step.q
        self.pending_step = step.name
        self.pending_validated = False
        self.pending_started = time.monotonic()
        self.state = "WAITING_MOTION"

        goal = JointState()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.name = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
        goal.position = list(step.q)
        self.joint_goal_pub.publish(goal)
        self._status(
            "pick_step_commanded",
            step=step.name,
            step_index=self.step_index,
            q=list(step.q),
            target_point_base=(
                list(step.target_point_base) if step.target_point_base else None
            ),
        )

    def _validation_callback(self, msg: String) -> None:
        if self.state != "WAITING_MOTION" or self.pending_q is None:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if event == "goal_rejected":
            self._fail(
                "arm_goal_rejected",
                step=self.pending_step,
                validator=payload,
            )
            return
        if event == "goal_validated":
            goal = payload.get("goal")
            if isinstance(goal, list) and len(goal) == 3:
                q = tuple(float(value) for value in goal)
                if _q_close(q, self.pending_q):
                    self.pending_validated = True
                    self._status("pick_step_validated", step=self.pending_step)

    def _bridge_callback(self, msg: String) -> None:
        if self.state != "WAITING_MOTION" or self.pending_q is None:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if event in {
            "runtime_interpolation_rejected",
            "defense_in_depth_rejection",
            "pico_error",
            "invalid_validated_goal",
        }:
            self._fail("servo_bridge_error", step=self.pending_step, bridge=payload)
            return
        if event != "trajectory_completed":
            return
        goal = payload.get("goal")
        if isinstance(goal, list) and len(goal) == 3:
            q = tuple(float(value) for value in goal)
            if not _q_close(q, self.pending_q):
                return
        completed_step = self.pending_step
        self.current_q = self.pending_q
        self.pending_q = None
        self.pending_step = ""
        self.pending_validated = False
        self.step_index += 1
        self._status("pick_step_completed", step=completed_step)
        self._send_current_step()

    def _fail(self, reason: str, **details: object) -> None:
        self.stop_pub.publish(Empty())
        self._cancel_finder(reason)
        self.state = "FAILED"
        self.pending_q = None
        self._clear_active_target()
        self._status("pick_failed", False, reason=reason, **details)
        self._publish_json(
            self.result_pub,
            {
                **details,
                "ok": False,
                "event": "pick_failed",
                "request_id": self.request_id,
                "object_name": self.object_name,
                "reason": reason,
            },
        )

    def _publish_result(self, event: str) -> None:
        payload: Dict[str, object] = {
            "ok": True,
            "event": event,
            "request_id": self.request_id,
            "object_name": self.object_name,
            "final_q": list(self.current_q),
        }
        if self.plan is not None:
            payload.update(
                {
                    "object_point_base": list(self.plan.object_point_base),
                    "grasp_point_base": list(self.plan.grasp_point_base),
                    "lift_point_base": list(self.plan.lift_point_base),
                    "steps": {step.name: list(step.q) for step in self.plan.steps},
                }
            )
        self._publish_json(self.result_pub, payload)
        self._status(event)

    def _publish_markers(self, plan: PickPlan) -> None:
        array = MarkerArray()
        clear = Marker()
        clear.action = Marker.DELETEALL
        array.markers.append(clear)
        now = self.get_clock().now().to_msg()

        specifications = (
            (0, "object", plan.object_point_base, (1.0, 0.2, 0.2, 0.9)),
            (1, "pregrasp", plan.pregrasp_point_base, (1.0, 0.8, 0.1, 0.9)),
            (2, "grasp", plan.grasp_point_base, (0.2, 1.0, 0.2, 0.9)),
            (3, "lift", plan.lift_point_base, (0.2, 0.5, 1.0, 0.9)),
        )
        for marker_id, label, point, color in specifications:
            marker = Marker()
            marker.header.frame_id = self.base_frame
            marker.header.stamp = now
            marker.ns = "macrobot_pick_points"
            marker.id = marker_id
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.orientation.w = 1.0
            marker.pose.position.x, marker.pose.position.y, marker.pose.position.z = point
            marker.scale.x = marker.scale.y = marker.scale.z = 0.018
            marker.color.r, marker.color.g, marker.color.b, marker.color.a = color
            array.markers.append(marker)

            text = Marker()
            text.header.frame_id = self.base_frame
            text.header.stamp = now
            text.ns = "macrobot_pick_labels"
            text.id = marker_id + 100
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD
            text.pose.orientation.w = 1.0
            text.pose.position.x = point[0]
            text.pose.position.y = point[1]
            text.pose.position.z = point[2] + 0.025
            text.scale.z = 0.018
            text.color.r = text.color.g = text.color.b = text.color.a = 1.0
            text.text = label
            array.markers.append(text)

        line = Marker()
        line.header.frame_id = self.base_frame
        line.header.stamp = now
        line.ns = "macrobot_pick_path"
        line.id = 200
        line.type = Marker.LINE_STRIP
        line.action = Marker.ADD
        line.scale.x = 0.004
        line.color.r = 0.8
        line.color.g = 0.8
        line.color.b = 1.0
        line.color.a = 0.9
        for point in (
            plan.pregrasp_point_base,
            plan.grasp_point_base,
            plan.lift_point_base,
        ):
            item = Point()
            item.x, item.y, item.z = point
            line.points.append(item)
        array.markers.append(line)
        self.marker_pub.publish(array)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PickCoordinatorNode()
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
