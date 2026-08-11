from __future__ import annotations

import math
import threading
import time
from typing import Any, Mapping

from .action_manager import ActionManager, ActionRecord, RunRecord
from .api_types import (
    ActionHandle,
    ActionResult,
    ActionState,
    ObjectId,
    OperationResult,
    ResourceId,
)
from .bridge import BridgeOutcome, HardwareBridge
from .resource_manager import ResourceManager
from .state_store import RobotStateStore, normalize_yaw_deg, unix_ms


ASYNC_FUNCTIONS = {
    "MOVE_BASE",
    "TURN_BASE",
    "MOVE_BASE_TO_POS",
    "ALIGN_WITH_OBJECT",
    "SET_ARM_JOINTS",
    "SET_GRIPPER",
    "SET_ARM_PRIMITIVE",
    "PICK_OBJECT",
    "PLACE_NEXTTO_OBJECT",
}

SYNC_FUNCTIONS = {
    "WAIT_SECOND",
    "WAIT_ACTION",
    "WAIT_RESOURCE",
    "CHECK_ACTION",
    "CANCEL_ACTION",
    "CANCEL_ALL",
    "STOP",
    "GET_OBJECT_STATE",
    "GET_ROBOT_POS",
    "SAVE_POS",
    "SAVE_ARM_PRIMITIVE",
}

PUBLIC_FUNCTIONS = ASYNC_FUNCTIONS | SYNC_FUNCTIONS


