#!/usr/bin/env python3
"""Cable-clutter aware refiner for MacRobot depth candidates.

This node is intentionally placed between the depth proposal node and the RGB
crop node:

    /depth_candidates/raw_candidates
        -> candidate_refiner_node
        -> /depth_candidates/candidates
        -> rgb_candidate_crop_node

It does not subscribe to RGB/depth images.  If the DepthCandidateArray carries a
foreground mask, it uses that small mask metadata to reject sparse cable-like
boxes and to expand surviving boxes so small objects such as Buds3 are not cut
by tight depth components.
"""

from __future__ import annotations

import copy
import json
import math
import time
from dataclasses import dataclass
from typing import Any

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import RegionOfInterest
from std_msgs.msg import String

from macrobot_interfaces.msg import DepthCandidateArray

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - OpenCV should exist on the Pi runtime.
    cv2 = None

try:
    from cv_bridge import CvBridge  # type: ignore
except Exception:  # pragma: no cover
    CvBridge = None


@dataclass
class CandidateMetrics:
    width: int
    height: int
    area: int
    image_area_ratio: float
    aspect_ratio: float
    depth_m: float
    proposal_score: float
    fill_ratio: float | None
    mask_component_count: int | None
    largest_component_aspect_ratio: float | None
    largest_component_area_ratio: float | None
    touches_border: bool


@dataclass
class Decision:
    accepted: bool
    reason: str
    score: float
    metrics: CandidateMetrics


