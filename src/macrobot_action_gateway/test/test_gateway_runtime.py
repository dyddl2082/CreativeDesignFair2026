import time

from macrobot_action_gateway.api_types import (
    ActionState,
    ObjectId,
)
from macrobot_action_gateway.bridge import DryRunBridge
from macrobot_action_gateway.gateway_runtime import GatewayRuntime


SETTINGS = {
    "real_motion_enabled": False,
    "run_limits": {"max_wall_time_s": 60.0, "max_internal_motion_steps_per_run": 20},
    "control_limits": {
        "max_wait_seconds_per_call": 2.0,
        "max_wait_action_timeout_s": 10.0,
        "max_wait_resource_timeout_s": 2.0,
    },
    "control_timeouts": {"cancel_all_s": 1.0, "stop_s": 1.0},
    "base_limits": {"max_move_distance_m_per_call": 1.0, "max_turn_angle_deg_per_call": 180.0},
    "base_timeouts": {"move_base_s": 1.0, "turn_base_s": 1.0, "move_base_to_pos_s": 5.0},
    "base_motion": {"move_speed": 80, "turn_speed": 70, "move_tolerance_m": 0.001, "turn_tolerance_deg": 0.1},
    "alignment": {"max_motion_steps_per_call": 5, "hard_timeout_s": 2.0},
    "arm_limits": {"arm_lift_deg": [-57.3, 57.3], "wrist_pitch_deg": [-74.5, 74.5]},
    "arm_timeouts": {"set_arm_joints_s": 1.0},
    "gripper_limits": {"logical_deg": [0.0, 90.0]},
    "gripper_timeouts": {"set_gripper_s": 1.0},
    "manipulation": {
        "pick_max_motion_steps_per_call": 8,
        "place_max_motion_steps_per_call": 8,
        "pick_hard_timeout_s": 2.0,
        "place_hard_timeout_s": 2.0,
        "default_placement_offset_base": [0.0, 0.12, 0.0],
    },
    "perception": {"object_state_max_age_ms": 1500, "health_max_age_ms": 5000},
}
CATALOG = {
    "BUDS3": {
        "runtime_name": "Buds3",
        "alignment_profile": "Buds3",
        "pick_profile": "Buds3",
        "placement_profile": "Buds3",
    },
    "CUP": {
        "runtime_name": "Cup",
        "alignment_profile": "Cup",
        "pick_profile": "Cup",
        "placement_profile": "Cup",
        "placement_offset_base": [0.0, 0.15, 0.0],
    },
}


def runtime():
    bridge = DryRunBridge()
    result = GatewayRuntime(bridge, SETTINGS, CATALOG)
    result.open_run("r")
    result.state.update_logical_joint_state(0.0, 0.0, 10.0)
    # Production receives this state from the resilient task heartbeat.
    result.state.set_held_object(None, known=True)
    return result, bridge


def wait(runtime, handle):
    return runtime.call("r", "WAIT_ACTION", {"action": handle, "timeout_s": 5.0})


def test_move_turn_and_position_restore():
    gateway, _ = runtime()
    assert wait(gateway, gateway.call("r", "MOVE_BASE", {"distance_m": 0.2})).state == ActionState.SUCCEEDED
    assert wait(gateway, gateway.call("r", "TURN_BASE", {"angle_deg": 90.0})).state == ActionState.SUCCEEDED
    saved = gateway.call("r", "SAVE_POS", {"position_id": "pose_1", "overwrite": False})
    assert saved.success
    assert wait(gateway, gateway.call("r", "MOVE_BASE", {"distance_m": 0.1})).state == ActionState.SUCCEEDED
    result = wait(gateway, gateway.call("r", "MOVE_BASE_TO_POS", {"position_id": "pose_1"}))
    assert result.state == ActionState.SUCCEEDED


