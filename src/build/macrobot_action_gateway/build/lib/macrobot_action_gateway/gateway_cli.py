from __future__ import annotations

import argparse
import json
import secrets
import sys
import time

from .api_types import ObjectId, ResourceId, to_wire
from .gateway_protocol import GatewayRpcClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MacRobot Action Gateway administration CLI")
    parser.add_argument("--socket", default="/tmp/macrobot_action_gateway.sock")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    stop = sub.add_parser("stop")
    stop.add_argument("--run-id", default="")
    abort = sub.add_parser("abort-run")
    abort.add_argument("run_id")
    call = sub.add_parser("call")
    call.add_argument("function")
    call.add_argument("--run-id", default="")
    call.add_argument("--args-json", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    client = GatewayRpcClient(args.socket, timeout_s=190.0)
    try:
        if args.command == "status":
            result = client.status()
        elif args.command == "abort-run":
            result = client.abort_run(args.run_id, "gateway_cli")
        elif args.command == "stop":
            run_id = args.run_id or f"admin-{int(time.time() * 1000)}-{secrets.token_hex(2)}"
            client.open_run(run_id)
            result = client.call(run_id, "STOP", {}, timeout_s=10.0)
        elif args.command == "call":
            run_id = args.run_id or f"cli-{int(time.time() * 1000)}-{secrets.token_hex(2)}"
            client.open_run(run_id)
            payload = json.loads(args.args_json)
            if not isinstance(payload, dict):
                raise ValueError("--args-json must decode to an object")
            result = client.call(run_id, args.function, payload)
        else:
            raise AssertionError(args.command)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(to_wire(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
