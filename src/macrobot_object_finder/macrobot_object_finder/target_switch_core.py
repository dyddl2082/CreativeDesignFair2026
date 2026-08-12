"""Pure helpers for verifying that all perception components use one target.

This module intentionally has no ROS imports so readiness rules can be tested
without a ROS installation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def _norm(value: object) -> str:
    return str(value or "").strip().casefold()


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


@dataclass(frozen=True)
class TargetReadiness:
    target: str
    ready: bool
    checks: dict[str, bool]
    reasons: tuple[str, ...]
    details: dict[str, Any]


def evaluate_target_readiness(
    target: str,
    statuses: Mapping[str, Mapping[str, Any]],
    *,
    require_candidate_target: bool = True,
    require_temporal_target: bool = True,
    require_patch_bank_when_enabled: bool = True,
) -> TargetReadiness:
    """Return whether the compact perception chain is ready for ``target``.

    The embedding bank is authoritative.  Candidate-filter and temporal target
    acknowledgements are also required by default so a stale target cannot
    produce a false confirmation during an asynchronous bank switch.
    """

    expected = _norm(target)
    candidate = dict(statuses.get("filter", {}))
    embedding = dict(statuses.get("embedding", {}))
    temporal = dict(statuses.get("temporal", {}))

    candidate_target = _norm(candidate.get("target_object"))
    embedding_target = _norm(embedding.get("target_object"))
    bank_target = _norm(embedding.get("bank_target", embedding.get("target_object")))
    temporal_target = _norm(temporal.get("target_object"))

    positive_count = _as_int(embedding.get("positive_reference_count"))
    negative_count = _as_int(embedding.get("negative_reference_count"))
    positive_patch_count = _as_int(
        embedding.get("positive_patch_prototype_count")
    )
    patch_enabled = bool(embedding.get("patch_localization_enabled", False))
    negative_required = bool(
        embedding.get("require_negative_bank_for_accept", False)
    )
    bank_ready = bool(
        embedding.get(
            "bank_ready",
            bank_target == expected and positive_count > 0,
        )
    )
    banks_loading = bool(embedding.get("banks_loading", False))

    checks = {
        "target_nonempty": bool(expected),
        "embedding_target_matches": embedding_target == expected,
        "embedding_bank_target_matches": bank_target == expected,
        "embedding_bank_ready": bank_ready and not banks_loading,
        "positive_bank_available": positive_count > 0,
        "negative_bank_available_if_required": (
            not negative_required or negative_count > 0
        ),
        "patch_bank_available_if_required": (
            not require_patch_bank_when_enabled
            or not patch_enabled
            or positive_patch_count > 0
        ),
        "candidate_target_matches": (
            not require_candidate_target or candidate_target == expected
        ),
        "temporal_target_matches": (
            not require_temporal_target or temporal_target == expected
        ),
    }
    reasons = tuple(name for name, passed in checks.items() if not passed)
    return TargetReadiness(
        target=str(target),
        ready=not reasons,
        checks=checks,
        reasons=reasons,
        details={
            "candidate_target": candidate.get("target_object", ""),
            "embedding_target": embedding.get("target_object", ""),
            "bank_target": embedding.get(
                "bank_target", embedding.get("target_object", "")
            ),
            "temporal_target": temporal.get("target_object", ""),
            "positive_reference_count": positive_count,
            "negative_reference_count": negative_count,
            "positive_patch_prototype_count": positive_patch_count,
            "patch_localization_enabled": patch_enabled,
            "require_negative_bank_for_accept": negative_required,
            "bank_ready": bank_ready,
            "banks_loading": banks_loading,
        },
    )