def test_arm_primitive_excludes_gripper_and_preserves_it():
    gateway, bridge = runtime()
    saved = gateway.call("r", "SAVE_ARM_PRIMITIVE", {"primitive_id": "pre_grasp", "overwrite": False})
    assert saved.success
    close = gateway.call("r", "SET_GRIPPER", {"gripper_deg": 40.0})
    assert wait(gateway, close).state == ActionState.SUCCEEDED
    primitive = gateway.call("r", "SET_ARM_PRIMITIVE", {"primitive_id": "pre_grasp"})
    assert wait(gateway, primitive).state == ActionState.SUCCEEDED
    assert bridge.calls[-1][0] == "ARM"
    q_rad = bridge.calls[-1][1]
    assert round(q_rad[2], 6) == round(40.0 * 3.141592653589793 / 180.0, 6)


def test_pick_and_place_reverse_sequence_bridge():
    gateway, bridge = runtime()
    pick = gateway.call("r", "PICK_OBJECT", {"object_id": ObjectId.BUDS3})
    assert wait(gateway, pick).state == ActionState.SUCCEEDED
    place = gateway.call("r", "PLACE_NEXTTO_OBJECT", {"reference_object_id": ObjectId.CUP})
    result = wait(gateway, place)
    assert result.state == ActionState.SUCCEEDED
    assert bridge.calls[-1][0] == "PLACE"
    assert bridge.calls[-1][1]["reference_object"] == "Cup"
    assert bridge.calls[-1][1]["held_object"] == "Buds3"
    assert bridge.calls[-1][1]["placement_offset_base"] == (0.0, 0.15, 0.0)
    held, known = gateway.state.held_object()
    assert known is True
    assert held is None


def test_place_rejects_empty_gripper():
    gateway, _ = runtime()
    place = gateway.call("r", "PLACE_NEXTTO_OBJECT", {"reference_object_id": ObjectId.CUP})
    result = wait(gateway, place)
    assert result.state == ActionState.FAILED
    assert result.error_code == "NO_HELD_OBJECT"



def test_pick_rejects_unknown_held_state_until_synchronized():
    bridge = DryRunBridge()
    gateway = GatewayRuntime(bridge, SETTINGS, CATALOG)
    gateway.open_run("unknown-held")
    pick = gateway.call(
        "unknown-held", "PICK_OBJECT", {"object_id": ObjectId.BUDS3}
    )
    result = gateway.call(
        "unknown-held", "WAIT_ACTION", {"action": pick, "timeout_s": 5.0}
    )
    assert result.state == ActionState.FAILED
    assert result.error_code == "HELD_OBJECT_STATE_UNKNOWN"

def test_stop_blocks_new_motion_in_same_run():
    gateway, _ = runtime()
    stopped = gateway.call("r", "STOP", {})
    assert stopped.success
    handle = gateway.call("r", "MOVE_BASE", {"distance_m": 0.1})
    result = wait(gateway, handle)
    assert result.state == ActionState.FAILED
    assert result.error_code == "RUN_STOPPED"


def test_close_run_cancels_active_action():
    class BlockingBridge(DryRunBridge):
        def execute_base_move(self, distance_m, *, speed, timeout_s, cancel_event):
            from macrobot_action_gateway.bridge import BridgeOutcome
            del distance_m, speed, timeout_s
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                if cancel_event.is_set():
                    return BridgeOutcome(
                        False,
                        "RUN_CANCELED",
                        "cancelled",
                        canceled=True,
                        started=True,
                    )
                time.sleep(0.01)
            return BridgeOutcome(True, started=True)

    bridge = BlockingBridge()
    gateway = GatewayRuntime(bridge, SETTINGS, CATALOG)
    gateway.open_run("close-test")
    handle = gateway.call("close-test", "MOVE_BASE", {"distance_m": 0.2})
    time.sleep(0.05)
    closed = gateway.close_run("close-test")
    assert closed["had_active_actions"] is True
    assert closed["cancel_success"] is True
    result = gateway.actions.check(handle, "close-test")
    assert result.state == ActionState.CANCELED
