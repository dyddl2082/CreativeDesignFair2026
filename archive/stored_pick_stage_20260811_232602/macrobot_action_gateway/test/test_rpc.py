from pathlib import Path

from macrobot_action_gateway.bridge import DryRunBridge
from macrobot_action_gateway.gateway_protocol import GatewayRpcClient, GatewayServerThread, GatewayUnixServer
from macrobot_action_gateway.gateway_runtime import GatewayRuntime


def test_rpc_status(tmp_path: Path):
    runtime = GatewayRuntime(
        DryRunBridge(),
        {
            "real_motion_enabled": False,
            "run_limits": {"max_wall_time_s": 10.0, "max_internal_motion_steps_per_run": 5},
        },
        {"BUDS3": {"runtime_name": "Buds3"}, "CUP": {"runtime_name": "Cup"}},
    )
    socket_path = tmp_path / "gateway.sock"
    server = GatewayUnixServer(str(socket_path), runtime)
    thread = GatewayServerThread(server)
    thread.start()
    try:
        client = GatewayRpcClient(str(socket_path), timeout_s=2.0)
        opened = client.open_run("run-test")
        assert opened["run_id"] == "run-test"
        status = client.status()
        assert status["spec_version"] == "0.2.0"
    finally:
        thread.close()