class CandidateRefinerNode(Node):
    def __init__(self) -> None:
        super().__init__("candidate_refiner")

        self._declare_parameters()

        self.input_topic = str(self.get_parameter("input_topic").value)
        self.output_topic = str(self.get_parameter("output_topic").value)
        self.status_topic = str(self.get_parameter("status_topic").value)

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.publisher = self.create_publisher(DepthCandidateArray, self.output_topic, qos)
        self.status_publisher = self.create_publisher(String, self.status_topic, 10)
        self.subscription = self.create_subscription(
            DepthCandidateArray,
            self.input_topic,
            self._callback,
            qos,
        )

        self.bridge = CvBridge() if CvBridge is not None else None
        self._last_status_monotonic = 0.0
        self._frames = 0
        self._accepted_total = 0
        self._rejected_total = 0
        self._reason_counts: dict[str, int] = {}

        self.get_logger().info(
            "Cable-aware candidate refiner: "
            f"{self.input_topic} -> {self.output_topic}"
        )

    def _declare_parameters(self) -> None:
        params: dict[str, Any] = {
            "input_topic": "/depth_candidates/raw_candidates",
            "output_topic": "/depth_candidates/candidates",
            "status_topic": "/depth_candidates/refiner_status",
            "status_period_sec": 3.0,
            # Depth gate.  This should be close to the actual manipulation range.
            "min_depth_m": 0.20,
            "max_depth_m": 0.85,
            # ROI size gate.
            "min_bbox_width_px": 8,
            "min_bbox_height_px": 8,
            "max_bbox_width_px": 260,
            "max_bbox_height_px": 220,
            "max_bbox_area_ratio": 0.25,
            "reject_border_candidates": True,
            "border_margin_px": 2,
            # Cable/sparse geometry rejection.
            "max_bbox_aspect_ratio": 4.8,
            "min_fill_ratio": 0.055,
            "large_bbox_area_px": 9000,
            "large_bbox_min_fill_ratio": 0.12,
            "max_sparse_component_count": 4,
            "sparse_component_fill_ratio": 0.09,
            "max_largest_component_aspect_ratio": 6.0,
            "min_largest_component_area_ratio": 0.18,
            # Keep enough candidates so Buds3 is not lost when other valid objects exist.
            "max_output_candidates": 8,
            "min_refined_score": -1.0,
            # Candidate ROI expansion before the RGB cropper sees it.
            "expand_roi_px": 12,
            "expand_roi_ratio": 0.18,
            "force_square_roi": True,
            "max_expanded_side_px": 240,
            # Ranking.  A mild depth prior helps reject distant clutter without
            # depending on object identity.
            "preferred_depth_m": 0.45,
            "depth_prior_sigma_m": 0.30,
            "debug_include_candidates": True,
        }
        for name, value in params.items():
            self.declare_parameter(name, value)

    def _callback(self, message: DepthCandidateArray) -> None:
        self._frames += 1
        mask = self._extract_foreground_mask(message)
        image_width = int(getattr(message, "image_width", 0))
        image_height = int(getattr(message, "image_height", 0))
        if image_width <= 0 or image_height <= 0:
            # Try foreground mask dimensions if image_width/image_height are absent.
            if mask is not None:
                image_height, image_width = mask.shape[:2]
            else:
                self.get_logger().warning(
                    "DepthCandidateArray has no valid image dimensions; forwarding empty output"
                )
                output = self._copy_array_header(message)
                output.candidates = []
                self.publisher.publish(output)
                return

        accepted: list[tuple[float, Any, Decision]] = []
        decisions: list[Decision] = []

        for candidate in list(message.candidates):
            decision = self._evaluate_candidate(candidate, image_width, image_height, mask)
            decisions.append(decision)
            if decision.accepted:
                refined = copy.deepcopy(candidate)
                self._expand_candidate_roi(refined, image_width, image_height)
                accepted.append((decision.score, refined, decision))
            else:
                self._reason_counts[decision.reason] = self._reason_counts.get(decision.reason, 0) + 1

        accepted.sort(key=lambda item: item[0], reverse=True)
        max_output = max(1, int(self.get_parameter("max_output_candidates").value))
        min_score = float(self.get_parameter("min_refined_score").value)
        selected = [candidate for score, candidate, _ in accepted if score >= min_score][:max_output]

        output = self._copy_array_header(message)
        output.candidates = selected
        self.publisher.publish(output)

        self._accepted_total += len(selected)
        self._rejected_total += max(0, len(message.candidates) - len(selected))
        self._publish_status_if_due(message, decisions, selected_count=len(selected), mask_available=mask is not None)

    def _copy_array_header(self, message: DepthCandidateArray) -> DepthCandidateArray:
        output = DepthCandidateArray()
        # These assignments are intentionally guarded to remain compatible with
        # slightly different local message revisions.
        for field in (
            "header",
            "image_width",
            "image_height",
            "foreground_mask_available",
            "foreground_mask",
        ):
            if hasattr(message, field) and hasattr(output, field):
                try:
                    setattr(output, field, copy.deepcopy(getattr(message, field)))
                except Exception:
                    setattr(output, field, getattr(message, field))
        return output

    def _extract_foreground_mask(self, message: DepthCandidateArray) -> np.ndarray | None:
        if self.bridge is None or cv2 is None:
            return None
        if not hasattr(message, "foreground_mask_available"):
            return None
        if not bool(getattr(message, "foreground_mask_available")):
            return None
        if not hasattr(message, "foreground_mask"):
            return None
        mask_message = getattr(message, "foreground_mask")
        try:
            mask = self.bridge.imgmsg_to_cv2(mask_message, desired_encoding="passthrough")
        except Exception as exc:
            self.get_logger().debug(f"Could not decode foreground_mask: {exc}")
            return None
        if mask is None:
            return None
        mask_np = np.asarray(mask)
        if mask_np.ndim == 3:
            mask_np = mask_np[:, :, 0]
        return (mask_np > 0).astype(np.uint8) * 255

    def _evaluate_candidate(
        self,
        candidate: Any,
        image_width: int,
        image_height: int,
        mask: np.ndarray | None,
    ) -> Decision:
        metrics = self._metrics(candidate, image_width, image_height, mask)
        reason = self._reject_reason(metrics)
        score = self._score(metrics)
        return Decision(accepted=(reason == "accepted"), reason=reason, score=score, metrics=metrics)

    def _metrics(
        self,
        candidate: Any,
        image_width: int,
        image_height: int,
        mask: np.ndarray | None,
    ) -> CandidateMetrics:
        roi = candidate.roi
        x = int(roi.x_offset)
        y = int(roi.y_offset)
        w = max(0, int(roi.width))
        h = max(0, int(roi.height))
        area = int(w * h)
        image_area = max(1, int(image_width * image_height))
        aspect = max(float(w) / max(float(h), 1.0), float(h) / max(float(w), 1.0))
        depth = self._float_attr(candidate, "median_depth_m", default=math.nan)
        proposal_score = self._float_attr(candidate, "proposal_score", default=0.0)
        touches_border = bool(getattr(candidate, "touches_border", False))

        fill_ratio = self._maybe_float_attr(candidate, "fill_ratio")
        component_count: int | None = None
        largest_aspect: float | None = None
        largest_area_ratio: float | None = None

        if mask is not None and w > 0 and h > 0:
            x0 = max(0, min(x, image_width - 1))
            y0 = max(0, min(y, image_height - 1))
            x1 = max(x0 + 1, min(x + w, image_width))
            y1 = max(y0 + 1, min(y + h, image_height))
            patch = mask[y0:y1, x0:x1]
            foreground = patch > 0
            foreground_count = int(np.count_nonzero(foreground))
            patch_area = max(1, int(patch.shape[0] * patch.shape[1]))
            fill_ratio = float(foreground_count) / float(patch_area)
            if cv2 is not None and foreground_count > 0:
                n_labels, _, stats, _ = cv2.connectedComponentsWithStats(
                    foreground.astype(np.uint8),
                    connectivity=8,
                )
                component_count = max(0, int(n_labels) - 1)
                if component_count > 0:
                    # label 0 is background.
                    areas = stats[1:, cv2.CC_STAT_AREA]
                    largest_index = int(np.argmax(areas)) + 1
                    largest_area = int(stats[largest_index, cv2.CC_STAT_AREA])
                    l_w = max(1, int(stats[largest_index, cv2.CC_STAT_WIDTH]))
                    l_h = max(1, int(stats[largest_index, cv2.CC_STAT_HEIGHT]))
                    largest_aspect = max(float(l_w) / float(l_h), float(l_h) / float(l_w))
                    largest_area_ratio = float(largest_area) / float(max(1, foreground_count))

        return CandidateMetrics(
            width=w,
            height=h,
            area=area,
            image_area_ratio=float(area) / float(image_area),
            aspect_ratio=aspect,
            depth_m=depth,
            proposal_score=proposal_score,
            fill_ratio=fill_ratio,
            mask_component_count=component_count,
            largest_component_aspect_ratio=largest_aspect,
            largest_component_area_ratio=largest_area_ratio,
            touches_border=touches_border,
        )

    def _reject_reason(self, m: CandidateMetrics) -> str:
        min_depth = float(self.get_parameter("min_depth_m").value)
        max_depth = float(self.get_parameter("max_depth_m").value)
        if not math.isfinite(m.depth_m) or m.depth_m < min_depth or m.depth_m > max_depth:
            return "depth_out_of_range"

        if m.width < int(self.get_parameter("min_bbox_width_px").value):
            return "bbox_too_narrow"
        if m.height < int(self.get_parameter("min_bbox_height_px").value):
            return "bbox_too_short"
        if m.width > int(self.get_parameter("max_bbox_width_px").value):
            return "bbox_too_wide"
        if m.height > int(self.get_parameter("max_bbox_height_px").value):
            return "bbox_too_tall"
        if m.image_area_ratio > float(self.get_parameter("max_bbox_area_ratio").value):
            return "bbox_area_too_large"

        if bool(self.get_parameter("reject_border_candidates").value) and m.touches_border:
            return "touches_border"

        if m.aspect_ratio > float(self.get_parameter("max_bbox_aspect_ratio").value):
            return "bbox_aspect_cable_like"

        min_fill = float(self.get_parameter("min_fill_ratio").value)
        if m.fill_ratio is not None and m.fill_ratio < min_fill:
            return "low_fill_cable_like"

        large_area_px = int(self.get_parameter("large_bbox_area_px").value)
        large_min_fill = float(self.get_parameter("large_bbox_min_fill_ratio").value)
        if m.area >= large_area_px and m.fill_ratio is not None and m.fill_ratio < large_min_fill:
            return "large_sparse_bbox"

        if (
            m.mask_component_count is not None
            and m.fill_ratio is not None
            and m.mask_component_count > int(self.get_parameter("max_sparse_component_count").value)
            and m.fill_ratio < float(self.get_parameter("sparse_component_fill_ratio").value)
        ):
            return "many_sparse_components"

        if (
            m.largest_component_aspect_ratio is not None
            and m.largest_component_aspect_ratio
            > float(self.get_parameter("max_largest_component_aspect_ratio").value)
            and (m.largest_component_area_ratio is None or m.largest_component_area_ratio > 0.55)
        ):
            return "largest_component_line_like"

        if (
            m.largest_component_area_ratio is not None
            and m.largest_component_area_ratio
            < float(self.get_parameter("min_largest_component_area_ratio").value)
            and m.fill_ratio is not None
            and m.fill_ratio < 0.14
        ):
            return "fragmented_sparse_bbox"

        return "accepted"

    def _score(self, m: CandidateMetrics) -> float:
        score = float(m.proposal_score)
        if m.fill_ratio is not None:
            score += 0.18 * min(max(m.fill_ratio / 0.25, 0.0), 1.0)
        depth_pref = float(self.get_parameter("preferred_depth_m").value)
        sigma = max(0.05, float(self.get_parameter("depth_prior_sigma_m").value))
        if math.isfinite(m.depth_m):
            score += 0.12 * math.exp(-0.5 * ((m.depth_m - depth_pref) / sigma) ** 2)
        if m.aspect_ratio > 2.5:
            score -= 0.06 * min(m.aspect_ratio - 2.5, 4.0)
        if m.image_area_ratio > 0.08:
            score -= 0.12 * min((m.image_area_ratio - 0.08) / 0.12, 1.0)
        return score

    def _expand_candidate_roi(self, candidate: Any, image_width: int, image_height: int) -> None:
        roi = candidate.roi
        x0 = int(roi.x_offset)
        y0 = int(roi.y_offset)
        w = int(roi.width)
        h = int(roi.height)
        if w <= 0 or h <= 0:
            return
        expand_px = int(self.get_parameter("expand_roi_px").value)
        expand_ratio = float(self.get_parameter("expand_roi_ratio").value)
        pad_x = expand_px + int(round(float(w) * expand_ratio))
        pad_y = expand_px + int(round(float(h) * expand_ratio))
        x0 -= pad_x
        y0 -= pad_y
        x1 = int(roi.x_offset) + w + pad_x
        y1 = int(roi.y_offset) + h + pad_y

        if bool(self.get_parameter("force_square_roi").value):
            cx = 0.5 * float(x0 + x1)
            cy = 0.5 * float(y0 + y1)
            side = max(float(x1 - x0), float(y1 - y0))
            max_side = max(1, int(self.get_parameter("max_expanded_side_px").value))
            side = min(side, float(max_side))
            x0 = int(round(cx - 0.5 * side))
            x1 = int(round(cx + 0.5 * side))
            y0 = int(round(cy - 0.5 * side))
            y1 = int(round(cy + 0.5 * side))

        x0 = max(0, min(x0, image_width - 1))
        y0 = max(0, min(y0, image_height - 1))
        x1 = max(x0 + 1, min(x1, image_width))
        y1 = max(y0 + 1, min(y1, image_height))

        candidate.roi = RegionOfInterest(
            x_offset=int(x0),
            y_offset=int(y0),
            width=int(x1 - x0),
            height=int(y1 - y0),
            do_rectify=bool(getattr(roi, "do_rectify", False)),
        )

    def _publish_status_if_due(
        self,
        message: DepthCandidateArray,
        decisions: list[Decision],
        selected_count: int,
        mask_available: bool,
    ) -> None:
        now = time.monotonic()
        period = float(self.get_parameter("status_period_sec").value)
        if now - self._last_status_monotonic < period:
            return
        self._last_status_monotonic = now

        reason_counts: dict[str, int] = {}
        for decision in decisions:
            reason_counts[decision.reason] = reason_counts.get(decision.reason, 0) + 1

        payload: dict[str, Any] = {
            "event": "candidate_refiner_status",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "frames": self._frames,
            "source_candidate_count": len(message.candidates),
            "selected_count": selected_count,
            "mask_available": mask_available,
            "reason_counts_last_frame": reason_counts,
            "reason_counts_total": self._reason_counts,
        }
        if bool(self.get_parameter("debug_include_candidates").value):
            rows = []
            for decision in decisions[:20]:
                m = decision.metrics
                rows.append(
                    {
                        "accepted": decision.accepted,
                        "reason": decision.reason,
                        "score": round(decision.score, 4),
                        "depth_m": round(m.depth_m, 4) if math.isfinite(m.depth_m) else None,
                        "roi_wh": [m.width, m.height],
                        "aspect": round(m.aspect_ratio, 3),
                        "fill": round(m.fill_ratio, 4) if m.fill_ratio is not None else None,
                        "components": m.mask_component_count,
                        "largest_aspect": round(m.largest_component_aspect_ratio, 3)
                        if m.largest_component_aspect_ratio is not None
                        else None,
                    }
                )
            payload["candidates_last_frame"] = rows

        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        self.status_publisher.publish(msg)

    @staticmethod
    def _float_attr(obj: Any, name: str, default: float) -> float:
        try:
            return float(getattr(obj, name))
        except Exception:
            return default

    @staticmethod
    def _maybe_float_attr(obj: Any, name: str) -> float | None:
        if not hasattr(obj, name):
            return None
        try:
            return float(getattr(obj, name))
        except Exception:
            return None


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = CandidateRefinerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
