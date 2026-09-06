"""Integrated camera-authoritative grasp teaching CLI.

One robust RGB-D reference is locked before the arm occludes the object.  The
same point and axial orientation are used for all five semantic keyframes and
for the stored grasp docking profile.  This removes the former mismatch between
separately recorded keyframes, close-range position and Pico odometry.
"""

from __future__ import annotations

import argparse
from collections import deque
import json
import math
import sys
import time
import uuid
from typing import Any, Callable, Deque, Dict, Mapping, Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .camera_teach_core import (
    CameraReferenceSample,
    CameraTeachingReference,
    aggregate_camera_reference,
    sample_from_localized_payload,
)


STAGES = ("OPEN", "PRE_GRASP", "GRASP_OPEN", "CLOSE", "LIFT")


class CameraGraspTeachClient(Node):
    def __init__(self) -> None:
        super().__init__("camera_grasp_teach_cli")
        self.finder_goal_pub = self.create_publisher(
            String, "/object_finder/goal", 10
        )
        self.finder_cancel_pub = self.create_publisher(
            String, "/object_finder/cancel", 10
        )
        self.keyframe_pub = self.create_publisher(
            String, "/macrobot/grasp_keyframes/command", 10
        )
        self.stored_record_pub = self.create_publisher(
            String, "/macrobot/stored_pick/record", 10
        )

        self.keyframe_results: Dict[str, Dict[str, Any]] = {}
        self.stored_results: Dict[str, Dict[str, Any]] = {}
        self.stored_status: Dict[str, Dict[str, Any]] = {}
        self.finder_status: Dict[str, Dict[str, Any]] = {}
        self.reference_samples: Deque[CameraReferenceSample] = deque(maxlen=128)
        self.target_object = ""
        self.reference_collection_not_before_sec = 0.0

        self.create_subscription(
            String,
            "/macrobot/grasp_keyframes/result",
            self._keyframe_result_callback,
            20,
        )
        self.create_subscription(
            String,
            "/macrobot/stored_pick/result",
            self._stored_result_callback,
            20,
        )
        self.create_subscription(
            String,
            "/macrobot/stored_pick/status",
            self._stored_status_callback,
            20,
        )
        self.create_subscription(
            String,
            "/object_finder/status",
            self._finder_status_callback,
            20,
        )
        self.create_subscription(
            String,
            "/macrobot/perception/localized_detection",
            self._localized_detection_callback,
            50,
        )

    @staticmethod
    def _decode(message: String) -> Optional[Dict[str, Any]]:
        try:
            payload = json.loads(message.data)
        except Exception:
            return None
        return payload if isinstance(payload, dict) else None

    @staticmethod
    def _publish(publisher, payload: object) -> None:
        message = String()
        message.data = (
            payload
            if isinstance(payload, str)
            else json.dumps(payload, ensure_ascii=False)
        )
        publisher.publish(message)

    def _keyframe_result_callback(self, message: String) -> None:
        payload = self._decode(message)
        if payload is None:
            return
        command_id = str(payload.get("command_id", ""))
        if command_id:
            self.keyframe_results[command_id] = payload

    def _stored_result_callback(self, message: String) -> None:
        payload = self._decode(message)
        if payload is None:
            return
        request_id = str(payload.get("request_id", ""))
        if request_id:
            self.stored_results[request_id] = payload

    def _stored_status_callback(self, message: String) -> None:
        payload = self._decode(message)
        if payload is None:
            return
        request_id = str(payload.get("request_id", ""))
        if request_id:
            self.stored_status[request_id] = payload

    def _finder_status_callback(self, message: String) -> None:
        payload = self._decode(message)
        if payload is None:
            return
        request_id = str(payload.get("request_id", ""))
        if request_id:
            self.finder_status[request_id] = payload

    def _localized_detection_callback(self, message: String) -> None:
        if not self.target_object:
            return
        payload = self._decode(message)
        if payload is None:
            return
        try:
            sample = sample_from_localized_payload(
                payload,
                expected_object=self.target_object,
            )
        except (TypeError, ValueError):
            return
        # Only retain recently published samples.  The source camera stamp may
        # legitimately be older because DINO/temporal confirmation crosses DDS.
        if sample.published_stamp_sec > 0.0:
            age = time.time() - sample.published_stamp_sec
            if not math.isfinite(age) or age < -1.0 or age > 5.0:
                return
            if (
                self.reference_collection_not_before_sec > 0.0
                and sample.published_stamp_sec
                < self.reference_collection_not_before_sec
            ):
                return
        self.reference_samples.append(sample)

    def _spin_until(
        self,
        predicate: Callable[[], bool],
        *,
        timeout_sec: float,
    ) -> bool:
        deadline = time.monotonic() + max(0.1, float(timeout_sec))
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
            if predicate():
                return True
        return bool(predicate())

    def _wait_for_subscriber(self, publisher, timeout_sec: float = 5.0) -> None:
        if not self._spin_until(
            lambda: publisher.get_subscription_count() > 0,
            timeout_sec=timeout_sec,
        ):
            raise RuntimeError("required ROS command subscriber was not discovered")

    def keyframe_command(
        self,
        action: str,
        *,
        timeout_sec: float = 30.0,
        **fields: Any,
    ) -> Dict[str, Any]:
        self._wait_for_subscriber(self.keyframe_pub)
        command_id = f"camera-teach-{action}-{uuid.uuid4().hex[:10]}"
        payload = {"action": action, "command_id": command_id, **fields}
        self.keyframe_results.pop(command_id, None)
        self._publish(self.keyframe_pub, payload)
        if not self._spin_until(
            lambda: command_id in self.keyframe_results,
            timeout_sec=timeout_sec,
        ):
            raise RuntimeError(f"keyframe command timed out: {action}")
        result = self.keyframe_results.pop(command_id)
        if result.get("ok") is not True:
            raise RuntimeError(
                f"keyframe {action} failed: {result.get('reason', result.get('event'))}"
            )
        return result

    def finder_reference(
        self,
        *,
        object_name: str,
        timeout_sec: float,
        rebuild_banks: bool,
        minimum_count: int,
        maximum_point_radius_m: float,
        minimum_orientation_quality: float,
        maximum_orientation_spread_deg: float,
    ) -> CameraTeachingReference:
        self._wait_for_subscriber(self.finder_goal_pub, timeout_sec=8.0)
        self.target_object = object_name
        self.reference_samples.clear()
        self.reference_collection_not_before_sec = time.time()
        request_id = f"camera-teach-find-{uuid.uuid4().hex[:10]}"
        goal = {
            "object_name": object_name,
            "request_id": request_id,
            "timeout_sec": max(60.0, float(timeout_sec)),
            "continuous": True,
            "rebuild_banks": bool(rebuild_banks),
            "min_score": 0.0,
        }
        deadline = time.monotonic() + max(1.0, float(timeout_sec))
        next_publish = 0.0
        last_error = "waiting for camera samples"
        while rclpy.ok() and time.monotonic() < deadline:
            now = time.monotonic()
            status = self.finder_status.get(request_id, {})
            event = str(status.get("event", "")).strip().casefold()
            if event == "target_switch_failed":
                raise RuntimeError(
                    f"finder target switch failed: {status.get('reason', '')}"
                )
            if now >= next_publish and event not in {
                "target_ready",
                "object_found",
            }:
                self._publish(self.finder_goal_pub, goal)
                next_publish = now + 0.75
            rclpy.spin_once(self, timeout_sec=0.1)
            try:
                reference = aggregate_camera_reference(
                    self.reference_samples,
                    minimum_count=minimum_count,
                    maximum_point_radius_m=maximum_point_radius_m,
                    minimum_localization_quality=0.15,
                    maximum_depth_std_m=0.035,
                    maximum_center_std_px=20.0,
                    minimum_orientation_quality=minimum_orientation_quality,
                    maximum_orientation_spread_deg=maximum_orientation_spread_deg,
                )
                return reference
            except ValueError as error:
                last_error = str(error)
        raise RuntimeError(
            "camera teaching reference acquisition timed out: " + last_error
        )

    def cancel_finder(self, reason: str = "camera_teaching_reference_locked") -> None:
        self._publish(self.finder_cancel_pub, reason)
        self.target_object = ""

    def lock_reference(
        self,
        *,
        keyframe_profile: str,
        object_name: str,
        reference: CameraTeachingReference,
    ) -> Dict[str, Any]:
        return self.keyframe_command(
            "lock_reference",
            profile=keyframe_profile,
            object_name=object_name,
            object_point_base=list(reference.point_base),
            object_orientation=reference.orientation_mapping(),
            reference_metadata={
                "localization": {
                    "quality": reference.localization_quality,
                    "method": "multi_frame_camera_teaching",
                },
                "score": reference.score,
                "depth_std_m": reference.depth_std_m,
                "center_std_px": reference.center_std_px,
                "point_radius_m": reference.point_radius_m,
                "orientation_spread_deg": reference.orientation_spread_deg,
                "sample_count": reference.sample_count,
            },
        )

    def reference_status(self, keyframe_profile: str) -> Dict[str, Any]:
        result = self.keyframe_command(
            "reference_status",
            profile=keyframe_profile,
        )
        reference = result.get("reference")
        if result.get("locked") is not True or not isinstance(reference, Mapping):
            raise RuntimeError(
                "no locked camera reference; run camera_grasp_teach_cli start first"
            )
        return dict(reference)

    def capture(
        self,
        *,
        keyframe_profile: str,
        object_name: str,
        stage: str,
    ) -> Dict[str, Any]:
        return self.keyframe_command(
            "capture",
            profile=keyframe_profile,
            object_name=object_name,
            stage=stage,
            timeout_sec=30.0,
        )

    def finalize(self, keyframe_profile: str) -> Dict[str, Any]:
        return self.keyframe_command(
            "finalize",
            profile=keyframe_profile,
            timeout_sec=30.0,
        )

    def delete_keyframes(self, keyframe_profile: str) -> None:
        """Delete an old keyframe profile; an already-missing profile is success."""
        self._wait_for_subscriber(self.keyframe_pub)
        command_id = f"camera-teach-delete-{uuid.uuid4().hex[:10]}"
        payload = {
            "action": "delete",
            "command_id": command_id,
            "profile": keyframe_profile,
        }
        self.keyframe_results.pop(command_id, None)
        self._publish(self.keyframe_pub, payload)
        if not self._spin_until(
            lambda: command_id in self.keyframe_results,
            timeout_sec=10.0,
        ):
            raise RuntimeError("keyframe delete command timed out")
        result = self.keyframe_results.pop(command_id)
        if str(result.get("event", "")) != "grasp_keyframe_profile_deleted":
            raise RuntimeError(
                "unexpected keyframe delete result: "
                + str(result.get("event", result))
            )

    def commit_runtime_profile(
        self,
        *,
        object_name: str,
        runtime_profile: str,
        keyframe_profile: str,
        reference: Mapping[str, Any],
        maximum_grasp_range_m: float,
        timeout_sec: float,
    ) -> Dict[str, Any]:
        self._wait_for_subscriber(self.stored_record_pub)
        point = reference.get("point_base")
        orientation = reference.get("object_orientation", {})
        if not isinstance(point, (list, tuple)) or len(point) != 3:
            raise RuntimeError("locked reference does not contain point_base")
        if not isinstance(orientation, Mapping):
            raise RuntimeError("locked reference does not contain object_orientation")
        request_id = f"camera-teach-commit-{uuid.uuid4().hex[:10]}"
        payload = {
            "request_id": request_id,
            "record_stage": "camera_grasp",
            "object_name": object_name,
            "profile": runtime_profile,
            "grasp_keyframe_profile": keyframe_profile,
            "pick_profile": object_name,
            "object_point_base": [float(value) for value in point],
            "object_orientation": dict(orientation),
            "score": float(reference.get("score", 0.0) or 0.0),
            "graspable_max_range_m": float(maximum_grasp_range_m),
            "require_orientation_match": True,
        }
        self.stored_results.pop(request_id, None)
        deadline = time.monotonic() + max(1.0, float(timeout_sec))
        next_publish = 0.0
        while rclpy.ok() and time.monotonic() < deadline:
            now = time.monotonic()
            if now >= next_publish:
                self._publish(self.stored_record_pub, payload)
                next_publish = now + 0.75
            rclpy.spin_once(self, timeout_sec=0.1)
            if request_id in self.stored_results:
                result = self.stored_results.pop(request_id)
                if result.get("ok") is not True:
                    raise RuntimeError(
                        "camera grasp profile commit failed: "
                        + str(result.get("reason", result.get("event")))
                    )
                return result
        raise RuntimeError("camera grasp profile commit timed out")

    def preflight(
        self,
        *,
        object_name: str,
        keyframe_profile: str,
        reference: Mapping[str, Any],
        timeout_sec: float,
    ) -> Dict[str, Any]:
        point = reference.get("point_base")
        orientation = reference.get("object_orientation", {})
        orientation_reference = (
            dict(orientation)
            if isinstance(orientation, Mapping)
            else {}
        )
        orientation_reference["source"] = (
            "integrated_camera_grasp_teaching"
        )
        return self.keyframe_command(
            "preflight",
            profile=keyframe_profile,
            object_name=object_name,
            object_point_base=point,
            object_orientation=orientation,
            orientation_reference=orientation_reference,
            timeout_sec=timeout_sec,
        )


