"""MacRobot serial-2R logical joints to physical servo commands."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Dict, Mapping, Tuple

import yaml

JOINT_NAMES = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")


@dataclass(frozen=True)
class ServoAxis:
    name: str
    channel: int
    zero_deg: float
    sign: float
    model_multiplier: float
    command_min_deg: float
    command_max_deg: float
    pulse_min_us: float = 500.0
    pulse_center_us: float = 1500.0
    pulse_max_us: float = 2500.0

    def model_angle_to_command_deg(self, model_angle_rad: float) -> float:
        return self.zero_deg + self.sign * math.degrees(self.model_multiplier * model_angle_rad)

    def within_command_limit(self, command_deg: float, tolerance_deg: float = 1e-6) -> bool:
        return self.command_min_deg - tolerance_deg <= command_deg <= self.command_max_deg + tolerance_deg

    def command_deg_to_pulse_us(self, command_deg: float) -> float:
        command_deg = min(180.0, max(0.0, float(command_deg)))
        if command_deg <= 90.0:
            ratio = command_deg / 90.0
            return self.pulse_min_us + ratio * (self.pulse_center_us - self.pulse_min_us)
        ratio = (command_deg - 90.0) / 90.0
        return self.pulse_center_us + ratio * (self.pulse_max_us - self.pulse_center_us)


@dataclass(frozen=True)
class LogicalLimits:
    q1_min: float
    q1_max: float
    q2_min: float
    q2_max: float
    q3_min: float
    q3_max: float
    home_q1: float = 0.0
    home_q2: float = 0.0
    home_q3: float = 0.0
    model_type: str = "serial_2r"
    model_revision: str = "unknown"

    @property
    def home(self) -> Tuple[float, float, float]:
        return (self.home_q1, self.home_q2, self.home_q3)

    @property
    def tool_pitch_min(self) -> float:
        """Deprecated compatibility alias; q2 is independent in serial 2R."""
        return self.q2_min

    @property
    def tool_pitch_max(self) -> float:
        return self.q2_max

    @property
    def four_bar_margin_rad(self) -> float:
        return 0.0


@dataclass(frozen=True)
class ServoMapping:
    logical_limits: LogicalLimits
    lift: ServoAxis
    tilt: ServoAxis
    gripper: ServoAxis

    def servo_commands_deg(self, q1: float, q2: float, q3: float) -> Dict[str, float]:
        return {
            "lift": self.lift.model_angle_to_command_deg(q1),
            "tilt": self.tilt.model_angle_to_command_deg(q2),
            "gripper": self.gripper.model_angle_to_command_deg(q3),
        }

    def servo_pulses_us(self, q1: float, q2: float, q3: float) -> Dict[str, float]:
        commands = self.servo_commands_deg(q1, q2, q3)
        return {
            "lift": self.lift.command_deg_to_pulse_us(commands["lift"]),
            "tilt": self.tilt.command_deg_to_pulse_us(commands["tilt"]),
            "gripper": self.gripper.command_deg_to_pulse_us(commands["gripper"]),
        }

    def command_limits_ok(self, q1: float, q2: float, q3: float) -> Tuple[bool, str]:
        commands = self.servo_commands_deg(q1, q2, q3)
        for key, axis in (("lift", self.lift), ("tilt", self.tilt), ("gripper", self.gripper)):
            if not axis.within_command_limit(commands[key]):
                return False, f"{key}_servo_limit"
        return True, "safe"


def _extract_ros_parameters(data: Mapping) -> Mapping:
    if "/**" in data:
        block = data["/**"]
        if isinstance(block, Mapping) and "ros__parameters" in block:
            return block["ros__parameters"]
    for block in data.values():
        if isinstance(block, Mapping) and "ros__parameters" in block:
            return block["ros__parameters"]
    if "ros__parameters" in data:
        return data["ros__parameters"]
    return data


def load_servo_mapping(path: str | Path) -> ServoMapping:
    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Actuator configuration not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as stream:
        raw = yaml.safe_load(stream) or {}
    p = _extract_ros_parameters(raw)
    limits = LogicalLimits(
        q1_min=float(p["q1_min"]), q1_max=float(p["q1_max"]),
        q2_min=float(p["q2_min"]), q2_max=float(p["q2_max"]),
        q3_min=float(p["q3_min"]), q3_max=float(p["q3_max"]),
        home_q1=float(p.get("home_q1", 0.0)),
        home_q2=float(p.get("home_q2", 0.0)),
        home_q3=float(p.get("home_q3", 0.0)),
        model_type=str(p.get("model_type", "serial_2r")),
        model_revision=str(p.get("model_revision", "unknown")),
    )

    def axis(prefix: str, default_channel: int, default_name: str) -> ServoAxis:
        return ServoAxis(
            name=default_name,
            channel=int(p.get(f"{prefix}_channel", default_channel)),
            zero_deg=float(p[f"{prefix}_zero_deg"]),
            sign=float(p[f"{prefix}_sign"]),
            model_multiplier=float(p[f"{prefix}_model_multiplier"]),
            command_min_deg=float(p[f"{prefix}_command_min_deg"]),
            command_max_deg=float(p[f"{prefix}_command_max_deg"]),
            pulse_min_us=float(p.get(f"{prefix}_pulse_min_us", 500.0)),
            pulse_center_us=float(p.get(f"{prefix}_pulse_center_us", 1500.0)),
            pulse_max_us=float(p.get(f"{prefix}_pulse_max_us", 2500.0)),
        )

    return ServoMapping(
        limits,
        axis("lift", 0, "left_mg996r_arm_lift"),
        axis("tilt", 1, "right_mg996r_wrist_pitch"),
        axis("gripper", 2, "gripper_mg90s"),
    )