class GatewayRuntime:
    """Spec v0.2 API implementation independent of the ROS transport layer."""

    def __init__(
        self,
        bridge: HardwareBridge,
        settings: Mapping[str, Any],
        object_catalog: Mapping[str, Mapping[str, Any]],
    ) -> None:
        self.bridge = bridge
        self.settings = dict(settings)
        self.object_catalog = {str(key): dict(value) for key, value in object_catalog.items()}
        self.resources = ResourceManager()
        self.actions = ActionManager(self.resources)
        self.state = RobotStateStore()

    # ------------------------------------------------------------------
    # Run lifecycle / RPC support
    # ------------------------------------------------------------------
    def open_run(self, run_id: str) -> dict[str, Any]:
        run = self.actions.open_run(
            run_id,
            max_wall_time_s=float(self._get("run_limits.max_wall_time_s", 300.0)),
            max_internal_motion_steps=int(
                self._get("run_limits.max_internal_motion_steps_per_run", 40)
            ),
        )
        return {
            "run_id": run.run_id,
            "max_wall_time_s": run.max_wall_time_s,
            "max_internal_motion_steps": run.max_internal_motion_steps,
        }

    def close_run(self, run_id: str) -> dict[str, Any]:
        """Close a code run without leaving orphaned robot actions behind.

        A generated program is required to wait for every dependent asynchronous
        action.  Nevertheless, the Gateway treats an early ``main()`` return as a
        safety event: active actions are cancelled before the run is closed.  If
        bounded cancellation cannot be confirmed, a system-wide controlled STOP
        is requested.
        """
        active_before = self.actions.active_records(run_id)
        had_active_actions = bool(active_before)
        cancel_success = True
        stop_success: bool | None = None
        stop_error_code: str | None = None
        if had_active_actions:
            cancel_success = self.actions.cancel_all(
                run_id, float(self._get("control_timeouts.cancel_all_s", 5.0))
            )
            if not cancel_success:
                stop = self._stop(run_id, mark_run_stopped=True)
                stop_success = stop.success
                stop_error_code = stop.error_code
        self.actions.close_run(run_id)
        return {
            "run_id": run_id,
            "closed": True,
            "had_active_actions": had_active_actions,
            "active_action_count": len(active_before),
            "cancel_success": cancel_success,
            "stop_success": stop_success,
            "stop_error_code": stop_error_code,
            "clean_shutdown": (not had_active_actions) or cancel_success or bool(stop_success),
        }

    def abort_run(self, run_id: str, reason: str = "worker_aborted") -> dict[str, Any]:
        self.actions.mark_run_canceled(run_id)
        self.actions.cancel_all(
            run_id, float(self._get("control_timeouts.cancel_all_s", 5.0))
        )
        stop = self._stop(run_id, mark_run_stopped=True)
        return {
            "run_id": run_id,
            "reason": reason,
            "stop_success": stop.success,
            "stop_error_code": stop.error_code,
        }

    def status(self) -> dict[str, Any]:
        return {
            "actions": self.actions.snapshot(),
            "resources": self.resources.snapshot(),
            "robot_state": self.state.debug_snapshot(),
            "bridge": self.bridge.system_health(),
            "real_motion_enabled": bool(self._get("real_motion_enabled", False)),
            "spec_version": "0.2.0",
        }

    # ------------------------------------------------------------------
    # Public dispatch
    # ------------------------------------------------------------------
    def call(self, run_id: str, function_name: str, args: Mapping[str, Any]) -> Any:
        name = str(function_name).strip().upper()
        if name not in PUBLIC_FUNCTIONS:
            return OperationResult(
                function_name=name or "UNKNOWN",
                run_id=run_id,
                success=False,
                error_code="INVALID_ARGUMENT",
                error_message=f"지원하지 않는 Robot API 함수입니다: {name}",
                finished_at_unix_ms=unix_ms(),
            )
        run = self.actions.get_run(run_id)
        if run is None:
            self.open_run(run_id)
            run = self.actions.get_run(run_id)
        assert run is not None

        if name == "WAIT_SECOND":
            return self._wait_second(run, args)
        if name == "WAIT_ACTION":
            return self._wait_action(run, args)
        if name == "WAIT_RESOURCE":
            return self._wait_resource(run, args)
        if name == "CHECK_ACTION":
            return self._check_action(run, args)
        if name == "CANCEL_ACTION":
            return self._cancel_action(run, args)
        if name == "CANCEL_ALL":
            return self._cancel_all(run)
        if name == "STOP":
            return self._stop(run_id, mark_run_stopped=True)
        if name == "GET_OBJECT_STATE":
            return self._get_object_state(run, args)
        if name == "GET_ROBOT_POS":
            return self.state.robot_snapshot(run_id)
        if name == "SAVE_POS":
            return self._save_pos(run, args)
        if name == "SAVE_ARM_PRIMITIVE":
            return self._save_arm_primitive(run, args)
        if name == "MOVE_BASE":
            return self._move_base(run, args)
        if name == "TURN_BASE":
            return self._turn_base(run, args)
        if name == "MOVE_BASE_TO_POS":
            return self._move_base_to_pos(run, args)
        if name == "ALIGN_WITH_OBJECT":
            return self._align_with_object(run, args)
        if name == "SET_ARM_JOINTS":
            return self._set_arm_joints(run, args)
        if name == "SET_GRIPPER":
            return self._set_gripper(run, args)
        if name == "SET_ARM_PRIMITIVE":
            return self._set_arm_primitive(run, args)
        if name == "PICK_OBJECT":
            return self._pick_object(run, args)
        if name == "PLACE_NEXTTO_OBJECT":
            return self._place_nextto_object(run, args)
        raise AssertionError(name)

    # ------------------------------------------------------------------
    # Synchronous control functions
    # ------------------------------------------------------------------
    def _wait_second(self, run: RunRecord, args: Mapping[str, Any]) -> OperationResult:
        seconds = self._finite_float(args.get("seconds"))
        maximum = float(self._get("control_limits.max_wait_seconds_per_call", 60.0))
        if seconds is None or not (0.0 < seconds <= maximum):
            return self._op_fail("WAIT_SECOND", run.run_id, "INVALID_ARGUMENT", "seconds 범위가 올바르지 않습니다.")
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            interruption = self._run_interruption(run)
            if interruption is not None:
                return self._op_fail("WAIT_SECOND", run.run_id, *interruption)
            time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
        return self._op_ok("WAIT_SECOND", run.run_id)

    def _wait_action(self, run: RunRecord, args: Mapping[str, Any]) -> ActionResult:
        handle = self._handle(args.get("action"))
        timeout_s = self._finite_float(args.get("timeout_s"))
        maximum = float(self._get("control_limits.max_wait_action_timeout_s", 180.0))
        if handle is None or timeout_s is None or not (0.0 < timeout_s <= maximum):
            return self._synthetic_action_failure(
                handle,
                run.run_id,
                "WAIT_ACTION",
                "INVALID_ARGUMENT",
                "ActionHandle 또는 timeout_s가 올바르지 않습니다.",
            )
        return self.actions.wait(handle, run.run_id, timeout_s, cancel_on_timeout=True)

    def _wait_resource(self, run: RunRecord, args: Mapping[str, Any]) -> OperationResult:
        try:
            resource = args.get("resource_id")
            resource_id = resource if isinstance(resource, ResourceId) else ResourceId(str(resource))
        except Exception:
            return self._op_fail("WAIT_RESOURCE", run.run_id, "INVALID_ARGUMENT", "유효한 ResourceId가 필요합니다.")
        waitable = {
            ResourceId.BASE_MOTION,
            ResourceId.ARM_MOTION,
            ResourceId.GRIPPER_MOTION,
            ResourceId.PICO_MOTION,
        }
        if resource_id not in waitable:
            return self._op_fail("WAIT_RESOURCE", run.run_id, "RESOURCE_NOT_WAITABLE", "이 자원은 공개 대기를 허용하지 않습니다.")
        timeout_s = self._finite_float(args.get("timeout_s"))
        maximum = float(self._get("control_limits.max_wait_resource_timeout_s", 120.0))
        if timeout_s is None or not (0.0 < timeout_s <= maximum):
            return self._op_fail("WAIT_RESOURCE", run.run_id, "INVALID_ARGUMENT", "timeout_s 범위가 올바르지 않습니다.")
        ok = self.resources.wait_idle(
            resource_id,
            timeout_s,
            interrupted=lambda: run.interrupted(),
        )
        if ok:
            return self._op_ok("WAIT_RESOURCE", run.run_id)
        interruption = self._run_interruption(run)
        if interruption is not None:
            return self._op_fail("WAIT_RESOURCE", run.run_id, *interruption)
        return self._op_fail("WAIT_RESOURCE", run.run_id, "WAIT_TIMEOUT", "제한시간 안에 자원이 idle 상태가 되지 않았습니다.")

    def _check_action(self, run: RunRecord, args: Mapping[str, Any]) -> ActionResult:
        handle = self._handle(args.get("action"))
        if handle is None:
            return self._synthetic_action_failure(None, run.run_id, "CHECK_ACTION", "INVALID_ARGUMENT", "ActionHandle이 필요합니다.")
        return self.actions.check(handle, run.run_id)

    def _cancel_action(self, run: RunRecord, args: Mapping[str, Any]) -> ActionResult:
        handle = self._handle(args.get("action"))
        if handle is None:
            return self._synthetic_action_failure(None, run.run_id, "CANCEL_ACTION", "INVALID_ARGUMENT", "ActionHandle이 필요합니다.")
        return self.actions.request_cancel(handle, run.run_id)

    def _cancel_all(self, run: RunRecord) -> OperationResult:
        ok = self.actions.cancel_all(
            run.run_id, float(self._get("control_timeouts.cancel_all_s", 5.0))
        )
        if ok:
            return self._op_ok("CANCEL_ALL", run.run_id)
        return self._op_fail("CANCEL_ALL", run.run_id, "PARTIAL_CANCEL_FAILURE", "일부 액션의 안전한 종료를 확인하지 못했습니다.")

    def _stop(self, run_id: str, *, mark_run_stopped: bool) -> OperationResult:
        if mark_run_stopped:
            self.actions.mark_run_stopped(run_id)
        # STOP is system-wide.  Signal every active action, regardless of run.
        for record in self.actions.active_records():
            with record.lock:
                if not record.state.terminal:
                    record.state = ActionState.CANCEL_REQUESTED
                    record.cancel_event.set()
        self.bridge.cancel_align_pick()
        timeout_s = float(self._get("control_timeouts.stop_s", 5.0))
        base_result = self.bridge.stop_base(timeout_s)
        arm_result = self.bridge.stop_arm(timeout_s)
        if base_result.success and arm_result.success:
            return self._op_ok("STOP", run_id)
        errors = [
            item.error_message
            for item in (base_result, arm_result)
            if not item.success and item.error_message
        ]
        return self._op_fail(
            "STOP",
            run_id,
            "SAFE_STOP_UNCONFIRMED",
            "; ".join(errors) or "모든 motion domain의 안전한 정지를 확인하지 못했습니다.",
        )

    def _get_object_state(self, run: RunRecord, args: Mapping[str, Any]):
        object_id = self._object_id(args.get("object_id"))
        if object_id is None or object_id.name not in self.object_catalog:
            requested = ObjectId.BUDS3 if object_id is None else object_id
            from .api_types import ObjectState, ObjectStateResult
            return ObjectStateResult(
                run_id=run.run_id,
                object_id=requested,
                state=ObjectState.UNKNOWN,
                confidence=None,
                observed_at_unix_ms=None,
                checked_at_unix_ms=unix_ms(),
                error_code="OBJECT_NOT_REGISTERED",
                error_message="등록되지 않은 ObjectId입니다.",
            )
        return self.state.object_state(
            run.run_id,
            object_id,
            max_age_ms=int(self._get("perception.object_state_max_age_ms", 1500)),
            perception_health_max_age_ms=int(
                self._get("perception.health_max_age_ms", 5000)
            ),
        )

    def _save_pos(self, run: RunRecord, args: Mapping[str, Any]) -> OperationResult:
        owner = f"sync-save-pos-{run.run_id}-{time.monotonic_ns()}"
        if not self.resources.is_idle(ResourceId.BASE_MOTION):
            return self._op_fail("SAVE_POS", run.run_id, "RESOURCE_BUSY", "차체가 움직이는 동안 위치를 저장할 수 없습니다.")
        if not self.resources.acquire(owner, [ResourceId.POSITION_STORE]):
            return self._op_fail("SAVE_POS", run.run_id, "RESOURCE_BUSY", "위치 저장소가 사용 중입니다.")
        try:
            position_id = str(args.get("position_id", ""))
            overwrite = args.get("overwrite", False)
            if type(overwrite) is not bool:
                return self._op_fail("SAVE_POS", run.run_id, "INVALID_ARGUMENT", "overwrite는 bool이어야 합니다.")
            error = self.state.save_position(position_id, overwrite)
            if error is None:
                return self._op_ok("SAVE_POS", run.run_id)
            messages = {
                "POSITION_ID_INVALID": "position_id 형식이 올바르지 않습니다.",
                "POSITION_ALREADY_EXISTS": "같은 position_id가 이미 존재합니다.",
                "POSE_ESTIMATE_UNRELIABLE": "현재 차체 추정 자세를 신뢰할 수 없습니다.",
            }
            return self._op_fail("SAVE_POS", run.run_id, error, messages.get(error, error))
        finally:
            self.resources.release(owner)

    def _save_arm_primitive(self, run: RunRecord, args: Mapping[str, Any]) -> OperationResult:
        owner = f"sync-save-arm-{run.run_id}-{time.monotonic_ns()}"
        if not self.resources.is_idle(ResourceId.ARM_MOTION):
            return self._op_fail("SAVE_ARM_PRIMITIVE", run.run_id, "RESOURCE_BUSY", "팔이 움직이는 동안 primitive를 저장할 수 없습니다.")
        if not self.resources.acquire(owner, [ResourceId.ARM_PRIMITIVE_STORE]):
            return self._op_fail("SAVE_ARM_PRIMITIVE", run.run_id, "RESOURCE_BUSY", "primitive 저장소가 사용 중입니다.")
        try:
            primitive_id = str(args.get("primitive_id", ""))
            overwrite = args.get("overwrite", False)
            if type(overwrite) is not bool:
                return self._op_fail("SAVE_ARM_PRIMITIVE", run.run_id, "INVALID_ARGUMENT", "overwrite는 bool이어야 합니다.")
            error = self.state.save_arm_primitive(primitive_id, overwrite)
            if error is None:
                return self._op_ok("SAVE_ARM_PRIMITIVE", run.run_id)
            messages = {
                "PRIMITIVE_ID_INVALID": "primitive_id 형식이 올바르지 않습니다.",
                "PRIMITIVE_ALREADY_EXISTS": "같은 primitive_id가 이미 존재합니다.",
                "ARM_STATE_UNAVAILABLE": "저장할 팔 상태가 없습니다.",
                "ARM_STATE_TRANSIENT": "팔이 움직이는 중입니다.",
                "ARM_STATE_UNRELIABLE": "팔 commanded state를 신뢰할 수 없습니다.",
            }
            return self._op_fail("SAVE_ARM_PRIMITIVE", run.run_id, error, messages.get(error, error))
        finally:
            self.resources.release(owner)

    # ------------------------------------------------------------------
    # Asynchronous motion functions
    # ------------------------------------------------------------------
    def _move_base(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        distance = self._finite_float(args.get("distance_m"))

        def execute(record: ActionRecord, current_run: RunRecord):
            maximum = float(self._get("base_limits.max_move_distance_m_per_call", 1.0))
            if distance is None or distance == 0.0 or abs(distance) > maximum:
                return ActionState.FAILED, "INVALID_ARGUMENT", "distance_m 범위가 올바르지 않습니다."
            if not self._motion_start_allowed(current_run, 1):
                return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "run motion step 제한을 초과합니다."
            self.state.mark_base_transient()
            outcome = self.bridge.execute_base_move(
                distance,
                speed=int(self._get("base_motion.move_speed", 80)),
                timeout_s=float(self._get("base_timeouts.move_base_s", 15.0)),
                cancel_event=record.cancel_event,
            )
            return self._finish_base_outcome(outcome, move_m=distance)

        return self.actions.create(
            run.run_id,
            "MOVE_BASE",
            [ResourceId.BASE_MOTION, ResourceId.PICO_MOTION],
            execute,
        )

    def _turn_base(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        angle = self._finite_float(args.get("angle_deg"))

        def execute(record: ActionRecord, current_run: RunRecord):
            maximum = float(self._get("base_limits.max_turn_angle_deg_per_call", 180.0))
            if angle is None or angle == 0.0 or abs(angle) > maximum:
                return ActionState.FAILED, "INVALID_ARGUMENT", "angle_deg 범위가 올바르지 않습니다."
            if not self._motion_start_allowed(current_run, 1):
                return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "run motion step 제한을 초과합니다."
            self.state.mark_base_transient()
            outcome = self.bridge.execute_base_turn(
                angle,
                speed=int(self._get("base_motion.turn_speed", 150)),
                timeout_s=float(self._get("base_timeouts.turn_base_s", 15.0)),
                cancel_event=record.cancel_event,
            )
            return self._finish_base_outcome(outcome, turn_deg=angle)

        return self.actions.create(
            run.run_id,
            "TURN_BASE",
            [ResourceId.BASE_MOTION, ResourceId.PICO_MOTION],
            execute,
        )

    def _move_base_to_pos(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        position_id = str(args.get("position_id", ""))

        def execute(record: ActionRecord, current_run: RunRecord):
            if not self.state.validate_id(position_id):
                return ActionState.FAILED, "POSITION_ID_INVALID", "position_id 형식이 올바르지 않습니다."
            target = self.state.get_position(position_id)
            if target is None:
                return ActionState.FAILED, "POSITION_NOT_FOUND", "저장된 위치를 찾을 수 없습니다."
            current = self.state.base_snapshot()
            if current.values is None or current.state.value != "valid":
                return ActionState.FAILED, "POSE_ESTIMATE_UNRELIABLE", "현재 차체 추정 자세를 신뢰할 수 없습니다."
            if current_run.remaining_motion_steps() < 3:
                return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "위치 복귀에 필요한 최대 3 motion step budget이 없습니다."
            start = time.monotonic()
            hard_timeout = float(self._get("base_timeouts.move_base_to_pos_s", 45.0))
            x, y, yaw = current.values
            tx, ty, tyaw = target
            dx, dy = tx - x, ty - y
            target_heading = math.degrees(math.atan2(dy, dx)) if math.hypot(dx, dy) > 1e-9 else yaw
            turn_tolerance = float(self._get("base_motion.turn_tolerance_deg", 1.0))
            move_tolerance = float(self._get("base_motion.move_tolerance_m", 0.01))

            def timed_out() -> bool:
                return time.monotonic() - start > hard_timeout

            first_turn = normalize_yaw_deg(target_heading - yaw)
            if abs(first_turn) > turn_tolerance:
                if not current_run.consume_motion_steps(1):
                    return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "run motion step 제한을 초과했습니다."
                outcome = self.bridge.execute_base_turn(
                    first_turn,
                    speed=int(self._get("base_motion.turn_speed", 150)),
                    timeout_s=min(float(self._get("base_timeouts.turn_base_s", 15.0)), max(0.1, hard_timeout - (time.monotonic() - start))),
                    cancel_event=record.cancel_event,
                )
                result = self._finish_base_outcome(outcome, turn_deg=first_turn)
                if result[0] != ActionState.SUCCEEDED:
                    return result
                yaw = normalize_yaw_deg(yaw + first_turn)
            distance = math.hypot(dx, dy)
            if abs(distance) > move_tolerance:
                if timed_out():
                    self.state.mark_base_unreliable()
                    return ActionState.TIMED_OUT, "ACTION_HARD_TIMEOUT", "MOVE_BASE_TO_POS hard timeout"
                if not current_run.consume_motion_steps(1):
                    return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "run motion step 제한을 초과했습니다."
                outcome = self.bridge.execute_base_move(
                    distance,
                    speed=int(self._get("base_motion.move_speed", 80)),
                    timeout_s=min(float(self._get("base_timeouts.move_base_s", 15.0)), max(0.1, hard_timeout - (time.monotonic() - start))),
                    cancel_event=record.cancel_event,
                )
                result = self._finish_base_outcome(outcome, move_m=distance)
                if result[0] != ActionState.SUCCEEDED:
                    return result
            final_turn = normalize_yaw_deg(tyaw - yaw)
            if abs(final_turn) > turn_tolerance:
                if timed_out():
                    self.state.mark_base_unreliable()
                    return ActionState.TIMED_OUT, "ACTION_HARD_TIMEOUT", "MOVE_BASE_TO_POS hard timeout"
                if not current_run.consume_motion_steps(1):
                    return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "run motion step 제한을 초과했습니다."
                outcome = self.bridge.execute_base_turn(
                    final_turn,
                    speed=int(self._get("base_motion.turn_speed", 150)),
                    timeout_s=min(float(self._get("base_timeouts.turn_base_s", 15.0)), max(0.1, hard_timeout - (time.monotonic() - start))),
                    cancel_event=record.cancel_event,
                )
                result = self._finish_base_outcome(outcome, turn_deg=final_turn)
                if result[0] != ActionState.SUCCEEDED:
                    return result
            return ActionState.SUCCEEDED, None, None

        return self.actions.create(
            run.run_id,
            "MOVE_BASE_TO_POS",
            [ResourceId.BASE_MOTION, ResourceId.PICO_MOTION],
            execute,
        )

    def _align_with_object(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        object_id = self._object_id(args.get("object_id"))
        return self._start_align_pick(run, object_id, execute_pick=False)

    def _set_arm_joints(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        arm_lift = self._finite_float(args.get("arm_lift_deg"))
        wrist = self._finite_float(args.get("wrist_pitch_deg"))

        def execute(record: ActionRecord, current_run: RunRecord):
            if arm_lift is None or wrist is None:
                return ActionState.FAILED, "INVALID_ARGUMENT", "팔 각도는 finite float여야 합니다."
            if not self._within(arm_lift, self._get("arm_limits.arm_lift_deg", [-57.3, 57.3])) or not self._within(wrist, self._get("arm_limits.wrist_pitch_deg", [-74.5, 74.5])):
                return ActionState.FAILED, "ARM_LIMIT_VIOLATION", "팔 논리 각도 범위를 벗어났습니다."
            current = self.state.arm_values()
            if current is None:
                return ActionState.FAILED, "ROBOT_STATE_UNAVAILABLE", "보존할 그리퍼 commanded state가 없습니다."
            if not self._motion_start_allowed(current_run, 1):
                return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "run motion step 제한을 초과합니다."
            target = (arm_lift, wrist, current[2])
            return self._execute_arm_target(record, target, "SET_ARM_JOINTS")

        return self.actions.create(
            run.run_id,
            "SET_ARM_JOINTS",
            [ResourceId.ARM_MOTION, ResourceId.PICO_MOTION],
            execute,
        )

    def _set_gripper(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        gripper = self._finite_float(args.get("gripper_deg"))

        def execute(record: ActionRecord, current_run: RunRecord):
            if gripper is None:
                return ActionState.FAILED, "INVALID_ARGUMENT", "gripper_deg는 finite float여야 합니다."
            if not self._within(gripper, self._get("gripper_limits.logical_deg", [0.0, 90.0])):
                return ActionState.FAILED, "GRIPPER_LIMIT_VIOLATION", "그리퍼 논리 각도 범위를 벗어났습니다."
            current = self.state.arm_values()
            if current is None:
                return ActionState.FAILED, "ROBOT_STATE_UNAVAILABLE", "보존할 팔 commanded state가 없습니다."
            if not self._motion_start_allowed(current_run, 1):
                return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "run motion step 제한을 초과합니다."
            target = (current[0], current[1], gripper)
            return self._execute_arm_target(record, target, "SET_GRIPPER")

        return self.actions.create(
            run.run_id,
            "SET_GRIPPER",
            [ResourceId.GRIPPER_MOTION, ResourceId.PICO_MOTION],
            execute,
        )

    def _set_arm_primitive(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        primitive_id = str(args.get("primitive_id", ""))

        def execute(record: ActionRecord, current_run: RunRecord):
            if not self.state.validate_id(primitive_id):
                return ActionState.FAILED, "PRIMITIVE_ID_INVALID", "primitive_id 형식이 올바르지 않습니다."
            primitive = self.state.get_arm_primitive(primitive_id)
            if primitive is None:
                return ActionState.FAILED, "PRIMITIVE_NOT_FOUND", "저장된 팔 primitive를 찾을 수 없습니다."
            current = self.state.arm_values()
            if current is None:
                return ActionState.FAILED, "ROBOT_STATE_UNAVAILABLE", "보존할 그리퍼 commanded state가 없습니다."
            if not self._motion_start_allowed(current_run, 1):
                return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "run motion step 제한을 초과합니다."
            return self._execute_arm_target(record, (primitive[0], primitive[1], current[2]), "SET_ARM_PRIMITIVE")

        return self.actions.create(
            run.run_id,
            "SET_ARM_PRIMITIVE",
            [ResourceId.ARM_MOTION, ResourceId.PICO_MOTION],
            execute,
        )

    def _pick_object(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        object_id = self._object_id(args.get("object_id"))
        return self._start_align_pick(run, object_id, execute_pick=True)

    def _place_nextto_object(self, run: RunRecord, args: Mapping[str, Any]) -> ActionHandle:
        reference = self._object_id(args.get("reference_object_id"))
        if reference is None:
            return self.actions.immediate_failure(
                run.run_id,
                "PLACE_NEXTTO_OBJECT",
                "INVALID_ARGUMENT",
                "유효한 reference_object_id가 필요합니다.",
            )
        held, known = self.state.held_object()
        if known and held is None:
            return self.actions.immediate_failure(
                run.run_id,
                "PLACE_NEXTTO_OBJECT",
                "NO_HELD_OBJECT",
                "현재 보유 중인 물체가 없습니다.",
            )
        # The uploaded v0.2 spec explicitly leaves placement profile schema and
        # verification policy TBD.  Safe-fail until that runtime exists.
        return self.actions.immediate_failure(
            run.run_id,
            "PLACE_NEXTTO_OBJECT",
            "PLACEMENT_PROFILE_NOT_FOUND",
            "현재 프로젝트에는 placement profile/runtime이 아직 구현되지 않았습니다.",
        )

    # ------------------------------------------------------------------
    # Shared asynchronous helpers
    # ------------------------------------------------------------------
    def _start_align_pick(
        self,
        run: RunRecord,
        object_id: ObjectId | None,
        *,
        execute_pick: bool,
    ) -> ActionHandle:
        action_name = "PICK_OBJECT" if execute_pick else "ALIGN_WITH_OBJECT"
        if object_id is None or object_id.name not in self.object_catalog:
            return self.actions.immediate_failure(
                run.run_id,
                action_name,
                "OBJECT_NOT_REGISTERED",
                "등록되지 않은 ObjectId입니다.",
            )
        if execute_pick:
            held, known = self.state.held_object()
            if known and held is not None:
                return self.actions.immediate_failure(
                    run.run_id,
                    action_name,
                    "ALREADY_HOLDING_OBJECT",
                    "다른 물체를 이미 보유 중입니다.",
                )
        config = self.object_catalog[object_id.name]
        max_steps = int(
            self._get(
                "manipulation.pick_max_motion_steps_per_call"
                if execute_pick
                else "alignment.max_motion_steps_per_call",
                12 if execute_pick else 20,
            )
        )

        def execute(record: ActionRecord, current_run: RunRecord):
            if current_run.remaining_motion_steps() < max_steps:
                return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "고수준 액션의 최대 내부 motion budget이 부족합니다."
            outcome = self.bridge.execute_align_pick(
                object_id,
                alignment_profile=str(config.get("alignment_profile", object_id.value)),
                pick_profile=str(config.get("pick_profile", object_id.value)),
                execute_pick=execute_pick,
                timeout_s=float(
                    self._get(
                        "manipulation.pick_hard_timeout_s"
                        if execute_pick
                        else "alignment.hard_timeout_s",
                        120.0 if execute_pick else 60.0,
                    )
                ),
                cancel_event=record.cancel_event,
            )
            actual_steps = int(outcome.details.get("internal_motion_steps", 0))
            if actual_steps > 0 and not current_run.consume_motion_steps(actual_steps):
                self.state.mark_base_unreliable()
                return ActionState.FAILED, "RUN_LIMIT_EXCEEDED", "고수준 액션 실행 중 run motion budget을 초과했습니다."
            if outcome.success:
                if execute_pick:
                    self.state.set_held_object(object_id, known=True)
                return ActionState.SUCCEEDED, None, None
            if outcome.started:
                self.state.mark_base_unreliable()
                if execute_pick:
                    self.state.set_held_object(None, known=False)
            return self._action_state_from_outcome(outcome)

        resources = [ResourceId.BASE_MOTION, ResourceId.PICO_MOTION]
        if execute_pick:
            resources.extend([ResourceId.ARM_MOTION, ResourceId.GRIPPER_MOTION])
        return self.actions.create(run.run_id, action_name, resources, execute)

    def _execute_arm_target(
        self,
        record: ActionRecord,
        target_deg: tuple[float, float, float],
        action_name: str,
    ) -> tuple[ActionState, str | None, str | None]:
        self.state.mark_arm_transient()
        q_rad = tuple(math.radians(value) for value in target_deg)
        timeout_key = (
            "gripper_timeouts.set_gripper_s"
            if action_name == "SET_GRIPPER"
            else "arm_timeouts.set_arm_joints_s"
        )
        outcome = self.bridge.execute_arm_goal(
            q_rad,
            timeout_s=float(self._get(timeout_key, 20.0)),
            cancel_event=record.cancel_event,
        )
        if outcome.success:
            self.state.update_logical_joint_state(*target_deg)
            return ActionState.SUCCEEDED, None, None
        if outcome.started:
            self.state.mark_arm_unreliable()
        return self._action_state_from_outcome(outcome)

    def _finish_base_outcome(
        self,
        outcome: BridgeOutcome,
        *,
        move_m: float | None = None,
        turn_deg: float | None = None,
    ) -> tuple[ActionState, str | None, str | None]:
        if outcome.success:
            if move_m is not None:
                self.state.apply_move(move_m)
            if turn_deg is not None:
                self.state.apply_turn(turn_deg)
            return ActionState.SUCCEEDED, None, None
        if outcome.started:
            self.state.mark_base_unreliable()
        return self._action_state_from_outcome(outcome)

    @staticmethod
    def _action_state_from_outcome(
        outcome: BridgeOutcome,
    ) -> tuple[ActionState, str | None, str | None]:
        if outcome.canceled:
            return ActionState.CANCELED, outcome.error_code or "RUN_CANCELED", outcome.error_message
        if outcome.timed_out:
            return ActionState.TIMED_OUT, outcome.error_code or "ACTION_HARD_TIMEOUT", outcome.error_message
        return ActionState.FAILED, outcome.error_code or "MOTION_EXECUTION_FAILED", outcome.error_message

    # ------------------------------------------------------------------
    # Validation / conversion helpers
    # ------------------------------------------------------------------
    def _motion_start_allowed(self, run: RunRecord, steps: int) -> bool:
        interruption = self._run_interruption(run)
        if interruption is not None:
            return False
        return run.consume_motion_steps(steps)

    @staticmethod
    def _finite_float(value: Any) -> float | None:
        if isinstance(value, bool):
            return None
        try:
            converted = float(value)
        except (TypeError, ValueError):
            return None
        return converted if math.isfinite(converted) else None

    @staticmethod
    def _within(value: float, limits: Any) -> bool:
        try:
            minimum, maximum = float(limits[0]), float(limits[1])
        except Exception:
            return False
        return minimum <= value <= maximum

    @staticmethod
    def _handle(value: Any) -> ActionHandle | None:
        if isinstance(value, ActionHandle):
            return value
        if isinstance(value, Mapping):
            try:
                return ActionHandle(
                    action_id=str(value["action_id"]),
                    action_name=str(value["action_name"]),
                    run_id=str(value["run_id"]),
                )
            except Exception:
                return None
        return None

    @staticmethod
    def _object_id(value: Any) -> ObjectId | None:
        if isinstance(value, ObjectId):
            return value
        text = str(value or "").strip()
        for item in ObjectId:
            if text in {item.name, item.value} or text.casefold() in {
                item.name.casefold(), item.value.casefold()
            }:
                return item
        return None

    def _run_interruption(self, run: RunRecord) -> tuple[str, str] | None:
        with run.lock:
            if run.stopped:
                return "RUN_STOPPED", "현재 run은 STOP 상태입니다."
            if run.canceled or run.closed:
                return "RUN_CANCELED", "현재 run이 취소 또는 종료되었습니다."
            if run.wall_timed_out():
                return "RUN_WALL_TIMEOUT", "전체 run wall-clock 제한을 초과했습니다."
        return None

    def _get(self, dotted: str, default: Any) -> Any:
        current: Any = self.settings
        for part in dotted.split("."):
            if not isinstance(current, Mapping) or part not in current:
                return default
            current = current[part]
        return current

    @staticmethod
    def _op_ok(function_name: str, run_id: str) -> OperationResult:
        return OperationResult(function_name, run_id, True, None, None, unix_ms())

    @staticmethod
    def _op_fail(
        function_name: str,
        run_id: str,
        error_code: str,
        error_message: str,
    ) -> OperationResult:
        return OperationResult(
            function_name,
            run_id,
            False,
            error_code,
            error_message,
            unix_ms(),
        )

    @staticmethod
    def _synthetic_action_failure(
        handle: ActionHandle | None,
        run_id: str,
        action_name: str,
        error_code: str,
        error_message: str,
    ) -> ActionResult:
        now = unix_ms()
        return ActionResult(
            action_id="" if handle is None else handle.action_id,
            action_name=action_name if handle is None else handle.action_name,
            run_id=run_id if handle is None else handle.run_id,
            state=ActionState.FAILED,
            error_code=error_code,
            error_message=error_message,
            started_at_unix_ms=None,
            finished_at_unix_ms=now,
            duration_ms=None,
        )