def _common_start_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("object_name")
    parser.add_argument("--profile", default="")
    parser.add_argument("--keyframes", default="")
    parser.add_argument("--replace-keyframes", action="store_true")
    parser.add_argument("--rebuild-banks", action="store_true")
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--position-radius", type=float, default=0.008)
    parser.add_argument("--min-orientation-quality", type=float, default=0.45)
    parser.add_argument("--orientation-spread", type=float, default=8.0)
    parser.add_argument("--timeout", type=float, default=120.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Record the camera grasp position and semantic keyframes from one "
            "shared RGB-D reference"
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    _common_start_arguments(start)

    capture = sub.add_parser("capture")
    capture.add_argument("object_name")
    capture.add_argument("stage", choices=STAGES)
    capture.add_argument("--keyframes", default="")
    capture.add_argument("--timeout", type=float, default=30.0)

    finish = sub.add_parser("finish")
    finish.add_argument("object_name")
    finish.add_argument("--profile", default="")
    finish.add_argument("--keyframes", default="")
    finish.add_argument("--max-grasp-range", type=float, default=0.30)
    finish.add_argument("--skip-preflight", action="store_true")
    finish.add_argument("--timeout", type=float, default=120.0)

    interactive = sub.add_parser("interactive")
    _common_start_arguments(interactive)
    interactive.add_argument("--max-grasp-range", type=float, default=0.30)
    interactive.add_argument("--skip-preflight", action="store_true")

    status = sub.add_parser("status")
    status.add_argument("--keyframes", required=True)

    abort = sub.add_parser("abort")
    abort.add_argument("--keyframes", default="")
    return parser


def _names(args: argparse.Namespace) -> tuple[str, str, str]:
    object_name = str(args.object_name).strip()
    runtime_profile = str(getattr(args, "profile", "") or object_name).strip()
    keyframe_profile = str(
        getattr(args, "keyframes", "") or f"{object_name}_r4"
    ).strip()
    return object_name, runtime_profile, keyframe_profile


def _print(payload: Mapping[str, Any]) -> None:
    print(json.dumps(dict(payload), ensure_ascii=False, indent=2), flush=True)


def _start_session(
    node: CameraGraspTeachClient,
    args: argparse.Namespace,
) -> tuple[str, str, str, CameraTeachingReference]:
    object_name, runtime_profile, keyframe_profile = _names(args)
    if args.replace_keyframes:
        node.delete_keyframes(keyframe_profile)
    print(
        "물체와 차체를 실제로 잘 잡히는 위치에 고정하고, "
        "카메라에서 물체 전체가 보이게 두십시오.",
        flush=True,
    )
    reference = node.finder_reference(
        object_name=object_name,
        timeout_sec=float(args.timeout),
        rebuild_banks=bool(args.rebuild_banks),
        minimum_count=max(3, int(args.samples)),
        maximum_point_radius_m=float(args.position_radius),
        minimum_orientation_quality=float(args.min_orientation_quality),
        maximum_orientation_spread_deg=float(args.orientation_spread),
    )
    lock_result = node.lock_reference(
        keyframe_profile=keyframe_profile,
        object_name=object_name,
        reference=reference,
    )
    node.cancel_finder()
    _print(
        {
            "ok": True,
            "event": "camera_grasp_teaching_started",
            "object_name": object_name,
            "runtime_profile": runtime_profile,
            "keyframe_profile": keyframe_profile,
            "camera_reference": reference.to_mapping(),
            "lock_result": lock_result,
        }
    )
    return object_name, runtime_profile, keyframe_profile, reference


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    rclpy.init()
    node = CameraGraspTeachClient()
    exit_code = 0
    try:
        if args.command == "start":
            _start_session(node, args)

        elif args.command == "capture":
            object_name = str(args.object_name).strip()
            keyframes = str(args.keyframes or f"{object_name}_r4").strip()
            result = node.capture(
                keyframe_profile=keyframes,
                object_name=object_name,
                stage=str(args.stage),
            )
            _print(result)

        elif args.command == "status":
            _print(node.reference_status(str(args.keyframes)))

        elif args.command == "abort":
            if args.keyframes:
                result = node.keyframe_command(
                    "clear_reference",
                    profile=str(args.keyframes),
                    timeout_sec=10.0,
                )
                _print(result)
            node.cancel_finder("camera_teaching_aborted")

        elif args.command == "finish":
            object_name, runtime_profile, keyframe_profile = _names(args)
            reference = node.reference_status(keyframe_profile)
            finalize_result = node.finalize(keyframe_profile)
            commit_result = node.commit_runtime_profile(
                object_name=object_name,
                runtime_profile=runtime_profile,
                keyframe_profile=keyframe_profile,
                reference=reference,
                maximum_grasp_range_m=float(args.max_grasp_range),
                timeout_sec=float(args.timeout),
            )
            preflight_result = None
            if not args.skip_preflight:
                preflight_result = node.preflight(
                    object_name=object_name,
                    keyframe_profile=keyframe_profile,
                    reference=reference,
                    timeout_sec=min(60.0, float(args.timeout)),
                )
            _print(
                {
                    "ok": True,
                    "event": "camera_grasp_teaching_completed",
                    "reference": reference,
                    "finalize": finalize_result,
                    "runtime_profile": commit_result,
                    "preflight": preflight_result,
                }
            )

        elif args.command == "interactive":
            object_name, runtime_profile, keyframe_profile, _ = _start_session(
                node, args
            )
            print(
                "별도 터미널의 arm_demo_cli로 자세를 맞춘 뒤, "
                "이 터미널에서 Enter를 누르십시오.",
                flush=True,
            )
            for stage in STAGES:
                answer = input(
                    f"[{stage}] 자세를 맞췄으면 Enter, 중단은 q 입력: "
                ).strip().casefold()
                if answer in {"q", "quit", "abort", "stop"}:
                    raise KeyboardInterrupt
                result = node.capture(
                    keyframe_profile=keyframe_profile,
                    object_name=object_name,
                    stage=stage,
                )
                _print(result)

            reference = node.reference_status(keyframe_profile)
            finalize_result = node.finalize(keyframe_profile)
            commit_result = node.commit_runtime_profile(
                object_name=object_name,
                runtime_profile=runtime_profile,
                keyframe_profile=keyframe_profile,
                reference=reference,
                maximum_grasp_range_m=float(args.max_grasp_range),
                timeout_sec=float(args.timeout),
            )
            preflight_result = None
            if not args.skip_preflight:
                preflight_result = node.preflight(
                    object_name=object_name,
                    keyframe_profile=keyframe_profile,
                    reference=reference,
                    timeout_sec=min(60.0, float(args.timeout)),
                )
            _print(
                {
                    "ok": True,
                    "event": "camera_grasp_teaching_completed",
                    "object_name": object_name,
                    "runtime_profile": runtime_profile,
                    "keyframe_profile": keyframe_profile,
                    "reference": reference,
                    "finalize": finalize_result,
                    "commit": commit_result,
                    "preflight": preflight_result,
                }
            )

    except KeyboardInterrupt:
        exit_code = 130
        try:
            node.cancel_finder("camera_teaching_interrupted")
        except Exception:
            pass
        print("Camera grasp teaching interrupted.", file=sys.stderr)
    except Exception as error:
        exit_code = 1
        try:
            node.cancel_finder("camera_teaching_failed")
        except Exception:
            pass
        print(f"ERROR: {error}", file=sys.stderr)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
