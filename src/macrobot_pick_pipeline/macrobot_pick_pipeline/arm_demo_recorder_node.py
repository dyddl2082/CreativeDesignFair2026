from __future__ import annotations

import json
import math
from pathlib import Path
import time
from typing import Any, Dict, Mapping, Optional, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, String

from .arm_demo_store import ArmDemoRepository
from .demo_core import (
    DemoRecording,
    JOINT_NAMES,
    Q,
    TrajectorySampler,
    Waypoint,
    max_joint_delta,
    playback_keyframes,
    q3,
    safe_name,
)
from .teach_store import AtomicYamlStore, utc_now


def _q_close(a: Q, b: Q, tolerance: float = 1e-4) -> bool:
    return max_joint_delta(a, b) <= tolerance


class ArmDemoRecorderNode(Node):
    """Camera-independent, source-agnostic arm demonstration recorder.

    The recorder passively observes ``/macrobot/arm/logical_joint_states``.  The
    user may control the arm with the bundled jog CLI or any other controller
    that still uses the validated ``/macrobot/arm/joint_goal`` path.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_arm_demo_recorder")

        default_report = (
            Path.home()
            / "MacRobot"
            / "data"
            / "commissioning"
            / "arm_commissioning_report.yaml"
        )
        default_recordings = (
            Path.home() / "MacRobot" / "data" / "arm_primitives"
        )

        self.declare_parameter("command_topic", "/macrobot/arm/demo/command")
        self.declare_parameter("status_topic", "/macrobot/arm/demo/status")
        self.declare_parameter("result_topic", "/macrobot/arm/demo/result")
        self.declare_parameter(
            "logical_state_topic", "/macrobot/arm/logical_joint_states"
        )
        self.declare_parameter("joint_goal_topic", "/macrobot/arm/joint_goal")
        self.declare_parameter(
            "validation_status_topic", "/macrobot/arm/validation_status"
        )
        self.declare_parameter(
            "bridge_status_topic", "/macrobot/arm/servo_bridge/status"
        )
        self.declare_parameter("arm_stop_topic", "/macrobot/arm/stop")
        self.declare_parameter("report_path", str(default_report))
        self.declare_parameter("recordings_dir", str(default_recordings))
        self.declare_parameter("allow_motion_commands", True)
        self.declare_parameter("sample_rate_hz", 30.0)
        self.declare_parameter("min_joint_delta_rad", 0.003)
        self.declare_parameter("max_sample_interval_sec", 0.25)
        self.declare_parameter("max_recording_duration_sec", 180.0)
        self.declare_parameter("playback_keyframe_delta_rad", 0.01)
        self.declare_parameter("playback_keyframe_interval_sec", 1.0)
        self.declare_parameter("motion_timeout_sec", 25.0)

        self.allow_motion_commands = bool(
            self.get_parameter("allow_motion_commands").value
        )
        self.report = AtomicYamlStore(str(self.get_parameter("report_path").value))
        self.repository = ArmDemoRepository(
            str(self.get_parameter("recordings_dir").value), self.report
        )

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
            30,
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
        self.have_state = False
        self.last_state_monotonic = 0.0

        self.sampler: Optional[TrajectorySampler] = None
        self.recording_name = ""
        self.recording_notes = ""
        self.recording_speed_scale = 0.5
        self.recording_command_id = ""

        self.pending_motion_q: Optional[Q] = None
        self.pending_motion_command_id = ""
        self.pending_motion_label = ""
        self.pending_motion_started = 0.0
        self.pending_motion_validated = False
        self.pending_motion_for_playback = False

        self.playback_name = ""
        self.playback_command_id = ""
        self.playback_waypoints = []
        self.playback_index = 0
        self.playback_speed_scale = 1.0
        self.playback_due_monotonic = 0.0

        rate = max(5.0, float(self.get_parameter("sample_rate_hz").value))
        self.create_timer(1.0 / rate, self._timer_callback)
        self._status(
            "arm_demo_recorder_ready",
            recordings_dir=str(self.repository.root),
            report_path=str(self.report.path),
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
            "have_state": self.have_state,
            "recording": bool(self.sampler and self.sampler.active),
            "recording_name": self.recording_name,
            "recording_paused": bool(self.sampler and self.sampler.paused),
            "playback_name": self.playback_name,
            "playback_index": self.playback_index,
            "playback_count": len(self.playback_waypoints),
        }
        self._publish_json(self.status_pub, payload)
        if ok:
            self.get_logger().info(json.dumps(payload, ensure_ascii=False))
        else:
            self.get_logger().warning(json.dumps(payload, ensure_ascii=False))

    def _result(
        self, command_id: str, event: str, ok: bool = True, **details: Any
    ) -> None:
        self._publish_json(
            self.result_pub,
            {**details, "ok": ok, "event": event, "command_id": command_id},
        )

    def _command_callback(self, msg: String) -> None:
        payload: Dict[str, Any] = {}
        command_id = ""
        try:
            loaded = json.loads(msg.data)
            if not isinstance(loaded, dict):
                raise ValueError("arm demo command must be a JSON object")
            payload = loaded
            action = str(payload.get("action", "")).strip().lower()
            command_id = str(
                payload.get("command_id", f"demo-{int(time.time() * 1000)}")
            )
            if not action:
                raise ValueError("missing action")
            handler = getattr(self, f"_action_{action}", None)
            if handler is None:
                raise ValueError(f"unsupported action: {action}")
            handler(command_id, payload)
        except Exception as exc:
            self._result(command_id, "arm_demo_command_failed", False, error=str(exc))

    def _action_status(self, command_id: str, _: Mapping[str, Any]) -> None:
        elapsed = (
            self.sampler.elapsed(time.monotonic())
            if self.sampler and self.sampler.active
            else 0.0
        )
        self._result(
            command_id,
            "arm_demo_status",
            current_q=list(self.current_q),
            have_state=self.have_state,
            state_age_sec=(
                max(0.0, time.monotonic() - self.last_state_monotonic)
                if self.have_state
                else None
            ),
            recording=bool(self.sampler and self.sampler.active),
            recording_paused=bool(self.sampler and self.sampler.paused),
            recording_name=self.recording_name,
            recording_elapsed_sec=elapsed,
            recording_waypoint_count=(len(self.sampler.waypoints) if self.sampler else 0),
            playback_name=self.playback_name,
            playback_index=self.playback_index,
            playback_count=len(self.playback_waypoints),
            primitives=self.repository.list(),
            recordings_dir=str(self.repository.root),
        )

    def _require_state(self) -> None:
        if not self.have_state:
            raise ValueError("no logical joint state has been received")

    def _action_start_recording(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        self._require_state()
        if self.sampler and self.sampler.active:
            raise ValueError("another recording is already active")
        if self.playback_name:
            raise ValueError("cannot record while playback is active")
        self.recording_name = safe_name(str(payload.get("name", "ARM_DEMO")))
        self.recording_notes = str(payload.get("notes", ""))
        self.recording_speed_scale = max(
            0.05, min(1.0, float(payload.get("speed_scale", 0.5)))
        )
        self.recording_command_id = command_id
        self.sampler = TrajectorySampler(
            min_joint_delta_rad=float(
                self.get_parameter("min_joint_delta_rad").value
            ),
            max_sample_interval_sec=float(
                self.get_parameter("max_sample_interval_sec").value
            ),
            max_duration_sec=float(
                self.get_parameter("max_recording_duration_sec").value
            ),
        )
        self.sampler.start(time.monotonic(), self.current_q)
        self._result(
            command_id,
            "arm_demo_recording_started",
            name=self.recording_name,
            initial_q=list(self.current_q),
        )
        self._status("arm_demo_recording_active", name=self.recording_name)

    def _action_pause_recording(
        self, command_id: str, _: Mapping[str, Any]
    ) -> None:
        if not self.sampler or not self.sampler.active:
            raise ValueError("no active recording")
        self.sampler.pause(time.monotonic())
        self._result(command_id, "arm_demo_recording_paused", name=self.recording_name)

    def _action_resume_recording(
        self, command_id: str, _: Mapping[str, Any]
    ) -> None:
        if not self.sampler or not self.sampler.active:
            raise ValueError("no active recording")
        self.sampler.resume(time.monotonic())
        self._result(command_id, "arm_demo_recording_resumed", name=self.recording_name)

    def _action_mark(self, command_id: str, payload: Mapping[str, Any]) -> None:
        if not self.sampler or not self.sampler.active:
            raise ValueError("no active recording")
        label = str(payload.get("label", "MARK")).strip() or "MARK"
        self.sampler.mark(time.monotonic(), label)
        self._result(command_id, "arm_demo_mark_added", label=label)

    def _finish_recording(self, *, save: bool) -> Dict[str, Any]:
        if not self.sampler or not self.sampler.active:
            raise ValueError("no active recording")
        waypoints, marks = self.sampler.finish(time.monotonic(), self.current_q)
        name = self.recording_name
        details: Dict[str, Any] = {
            "name": name,
            "waypoint_count": len(waypoints),
            "duration_sec": waypoints[-1].t_sec if waypoints else 0.0,
            "final_q": list(waypoints[-1].q if waypoints else self.current_q),
            "saved": save,
        }
        if save:
            recording = DemoRecording(
                name=name,
                kind="trajectory",
                recorded_at=utc_now(),
                waypoints=waypoints,
                speed_scale=self.recording_speed_scale,
                notes=self.recording_notes,
                marks=marks,
            )
            path = self.repository.save(recording)
            details["path"] = str(path)
        self.sampler = None
        self.recording_name = ""
        self.recording_notes = ""
        self.recording_command_id = ""
        return details

    def _action_stop_recording(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        details = self._finish_recording(save=bool(payload.get("save", True)))
        self._result(command_id, "arm_demo_recording_stopped", **details)
        self._status("arm_demo_recording_idle")

    def _action_discard_recording(
        self, command_id: str, _: Mapping[str, Any]
    ) -> None:
        details = self._finish_recording(save=False)
        self._result(command_id, "arm_demo_recording_discarded", **details)

    def _action_record_pose(
        self, command_id: str, payload: Mapping[str, Any]
    ) -> None:
        self._require_state()
        name = safe_name(str(payload.get("name", "ARM_POSE")))
        recording = DemoRecording(
            name=name,
            kind="pose",
            recorded_at=utc_now(),
            waypoints=[
                # A pose is represented as a one-waypoint trajectory for a common player.
                Waypoint(0.0, self.current_q)
            ],
            speed_scale=max(0.05, min(1.0, float(payload.get("speed_scale", 0.5)))),
            notes=str(payload.get("notes", "")),
        )
        path = self.repository.save(recording)
        self._result(
            command_id,
            "arm_pose_recorded",
            name=name,
            q=list(self.current_q),
            path=str(path),
        )

    def _action_list(self, command_id: str, _: Mapping[str, Any]) -> None:
        self._result(command_id, "arm_demo_list", primitives=self.repository.list())

    def _action_delete(self, command_id: str, payload: Mapping[str, Any]) -> None:
        name = str(payload.get("name", "")).strip()
        if not name:
            raise ValueError("name is required")
        deleted = self.repository.delete(name)
        self._result(command_id, "arm_demo_deleted", deleted=deleted, name=name)

    def _action_move_to_q(self, command_id: str, payload: Mapping[str, Any]) -> None:
        q = q3(payload.get("q"), name="move_to_q.q")
        self._start_motion(command_id, q, str(payload.get("label", "arm_demo_jog")), False)

    def _action_play(self, command_id: str, payload: Mapping[str, Any]) -> None:
        if not self.allow_motion_commands:
            raise ValueError("motion commands are disabled")
        if self.playback_name or self.pending_motion_q is not None:
            raise ValueError("another motion or playback is active")
        name = str(payload.get("name", "")).strip()
        if not name:
            raise ValueError("name is required")
        recording = self.repository.load(name)
        keyframes = playback_keyframes(
            recording.waypoints,
            min_joint_delta_rad=float(
                self.get_parameter("playback_keyframe_delta_rad").value
            ),
            max_interval_sec=float(
                self.get_parameter("playback_keyframe_interval_sec").value
            ),
        )
        if not keyframes:
            raise ValueError("primitive contains no playable waypoints")
        self.playback_name = recording.name
        self.playback_command_id = command_id
        self.playback_waypoints = keyframes
        self.playback_index = 0
        self.playback_speed_scale = max(
            0.05, min(2.0, float(payload.get("speed_scale", 1.0)))
        )
        self.playback_due_monotonic = time.monotonic()
        self._status(
            "arm_demo_playback_started",
            name=self.playback_name,
            keyframe_count=len(keyframes),
            original_waypoint_count=len(recording.waypoints),
        )

    def _action_stop(self, command_id: str, _: Mapping[str, Any]) -> None:
        self.stop_pub.publish(Empty())
        self._clear_motion()
        self._clear_playback()
        self._result(command_id, "arm_demo_motion_stopped")

    def _start_motion(
        self, command_id: str, q: Q, label: str, for_playback: bool
    ) -> None:
        if not self.allow_motion_commands:
            raise ValueError("motion commands are disabled")
        if self.pending_motion_q is not None:
            raise ValueError("another motion is active")
        if not all(math.isfinite(value) for value in q):
            raise ValueError("motion q contains a non-finite value")
        goal = JointState()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.name = list(JOINT_NAMES)
        goal.position = list(q)
        self.pending_motion_q = q
        self.pending_motion_command_id = command_id
        self.pending_motion_label = label
        self.pending_motion_started = time.monotonic()
        self.pending_motion_validated = False
        self.pending_motion_for_playback = for_playback
        self.joint_goal_pub.publish(goal)
        self._status("arm_demo_motion_commanded", label=label, q=list(q))

    def _clear_motion(self) -> None:
        self.pending_motion_q = None
        self.pending_motion_command_id = ""
        self.pending_motion_label = ""
        self.pending_motion_started = 0.0
        self.pending_motion_validated = False
        self.pending_motion_for_playback = False

    def _clear_playback(self) -> None:
        self.playback_name = ""
        self.playback_command_id = ""
        self.playback_waypoints = []
        self.playback_index = 0
        self.playback_due_monotonic = 0.0

    def _state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        if all(name in values for name in JOINT_NAMES):
            candidate = tuple(float(values[name]) for name in JOINT_NAMES)
            if all(math.isfinite(value) for value in candidate):
                self.current_q = candidate  # type: ignore[assignment]
                self.have_state = True
                self.last_state_monotonic = time.monotonic()

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
            playback = self.pending_motion_for_playback
            self._clear_motion()
            if playback:
                name = self.playback_name
                self._clear_playback()
                self._result(
                    command_id,
                    "arm_demo_playback_rejected",
                    False,
                    name=name,
                    label=label,
                    validator=dict(payload),
                )
            else:
                self._result(
                    command_id,
                    "arm_demo_motion_rejected",
                    False,
                    label=label,
                    validator=dict(payload),
                )
            return
        if event == "goal_validated":
            raw = payload.get("goal")
            if isinstance(raw, list) and len(raw) == 3:
                candidate = tuple(float(item) for item in raw)
                if _q_close(candidate, self.pending_motion_q):
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
            playback = self.pending_motion_for_playback
            self._clear_motion()
            if playback:
                name = self.playback_name
                self._clear_playback()
                self._result(
                    command_id,
                    "arm_demo_playback_failed",
                    False,
                    name=name,
                    label=label,
                    bridge=dict(payload),
                )
            else:
                self._result(
                    command_id,
                    "arm_demo_motion_failed",
                    False,
                    label=label,
                    bridge=dict(payload),
                )
            return
        if event != "trajectory_completed":
            return
        command_id = self.pending_motion_command_id
        label = self.pending_motion_label
        playback = self.pending_motion_for_playback
        self._clear_motion()
        if playback:
            self.playback_index += 1
            if self.playback_index >= len(self.playback_waypoints):
                name = self.playback_name
                count = len(self.playback_waypoints)
                self._clear_playback()
                self._result(
                    command_id,
                    "arm_demo_playback_completed",
                    name=name,
                    keyframe_count=count,
                )
                self._status("arm_demo_playback_idle")
            else:
                previous = self.playback_waypoints[self.playback_index - 1]
                current = self.playback_waypoints[self.playback_index]
                recorded_delay = max(0.0, current.t_sec - previous.t_sec)
                self.playback_due_monotonic = time.monotonic() + min(
                    1.0, recorded_delay / self.playback_speed_scale
                )
        else:
            self._result(
                command_id,
                "arm_demo_motion_completed",
                label=label,
                q=list(self.current_q),
            )

    def _timer_callback(self) -> None:
        now = time.monotonic()
        if self.sampler and self.sampler.active and not self.sampler.paused:
            self.sampler.add(now, self.current_q)
            if self.sampler.elapsed(now) >= self.sampler.max_duration_sec:
                details = self._finish_recording(save=True)
                self._status("arm_demo_recording_auto_stopped", **details)

        if self.pending_motion_q is not None:
            timeout = float(self.get_parameter("motion_timeout_sec").value)
            if now - self.pending_motion_started > timeout:
                command_id = self.pending_motion_command_id
                label = self.pending_motion_label
                playback = self.pending_motion_for_playback
                self.stop_pub.publish(Empty())
                self._clear_motion()
                if playback:
                    name = self.playback_name
                    self._clear_playback()
                    self._result(
                        command_id,
                        "arm_demo_playback_timeout",
                        False,
                        name=name,
                        label=label,
                    )
                else:
                    self._result(
                        command_id,
                        "arm_demo_motion_timeout",
                        False,
                        label=label,
                    )
            return

        if self.playback_name and self.playback_index < len(self.playback_waypoints):
            if now >= self.playback_due_monotonic:
                waypoint = self.playback_waypoints[self.playback_index]
                self._start_motion(
                    self.playback_command_id,
                    waypoint.q,
                    f"playback:{self.playback_name}:{self.playback_index}",
                    True,
                )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ArmDemoRecorderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
