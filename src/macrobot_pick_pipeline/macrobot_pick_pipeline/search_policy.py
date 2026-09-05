"""Translation-dominant active visual-search policy.

The pattern intentionally avoids using a large calibrated turn as a geometric
measurement.  Turns are only small camera-view changes; every useful decision is
made again from vision after the chassis stops.  Short forward probes are gated
by the depth-clearance monitor and are reversed along the same corridor.
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


@dataclass(frozen=True)
class TranslationDominantSearchConfig:
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
    """Return a monotonic view sweep made only of one-step yaw changes.

    Alternating directly between +N and -N creates increasingly large turns
    (for example +30 -> -30).  The tracked chassis is floor-sensitive, so the
    camera instead sweeps gradually from center to one side, back through
    center, and then to the other side.  The final pose need not reproduce an
    exact yaw because every useful decision is visual.
    """

    count = max(0, int(levels))
    step = float(step_deg)
    if count == 0 or step <= 0.0:
        return (0.0,)
    positive = [step * level for level in range(1, count + 1)]
    return_to_center = [step * level for level in range(count - 1, -1, -1)]
    negative = [-step * level for level in range(1, count + 1)]
    return tuple([0.0, *positive, *return_to_center, *negative])


def build_translation_dominant_search(
    config: TranslationDominantSearchConfig,
) -> Tuple[SearchAction, ...]:
    config.validate()
    actions = [
        SearchAction(
            "observe",
            label="initial_view",
            observe_sec=config.observation_sec,
        )
    ]

    traveled = 0.0
    for index in range(config.forward_steps):
        if config.forward_step_m <= 0.0:
            break
        actions.append(
            SearchAction(
                "move",
                amount=config.forward_step_m,
                label=f"corridor_forward_{index + 1}",
            )
        )
        traveled += config.forward_step_m
        actions.append(
            SearchAction(
                "observe",
                label=f"corridor_view_{index + 1}",
                observe_sec=config.observation_sec,
            )
        )

    if config.include_reverse_return and traveled > 0.0:
        # Return in the same short increments so perception can still re-plan at
        # every boundary and the rear motion stays on an already observed path.
        for index in range(config.forward_steps):
            actions.append(
                SearchAction(
                    "move",
                    amount=-config.forward_step_m,
                    label=f"corridor_reverse_{index + 1}",
                )
            )
            actions.append(
                SearchAction(
                    "observe",
                    label=f"reverse_view_{index + 1}",
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


def total_motion_budget(actions: Iterable[SearchAction]) -> tuple[float, float]:
    move = 0.0
    turn = 0.0
    for action in actions:
        if action.kind == "move":
            move += abs(action.amount)
        elif action.kind == "turn":
            turn += abs(action.amount)
    return move, turn
