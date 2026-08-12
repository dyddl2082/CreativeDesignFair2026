"""Pure helpers for explicit per-object field threshold calibration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from pathlib import Path
import tempfile
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

import numpy as np
import yaml


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ScoreSample:
    frame_key: int
    candidate_id: int
    positive: float
    negative: float
    margin: float
    center_x: float
    center_y: float
    depth_m: Optional[float]
    localization_quality: float = 0.0

    def validate(self) -> None:
        for value in (self.positive, self.margin, self.center_x, self.center_y):
            if not math.isfinite(float(value)):
                raise ValueError("sample contains non-finite values")


@dataclass(frozen=True)
class ThresholdRecommendation:
    min_positive_similarity: float
    min_margin: float
    target_count: int
    negative_count: int
    target_positive_p10: float
    negative_positive_p99: float
    target_margin_p10: float
    negative_margin_p99: float
    positive_separation: float
    margin_separation: float
    safe_to_apply: bool
    reason: str = ""

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "min_positive_similarity": self.min_positive_similarity,
            "min_margin": self.min_margin,
            "target_count": self.target_count,
            "negative_count": self.negative_count,
            "target_positive_p10": self.target_positive_p10,
            "negative_positive_p99": self.negative_positive_p99,
            "target_margin_p10": self.target_margin_p10,
            "negative_margin_p99": self.negative_margin_p99,
            "positive_separation": self.positive_separation,
            "margin_separation": self.margin_separation,
            "safe_to_apply": self.safe_to_apply,
            "reason": self.reason,
        }


def _distance(first: ScoreSample, second: ScoreSample) -> float:
    center = math.hypot(first.center_x - second.center_x, first.center_y - second.center_y)
    if first.depth_m is None or second.depth_m is None:
        return center
    return center + 300.0 * abs(first.depth_m - second.depth_m)


def split_target_and_negative(
    frames: Mapping[int, Sequence[ScoreSample]],
    *,
    association_max_distance: float = 160.0,
    score_slack: float = 0.18,
    negative_exclusion_distance: float = 80.0,
) -> tuple[list[ScoreSample], list[ScoreSample]]:
    """Pick one spatially consistent top candidate per frame as the declared target.

    This function is only used in an operator-confirmed calibration session: the
    operator has asserted that the target is visible. Remaining candidates become
    field negatives. It must never run as an automatic threshold-lowering loop.
    """

    target: list[ScoreSample] = []
    negatives: list[ScoreSample] = []
    previous: Optional[ScoreSample] = None
    for frame_key in sorted(frames):
        candidates = [item for item in frames[frame_key] if math.isfinite(item.positive)]
        if not candidates:
            continue
        candidates.sort(key=lambda item: (item.positive + 0.5 * item.margin), reverse=True)
        best_score = candidates[0].positive + 0.5 * candidates[0].margin
        if previous is None:
            chosen = candidates[0]
        else:
            eligible = [
                item
                for item in candidates
                if item.positive + 0.5 * item.margin >= best_score - score_slack
                and _distance(previous, item) <= association_max_distance
            ]
            chosen = min(eligible, key=lambda item: _distance(previous, item)) if eligible else candidates[0]
        target.append(chosen)
        previous = chosen
        negatives.extend(
            item
            for item in candidates
            if item is not chosen
            and _distance(chosen, item) > float(negative_exclusion_distance)
        )
    return target, negatives


def recommend_thresholds(
    target_samples: Sequence[ScoreSample],
    negative_samples: Sequence[ScoreSample],
    *,
    target_low_quantile: float = 0.10,
    negative_high_quantile: float = 0.99,
    minimum_positive_separation: float = 0.03,
    minimum_margin_separation: float = 0.02,
    fallback_positive_margin: float = 0.03,
    fallback_margin_margin: float = 0.02,
    min_target_samples: int = 12,
) -> ThresholdRecommendation:
    if len(target_samples) < min_target_samples:
        return ThresholdRecommendation(
            0.0, 0.0, len(target_samples), len(negative_samples),
            -1.0, -1.0, -1.0, -1.0, 0.0, 0.0, False,
            "insufficient_target_samples",
        )
    target_positive = np.asarray([item.positive for item in target_samples], dtype=np.float64)
    target_margin = np.asarray([item.margin for item in target_samples], dtype=np.float64)
    tp10 = float(np.quantile(target_positive, target_low_quantile))
    tm10 = float(np.quantile(target_margin, target_low_quantile))

    if negative_samples:
        negative_positive = np.asarray([item.positive for item in negative_samples], dtype=np.float64)
        negative_margin = np.asarray([item.margin for item in negative_samples], dtype=np.float64)
        np99 = float(np.quantile(negative_positive, negative_high_quantile))
        nm99 = float(np.quantile(negative_margin, negative_high_quantile))
        positive_separation = tp10 - np99
        margin_separation = tm10 - nm99
        safe = (
            positive_separation >= minimum_positive_separation
            and margin_separation >= minimum_margin_separation
        )
        positive_threshold = 0.5 * (tp10 + np99)
        margin_threshold = 0.5 * (tm10 + nm99)
        reason = "" if safe else "target_and_field_negative_distributions_overlap"
    else:
        np99 = -1.0
        nm99 = -1.0
        positive_separation = 2.0
        margin_separation = 2.0
        positive_threshold = tp10 - fallback_positive_margin
        margin_threshold = tm10 - fallback_margin_margin
        safe = True
        reason = "no_field_negatives_fallback"

    return ThresholdRecommendation(
        min_positive_similarity=float(np.clip(positive_threshold, -1.0, 1.0)),
        min_margin=float(np.clip(margin_threshold, -2.0, 2.0)),
        target_count=len(target_samples),
        negative_count=len(negative_samples),
        target_positive_p10=tp10,
        negative_positive_p99=np99,
        target_margin_p10=tm10,
        negative_margin_p99=nm99,
        positive_separation=positive_separation,
        margin_separation=margin_separation,
        safe_to_apply=safe,
        reason=reason,
    )


class ThresholdProfileStore:
    SCHEMA = "macrobot.perception_threshold/v1"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.root: Dict[str, Any] = {"schema": self.SCHEMA, "profiles": {}}
        self.reload()

    def reload(self) -> None:
        if not self.path.exists():
            self.root = {"schema": self.SCHEMA, "profiles": {}}
            return
        loaded = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, Mapping):
            raise ValueError("threshold profile root must be a mapping")
        schema = str(loaded.get("schema", self.SCHEMA))
        if schema != self.SCHEMA:
            raise ValueError(f"unsupported threshold profile schema: {schema}")
        profiles = loaded.get("profiles", {})
        if not isinstance(profiles, Mapping):
            raise ValueError("profiles must be a mapping")
        self.root = dict(loaded)
        self.root["schema"] = self.SCHEMA
        self.root["profiles"] = dict(profiles)

    @staticmethod
    def _object_key(name: str) -> str:
        key = name.strip()
        if not key:
            raise ValueError("object name is empty")
        return key

    @staticmethod
    def _environment_key(name: str) -> str:
        return name.strip() or "default"

    def get(self, object_name: str, environment_id: str = "default") -> Optional[Dict[str, Any]]:
        objects = self.root.get("profiles", {})
        object_data = objects.get(self._object_key(object_name)) if isinstance(objects, Mapping) else None
        if not isinstance(object_data, Mapping):
            return None
        environments = object_data.get("environments", {})
        if not isinstance(environments, Mapping):
            return None
        env_key = self._environment_key(environment_id)
        value = environments.get(env_key) or environments.get("default")
        return dict(value) if isinstance(value, Mapping) else None

    def upsert(
        self,
        object_name: str,
        environment_id: str,
        recommendation: ThresholdRecommendation,
        *,
        applied: bool,
    ) -> None:
        object_key = self._object_key(object_name)
        env_key = self._environment_key(environment_id)
        profiles = self.root.setdefault("profiles", {})
        object_data = profiles.setdefault(object_key, {})
        environments = object_data.setdefault("environments", {})
        environments[env_key] = {
            "embedding": {
                "min_positive_similarity": recommendation.min_positive_similarity,
                "min_margin": recommendation.min_margin,
                "enforce_thresholds": True,
            },
            "calibration": {
                **recommendation.to_mapping(),
                "applied": bool(applied),
                "calibrated_at": utc_now_iso(),
            },
        }
        self.root["updated_at"] = utc_now_iso()
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(self.root, allow_unicode=True, sort_keys=False)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=str(self.path.parent),
            prefix=self.path.name + ".", suffix=".tmp", delete=False,
        ) as stream:
            stream.write(text)
            temporary = Path(stream.name)
        temporary.replace(self.path)
