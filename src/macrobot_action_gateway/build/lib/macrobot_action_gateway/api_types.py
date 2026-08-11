from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any, Mapping


class TaskStatus(str, Enum):
    SUCCEEDED = "succeeded"
    PARTIALLY_SUCCEEDED = "partially_succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True)
class TaskOutcome:
    status: TaskStatus
    message: str
    data: dict[str, object] | None = None


class ActionState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    CANCEL_REQUESTED = "cancel_requested"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMED_OUT = "timed_out"

    @property
    def terminal(self) -> bool:
        return self in {
            ActionState.SUCCEEDED,
            ActionState.FAILED,
            ActionState.CANCELED,
            ActionState.TIMED_OUT,
        }


@dataclass(frozen=True)
class ActionHandle:
    action_id: str
    action_name: str
    run_id: str


@dataclass(frozen=True)
class ActionResult:
    action_id: str
    action_name: str
    run_id: str
    state: ActionState
    error_code: str | None
    error_message: str | None
    started_at_unix_ms: int | None
    finished_at_unix_ms: int | None
    duration_ms: int | None


@dataclass(frozen=True)
class OperationResult:
    function_name: str
    run_id: str
    success: bool
    error_code: str | None
    error_message: str | None
    finished_at_unix_ms: int


class ResourceId(str, Enum):
    BASE_MOTION = "base_motion"
    ARM_MOTION = "arm_motion"
    GRIPPER_MOTION = "gripper_motion"
    PICO_MOTION = "pico_motion"
    POSITION_STORE = "position_store"
    ARM_PRIMITIVE_STORE = "arm_primitive_store"


class ObjectId(str, Enum):
    """Initial canonical object catalog used by the v0.2 examples.

    Extend this enum together with ``config/object_catalog.yaml`` whenever a new
    object becomes part of the public LLM contract.  Runtime-only free-form
    object names intentionally are not accepted by the generated-code API.
    """

    BUDS3 = "Buds3"
    CUP = "Cup"


class ObjectState(str, Enum):
    VISIBLE = "visible"
    NOT_VISIBLE = "not_visible"
    AMBIGUOUS = "ambiguous"
    STALE = "stale"
    PERCEPTION_UNAVAILABLE = "perception_unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ObjectStateResult:
    run_id: str
    object_id: ObjectId
    state: ObjectState
    confidence: float | None
    observed_at_unix_ms: int | None
    checked_at_unix_ms: int
    error_code: str | None
    error_message: str | None


class EstimateState(str, Enum):
    VALID = "valid"
    TRANSIENT = "transient"
    UNRELIABLE = "unreliable"
    UNAVAILABLE = "unavailable"


class StateSource(str, Enum):
    COMMAND_HISTORY = "command_history"
    COMMANDED_STATE = "commanded_state"
    MEASURED_STATE = "measured_state"


class RobotSnapshotState(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class RobotPosResult:
    run_id: str
    snapshot_state: RobotSnapshotState
    captured_at_unix_ms: int

    x_m: float | None
    y_m: float | None
    yaw_deg: float | None
    base_state: EstimateState
    base_source: StateSource
    base_updated_at_unix_ms: int | None

    arm_lift_deg: float | None
    wrist_pitch_deg: float | None
    arm_state: EstimateState
    arm_source: StateSource
    arm_updated_at_unix_ms: int | None

    gripper_deg: float | None
    gripper_state: EstimateState
    gripper_source: StateSource
    gripper_updated_at_unix_ms: int | None

    error_code: str | None
    error_message: str | None


SERIALIZABLE_TYPES = {
    cls.__name__: cls
    for cls in (
        TaskOutcome,
        ActionHandle,
        ActionResult,
        OperationResult,
        ObjectStateResult,
        RobotPosResult,
    )
}

ENUM_TYPES = {
    cls.__name__: cls
    for cls in (
        TaskStatus,
        ActionState,
        ResourceId,
        ObjectId,
        ObjectState,
        EstimateState,
        StateSource,
        RobotSnapshotState,
    )
}


def to_wire(value: Any) -> Any:
    if isinstance(value, Enum):
        return {"__enum__": type(value).__name__, "value": value.value}
    if is_dataclass(value):
        payload = {key: to_wire(item) for key, item in asdict(value).items()}
        payload["__type__"] = type(value).__name__
        return payload
    if isinstance(value, Mapping):
        return {str(key): to_wire(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [to_wire(item) for item in value]
    if isinstance(value, list):
        return [to_wire(item) for item in value]
    return value


def from_wire(value: Any) -> Any:
    if isinstance(value, list):
        return [from_wire(item) for item in value]
    if not isinstance(value, dict):
        return value
    if "__enum__" in value:
        enum_cls = ENUM_TYPES.get(str(value["__enum__"]))
        if enum_cls is None:
            raise ValueError(f"Unknown enum type: {value['__enum__']}")
        return enum_cls(value["value"])
    type_name = value.get("__type__")
    if type_name:
        cls = SERIALIZABLE_TYPES.get(str(type_name))
        if cls is None:
            raise ValueError(f"Unknown serialized type: {type_name}")
        kwargs = {
            key: from_wire(item)
            for key, item in value.items()
            if key != "__type__"
        }
        return cls(**kwargs)
    return {str(key): from_wire(item) for key, item in value.items()}
