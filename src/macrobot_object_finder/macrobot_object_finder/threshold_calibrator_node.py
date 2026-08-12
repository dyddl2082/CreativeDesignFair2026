"""Explicit, operator-confirmed field calibration for DINOv2 thresholds.

This node never lowers thresholds during normal search.  Calibration starts only
from an explicit command stating that the requested object is currently visible.
It observes all embedding candidates, tracks one spatially consistent target
candidate per frame, treats the remaining candidates as field negatives, and
refuses to apply a recommendation when the score distributions overlap.
"""

from __future__ import annotations

from collections import defaultdict
import json
import math
from pathlib import Path
import time
from typing import Any, DefaultDict, Optional

from macrobot_interfaces.msg import EmbeddingRetrievalResult
import rclpy
from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue
from rcl_interfaces.srv import SetParameters
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

from .threshold_core import (
    ScoreSample,
    ThresholdProfileStore,
    recommend_thresholds,
    split_target_and_negative,
)


class ThresholdCalibratorNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_threshold_calibrator")
        self._declare_parameters()

        reliable = QoSProfile(depth=50)
        reliable.reliability = ReliabilityPolicy.RELIABLE
        target_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.command_sub = self.create_subscription(
            String,
            str(self.get_parameter("command_topic").value),
            self._command_callback,
            reliable,
        )
        self.result_sub = self.create_subscription(
            EmbeddingRetrievalResult,
            str(self.get_parameter("embedding_result_topic").value),
            self._embedding_callback,
            reliable,
        )
        self.target_sub = self.create_subscription(
            String,
            str(self.get_parameter("active_target_topic").value),
            self._active_target_callback,
            target_qos,
        )
        self.candidate_target_pub = self.create_publisher(
            String,
            str(self.get_parameter("candidate_filter_target_topic").value),
            target_qos,
        )
        self.embedding_target_pub = self.create_publisher(
            String,
            str(self.get_parameter("embedding_target_topic").value),
            target_qos,
        )
        self.status_pub = self.create_publisher(
            String,
            str(self.get_parameter("status_topic").value),
            10,
        )
        self.result_pub = self.create_publisher(
            String,
            str(self.get_parameter("result_topic").value),
            10,
        )
        self.set_parameter_client = self.create_client(
            SetParameters,
            str(self.get_parameter("embedding_set_parameters_service").value),
        )

        self.store = ThresholdProfileStore(
            str(self.get_parameter("profile_file").value)
        )
        self.active = False
        self.object_name = ""
        self.environment_id = "default"
        self.apply_requested = False
        self.started_monotonic = 0.0
        self.deadline_monotonic = 0.0
        self.frames: DefaultDict[int, list[ScoreSample]] = defaultdict(list)
        self.received = 0
        self.last_active_target = ""
        self.pending_application: Optional[dict[str, Any]] = None

        self.timer = self.create_timer(0.1, self._timer_callback)
        self._publish_status("ready")
        self.get_logger().info(
            "Threshold calibrator ready. It is inactive during normal search and "
            "requires an explicit operator-confirmed calibration command."
        )

    def _declare_parameters(self) -> None:
        defaults = {
            "command_topic": "/object_finder/calibration/command",
            "status_topic": "/object_finder/calibration/status",
            "result_topic": "/object_finder/calibration/result",
            "embedding_result_topic": "/embedding_retrieval/results",
            "active_target_topic": "/macrobot/pick/active_target",
            "candidate_filter_target_topic": "/candidate_filter/target",
            "embedding_target_topic": "/embedding_retrieval/target",
            "embedding_set_parameters_service": "/embedding_retrieval/set_parameters",
            "profile_file": "~/MacRobot/data/perception/threshold_profiles.yaml",
            "active_environment_id": "default",
            "default_duration_sec": 8.0,
            "minimum_duration_sec": 3.0,
            "maximum_duration_sec": 30.0,
            "minimum_target_samples": 12,
            "target_low_quantile": 0.10,
            "negative_high_quantile": 0.99,
            "minimum_positive_separation": 0.03,
            "minimum_margin_separation": 0.02,
            "association_max_distance": 160.0,
            "association_score_slack": 0.18,
            "negative_exclusion_distance": 80.0,
            "auto_apply_profile_on_target": True,
            "require_localization_quality": True,
            "minimum_localization_quality": 0.15,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    @staticmethod
    def _stamp_key(message: EmbeddingRetrievalResult) -> int:
        stamp = message.proposal_header.stamp
        return int(stamp.sec) * 1_000_000_000 + int(stamp.nanosec)

    @staticmethod
    def _json(msg: String) -> dict[str, Any]:
        data = json.loads(msg.data)
        if not isinstance(data, dict):
            raise ValueError("command must be a JSON object")
        return data

    def _publish_json(self, publisher, payload: dict[str, Any]) -> None:
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        publisher.publish(message)

    def _publish_status(self, event: str, **details: Any) -> None:
        self._publish_json(
            self.status_pub,
            {
                "ok": True,
                "event": event,
                "active": self.active,
                "object_name": self.object_name,
                "environment_id": self.environment_id,
                "received_candidates": self.received,
                "frame_count": len(self.frames),
                **details,
            },
        )

    def _publish_result(self, payload: dict[str, Any]) -> None:
        self._publish_json(self.result_pub, payload)

    def _command_callback(self, message: String) -> None:
        try:
            data = self._json(message)
            action = str(data.get("action", "")).strip().lower()
            if action in {"start", "calibrate"}:
                self._start(data)
            elif action == "cancel":
                self._cancel("operator_cancel")
            elif action == "apply":
                self._apply_saved(data)
            elif action == "list":
                self.store.reload()
                self._publish_result(
                    {
                        "ok": True,
                        "event": "threshold_profiles",
                        "profiles": self.store.root.get("profiles", {}),
                        "profile_file": str(self.store.path),
                    }
                )
            elif action == "reload":
                self.store.reload()
                self._publish_result(
                    {
                        "ok": True,
                        "event": "threshold_profiles_reloaded",
                        "profile_file": str(self.store.path),
                    }
                )
            else:
                raise ValueError("action must be start, cancel, apply, list, or reload")
        except Exception as error:
            self._publish_result(
                {
                    "ok": False,
                    "event": "threshold_calibration_command_rejected",
                    "reason": str(error),
                }
            )

    def _start(self, data: dict[str, Any]) -> None:
        if self.active:
            raise ValueError("calibration_already_active")
        object_name = str(data.get("object_name", "")).strip()
        if not object_name:
            raise ValueError("object_name is required")
        confirmed_visible = bool(data.get("operator_confirms_visible", False))
        if not confirmed_visible:
            raise ValueError(
                "operator_confirms_visible=true is required; automatic threshold lowering is forbidden"
            )
        duration = float(
            data.get("duration_sec", self.get_parameter("default_duration_sec").value)
        )
        minimum = float(self.get_parameter("minimum_duration_sec").value)
        maximum = float(self.get_parameter("maximum_duration_sec").value)
        if not math.isfinite(duration) or duration < minimum or duration > maximum:
            raise ValueError(f"duration_sec must be within [{minimum}, {maximum}]")

        self.object_name = object_name
        self.environment_id = str(
            data.get(
                "environment_id",
                self.get_parameter("active_environment_id").value,
            )
        ).strip() or "default"
        self.apply_requested = bool(data.get("apply", True))
        self.started_monotonic = time.monotonic()
        self.deadline_monotonic = self.started_monotonic + duration
        self.frames.clear()
        self.received = 0
        self.active = True

        target = String()
        target.data = object_name
        self.candidate_target_pub.publish(target)
        self.embedding_target_pub.publish(target)
        self._publish_status(
            "threshold_calibration_started",
            duration_sec=duration,
            apply_requested=self.apply_requested,
            safety_note=(
                "The target candidate is inferred only inside this explicit, "
                "operator-confirmed session. Normal search never self-lowers thresholds."
            ),
        )

    def _cancel(self, reason: str) -> None:
        if not self.active:
            self._publish_status("threshold_calibration_cancel_ignored", reason="not_active")
            return
        self.active = False
        self._publish_result(
            {
                "ok": False,
                "event": "threshold_calibration_cancelled",
                "object_name": self.object_name,
                "environment_id": self.environment_id,
                "reason": reason,
                "received_candidates": self.received,
                "frame_count": len(self.frames),
            }
        )
        self._publish_status("threshold_calibration_cancelled", reason=reason)

    def _embedding_callback(self, message: EmbeddingRetrievalResult) -> None:
        if not self.active:
            return
        if str(message.target_object).strip().casefold() != self.object_name.casefold():
            return
        if not bool(message.positive_bank_available):
            return
        if bool(self.get_parameter("require_localization_quality").value):
            if not bool(message.localization_available):
                return
            if float(message.localization_quality) < float(
                self.get_parameter("minimum_localization_quality").value
            ):
                return
        center_x = (
            float(message.localized_center_x)
            if bool(message.localization_available)
            else float(message.candidate.center_x)
        )
        center_y = (
            float(message.localized_center_y)
            if bool(message.localization_available)
            else float(message.candidate.center_y)
        )
        depth_m = float(message.candidate.median_depth_m)
        if not math.isfinite(depth_m) or depth_m <= 0.0:
            depth_value: Optional[float] = None
        else:
            depth_value = depth_m
        sample = ScoreSample(
            frame_key=self._stamp_key(message),
            candidate_id=int(message.candidate_id),
            positive=float(message.positive_similarity),
            negative=float(message.negative_similarity),
            margin=float(message.margin),
            center_x=center_x,
            center_y=center_y,
            depth_m=depth_value,
            localization_quality=float(message.localization_quality),
        )
        try:
            sample.validate()
        except ValueError:
            return
        self.frames[sample.frame_key].append(sample)
        self.received += 1

    def _timer_callback(self) -> None:
        if self.active and time.monotonic() >= self.deadline_monotonic:
            self._finish()

    def _finish(self) -> None:
        self.active = False
        target, negatives = split_target_and_negative(
            self.frames,
            association_max_distance=float(
                self.get_parameter("association_max_distance").value
            ),
            score_slack=float(self.get_parameter("association_score_slack").value),
            negative_exclusion_distance=float(
                self.get_parameter("negative_exclusion_distance").value
            ),
        )
        recommendation = recommend_thresholds(
            target,
            negatives,
            target_low_quantile=float(
                self.get_parameter("target_low_quantile").value
            ),
            negative_high_quantile=float(
                self.get_parameter("negative_high_quantile").value
            ),
            minimum_positive_separation=float(
                self.get_parameter("minimum_positive_separation").value
            ),
            minimum_margin_separation=float(
                self.get_parameter("minimum_margin_separation").value
            ),
            min_target_samples=int(
                self.get_parameter("minimum_target_samples").value
            ),
        )

        payload = {
            "ok": bool(recommendation.safe_to_apply),
            "event": (
                "threshold_calibration_recommended"
                if recommendation.safe_to_apply
                else "threshold_calibration_separation_failed"
            ),
            "object_name": self.object_name,
            "environment_id": self.environment_id,
            "duration_sec": max(0.0, time.monotonic() - self.started_monotonic),
            "received_candidates": self.received,
            "frame_count": len(self.frames),
            "recommendation": recommendation.to_mapping(),
            "applied": False,
            "profile_file": str(self.store.path),
        }

        if not recommendation.safe_to_apply:
            self._publish_result(payload)
            self._publish_status(
                "threshold_calibration_separation_failed",
                reason=recommendation.reason,
            )
            return

        # Persist the recommendation even when the operator asked not to apply it.
        self.store.upsert(
            self.object_name,
            self.environment_id,
            recommendation,
            applied=False,
        )
        if self.apply_requested:
            self._apply_values(
                self.object_name,
                self.environment_id,
                recommendation.min_positive_similarity,
                recommendation.min_margin,
                payload,
            )
        else:
            self._publish_result(payload)
            self._publish_status("threshold_calibration_completed", applied=False)

    @staticmethod
    def _double_parameter(name: str, value: float) -> Parameter:
        return Parameter(
            name=name,
            value=ParameterValue(
                type=ParameterType.PARAMETER_DOUBLE,
                double_value=float(value),
            ),
        )

    @staticmethod
    def _bool_parameter(name: str, value: bool) -> Parameter:
        return Parameter(
            name=name,
            value=ParameterValue(
                type=ParameterType.PARAMETER_BOOL,
                bool_value=bool(value),
            ),
        )

    def _apply_values(
        self,
        object_name: str,
        environment_id: str,
        positive_threshold: float,
        margin_threshold: float,
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        if not self.set_parameter_client.service_is_ready():
            result = payload or {}
            result.update(
                {
                    "ok": False,
                    "event": "threshold_profile_saved_but_not_applied",
                    "object_name": object_name,
                    "environment_id": environment_id,
                    "applied": False,
                    "reason": "embedding_set_parameters_service_unavailable",
                }
            )
            self._publish_result(result)
            return
        request = SetParameters.Request()
        request.parameters = [
            self._double_parameter("min_positive_similarity", positive_threshold),
            self._double_parameter("min_margin", margin_threshold),
            self._bool_parameter("enforce_thresholds", True),
        ]
        self.pending_application = {
            "payload": dict(payload or {}),
            "object_name": object_name,
            "environment_id": environment_id,
            "positive_threshold": positive_threshold,
            "margin_threshold": margin_threshold,
        }
        future = self.set_parameter_client.call_async(request)
        future.add_done_callback(self._apply_done)

    def _apply_done(self, future) -> None:
        pending = self.pending_application or {}
        self.pending_application = None
        payload = dict(pending.get("payload", {}))
        try:
            response = future.result()
            results = list(response.results)
            success = bool(results) and all(bool(item.successful) for item in results)
            reasons = [str(item.reason) for item in results if not bool(item.successful)]
        except Exception as error:
            success = False
            reasons = [str(error)]
        payload.update(
            {
                "ok": success,
                "event": (
                    "threshold_profile_applied"
                    if success
                    else "threshold_profile_apply_failed"
                ),
                "object_name": pending.get("object_name", ""),
                "environment_id": pending.get("environment_id", "default"),
                "applied": success,
                "reason": "; ".join(reasons),
            }
        )
        if success:
            profile = self.store.get(
                str(pending.get("object_name", "")),
                str(pending.get("environment_id", "default")),
            )
            if profile:
                # Update the persisted applied flag without changing calibrated values.
                calibration = profile.setdefault("calibration", {})
                calibration["applied"] = True
                object_name = str(pending.get("object_name", "")).strip()
                environment_id = str(pending.get("environment_id", "default")).strip() or "default"
                profiles = self.store.root.setdefault("profiles", {})
                object_data = profiles.setdefault(object_name, {})
                environments = object_data.setdefault("environments", {})
                environments[environment_id] = profile
                self.store.save()
        self._publish_result(payload)
        self._publish_status(payload["event"], applied=success)

    def _apply_saved(self, data: dict[str, Any]) -> None:
        object_name = str(data.get("object_name", "")).strip()
        if not object_name:
            raise ValueError("object_name is required")
        environment_id = str(
            data.get(
                "environment_id",
                self.get_parameter("active_environment_id").value,
            )
        ).strip() or "default"
        self.store.reload()
        profile = self.store.get(object_name, environment_id)
        if profile is None:
            raise ValueError("threshold_profile_not_found")
        embedding = profile.get("embedding", {})
        self._apply_values(
            object_name,
            environment_id,
            float(embedding["min_positive_similarity"]),
            float(embedding["min_margin"]),
            {
                "ok": True,
                "event": "threshold_profile_apply_requested",
                "profile": profile,
                "profile_file": str(self.store.path),
            },
        )

    def _active_target_callback(self, message: String) -> None:
        target = message.data.strip()
        if not target or target == self.last_active_target:
            return
        self.last_active_target = target
        if not bool(self.get_parameter("auto_apply_profile_on_target").value):
            return
        environment_id = str(
            self.get_parameter("active_environment_id").value
        ).strip() or "default"
        try:
            self.store.reload()
            profile = self.store.get(target, environment_id)
            if profile is None:
                self._publish_status(
                    "threshold_profile_not_found_for_target",
                    target=target,
                    environment_id=environment_id,
                )
                return
            embedding = profile.get("embedding", {})
            self._apply_values(
                target,
                environment_id,
                float(embedding["min_positive_similarity"]),
                float(embedding["min_margin"]),
                {
                    "ok": True,
                    "event": "threshold_profile_auto_apply_requested",
                    "profile": profile,
                },
            )
        except Exception as error:
            self._publish_status(
                "threshold_profile_auto_apply_failed",
                target=target,
                reason=str(error),
            )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ThresholdCalibratorNode()
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
