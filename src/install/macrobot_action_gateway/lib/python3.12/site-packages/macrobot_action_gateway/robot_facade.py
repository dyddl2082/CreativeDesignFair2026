from __future__ import annotations

from .api_types import (
    ActionHandle,
    ActionResult,
    ObjectId,
    ObjectStateResult,
    OperationResult,
    ResourceId,
    RobotPosResult,
)
from .gateway_protocol import GatewayRpcClient


class RobotFacade:
    """The only object injected into generated Python code."""

    def __init__(self, client: GatewayRpcClient, run_id: str) -> None:
        self._client = client
        self._run_id = run_id

    def WAIT_SECOND(self, seconds: float) -> OperationResult:
        return self._client.call(self._run_id, "WAIT_SECOND", {"seconds": seconds})

    def WAIT_ACTION(self, action: ActionHandle, timeout_s: float) -> ActionResult:
        return self._client.call(
            self._run_id,
            "WAIT_ACTION",
            {"action": action, "timeout_s": timeout_s},
            timeout_s=max(5.0, float(timeout_s) + 8.0),
        )

    def WAIT_RESOURCE(self, resource_id: ResourceId, timeout_s: float) -> OperationResult:
        return self._client.call(
            self._run_id,
            "WAIT_RESOURCE",
            {"resource_id": resource_id, "timeout_s": timeout_s},
            timeout_s=max(5.0, float(timeout_s) + 2.0),
        )

    def CHECK_ACTION(self, action: ActionHandle) -> ActionResult:
        return self._client.call(self._run_id, "CHECK_ACTION", {"action": action})

    def CANCEL_ACTION(self, action: ActionHandle) -> ActionResult:
        return self._client.call(
            self._run_id,
            "CANCEL_ACTION",
            {"action": action},
            timeout_s=10.0,
        )

    def CANCEL_ALL(self) -> OperationResult:
        return self._client.call(self._run_id, "CANCEL_ALL", {}, timeout_s=10.0)

    def STOP(self) -> OperationResult:
        return self._client.call(self._run_id, "STOP", {}, timeout_s=10.0)

    def GET_OBJECT_STATE(self, object_id: ObjectId) -> ObjectStateResult:
        return self._client.call(
            self._run_id,
            "GET_OBJECT_STATE",
            {"object_id": object_id},
        )

    def GET_ROBOT_POS(self) -> RobotPosResult:
        return self._client.call(self._run_id, "GET_ROBOT_POS", {})

    def MOVE_BASE(self, distance_m: float) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "MOVE_BASE",
            {"distance_m": distance_m},
        )

    def TURN_BASE(self, angle_deg: float) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "TURN_BASE",
            {"angle_deg": angle_deg},
        )

    def SAVE_POS(self, position_id: str, overwrite: bool = False) -> OperationResult:
        return self._client.call(
            self._run_id,
            "SAVE_POS",
            {"position_id": position_id, "overwrite": overwrite},
        )

    def MOVE_BASE_TO_POS(self, position_id: str) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "MOVE_BASE_TO_POS",
            {"position_id": position_id},
        )

    def ALIGN_WITH_OBJECT(self, object_id: ObjectId) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "ALIGN_WITH_OBJECT",
            {"object_id": object_id},
        )

    def SET_ARM_JOINTS(
        self,
        arm_lift_deg: float,
        wrist_pitch_deg: float,
    ) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "SET_ARM_JOINTS",
            {
                "arm_lift_deg": arm_lift_deg,
                "wrist_pitch_deg": wrist_pitch_deg,
            },
        )

    def SET_GRIPPER(self, gripper_deg: float) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "SET_GRIPPER",
            {"gripper_deg": gripper_deg},
        )

    def SAVE_ARM_PRIMITIVE(
        self,
        primitive_id: str,
        overwrite: bool = False,
    ) -> OperationResult:
        return self._client.call(
            self._run_id,
            "SAVE_ARM_PRIMITIVE",
            {"primitive_id": primitive_id, "overwrite": overwrite},
        )

    def SET_ARM_PRIMITIVE(self, primitive_id: str) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "SET_ARM_PRIMITIVE",
            {"primitive_id": primitive_id},
        )

    def PICK_OBJECT(self, object_id: ObjectId) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "PICK_OBJECT",
            {"object_id": object_id},
        )

    def PLACE_NEXTTO_OBJECT(self, reference_object_id: ObjectId) -> ActionHandle:
        return self._client.call(
            self._run_id,
            "PLACE_NEXTTO_OBJECT",
            {"reference_object_id": reference_object_id},
        )
