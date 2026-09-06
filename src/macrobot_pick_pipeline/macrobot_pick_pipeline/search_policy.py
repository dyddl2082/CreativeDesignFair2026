"""Rotation-first active visual-search policy.

The tracked chassis has floor-dependent translational and rotational error.  A
search therefore does not use blind forward motion to discover an object.  It
first observes the current view, optionally performs a *small conditional
backoff* when aligned depth reports that something is too close to the camera,
and then changes only the camera heading in bounded yaw steps.  Translation is
reserved for the visual-alignment phase after the requested object has been
identified and localized.

The backoff actions are deliberately labelled ``close_obstacle_backoff_*``.
They are conditional: :class:`ResilientObjectTaskNode` executes them only while
a fresh central-corridor clearance sample is below the configured threshold.
Because MacRobot has no rear depth sensor, the total reverse distance must stay
small and the operator must keep the rear corridor clear during demonstrations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

from .stored_object_core import absolute_offsets_to_relative_turns


@dataclass(frozen=True)
class SearchAction:
    kind: str  # observe | move | turn
    amount: float = 0.0
    label: str = ""
    observe_sec: float = 0.0

    def validate(self) -> None:
        if self.kind not in {"observe", "move", "turn"}:
            raise ValueError(f"unsupported search action: {self.kind}")
        if self.kind == "observe" and self.amount != 0.0:
            raise ValueError("observe action amount must be zero")
        if self.kind != "observe" and self.observe_sec != 0.0:
            raise ValueError("motion action observe_sec must be zero")


@dataclass(frozen=True)
class RotationFirstSearchConfig:
    """Configuration for bounded rotation-first target acquisition."""

    initial_observation_sec: float = 4.0
    observation_sec: float = 3.0
    backoff_step_m: float = 0.04
    backoff_steps: int = 2
    yaw_step_deg: float = 10.0
    yaw_levels: int = 3
    include_conditional_backoff: bool = True

    def validate(self) -> None:
        if self.initial_observation_sec <= 0.0:
            raise ValueError("initial_observation_sec must be positive")
        if self.observation_sec <= 0.0:
            raise ValueError("observation_sec must be positive")
        if not 0.0 <= self.backoff_step_m <= 0.04:
            raise ValueError("backoff_step_m must be within 0.0 .. 0.04 m")
        if not 0 <= self.backoff_steps <= 2:
            raise ValueError("backoff_steps must be within 0 .. 2")
        if not 0.0 <= self.yaw_step_deg <= 10.0:
            raise ValueError("yaw_step_deg must be within 0.0 .. 10.0 deg")
        if self.yaw_levels < 0:
            raise ValueError("yaw_levels must be non-negative")


@dataclass(frozen=True)
class TranslationDominantSearchConfig:
    """Deprecated compatibility schema.

    Older callers may still construct this class.  Its former forward probe is
    interpreted as a bounded conditional backoff so that no caller silently
    re-enables translation-first search.
    """

    forward_step_m: float = 0.08
    forward_steps: int = 2
    observation_sec: float = 2.0
    yaw_step_deg: float = 12.0
    yaw_levels: int = 3
    include_reverse_return: bool = True

    def validate(self) -> None:
        if self.forward_step_m < 0.0:
            raise ValueError("forward_step_m must be non-negative")
        if self.forward_steps < 0:
            raise ValueError("forward_steps must be non-negative")
        if self.observation_sec <= 0.0:
            raise ValueError("observation_sec must be positive")
        if self.yaw_step_deg < 0.0:
            raise ValueError("yaw_step_deg must be non-negative")
        if self.yaw_levels < 0:
            raise ValueError("yaw_levels must be non-negative")


def _yaw_offsets(step_deg: float, levels: int) -> Tuple[float, ...]:
    """Return a monotonic, small-step camera-view sweep.

    Alternating directly between positive and negative extrema would command
    increasingly large turns.  Instead the camera moves from centre to one
    side, back through centre, and then to the other side.  Every useful
    decision is made from a fresh stationary observation.
    """

    count = max(0, int(levels))
    step = float(step_deg)
    if count == 0 or step <= 0.0:
        return (0.0,)
    positive = [step * level for level in range(1, count + 1)]
    return_to_center = [step * level for level in range(count - 1, -1, -1)]
    negative = [-step * level for level in range(1, count + 1)]
    return tuple([0.0, *positive, *return_to_center, *negative])


def build_rotation_first_search(
    config: RotationFirstSearchConfig,
) -> Tuple[SearchAction, ...]:
    """Build initial observation, conditional backoff, then yaw-only search."""

    config.validate()
    actions = [
        SearchAction(
            "observe",
            label="initial_view",
            observe_sec=config.initial_observation_sec,
        )
    ]

    if config.include_conditional_backoff and config.backoff_step_m > 0.0:
        for index in range(config.backoff_steps):
            actions.append(
                SearchAction(
                    "move",
                    amount=-config.backoff_step_m,
                    label=f"close_obstacle_backoff_{index + 1}",
                )
            )
            actions.append(
                SearchAction(
                    "observe",
                    label=f"post_backoff_view_{index + 1}",
                    observe_sec=config.observation_sec,
                )
            )

    offsets = _yaw_offsets(config.yaw_step_deg, config.yaw_levels)
    relative = absolute_offsets_to_relative_turns(offsets)
    for index, turn in enumerate(relative[1:], start=1):
        actions.append(SearchAction("turn", amount=turn, label=f"view_turn_{index}"))
        actions.append(
            SearchAction(
                "observe",
                label=f"yaw_view_{index}",
                observe_sec=config.observation_sec,
            )
        )

    for action in actions:
        action.validate()
    return tuple(actions)


def build_translation_dominant_search(
    config: TranslationDominantSearchConfig,
) -> Tuple[SearchAction, ...]:
    """Compatibility wrapper that now returns the safer rotation-first plan."""

    config.validate()
    return build_rotation_first_search(
        RotationFirstSearchConfig(
            initial_observation_sec=config.observation_sec,
            observation_sec=config.observation_sec,
            backoff_step_m=min(0.04, config.forward_step_m),
            backoff_steps=min(2, config.forward_steps),
            yaw_step_deg=min(10.0, config.yaw_step_deg),
            yaw_levels=config.yaw_levels,
            include_conditional_backoff=config.include_reverse_return,
        )
    )


def total_motion_budget(actions: Iterable[SearchAction]) -> tuple[float, float]:
    move = 0.0
    turn = 0.0
    for action in actions:
        if action.kind == "move":
            move += abs(action.amount)
        elif action.kind == "turn":
            turn += abs(action.amount)
    return move, turn
