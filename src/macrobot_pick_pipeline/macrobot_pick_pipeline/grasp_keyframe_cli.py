"""CLI for semantic grasp keyframe capture, preflight, and playback.

This wrapper intentionally keeps all ROS/hardware interaction inside the
macrobot_grasp_keyframes node.  The CLI only sends a JSON command and waits for
one result.  For close-range operation where DINO/localized detections are not
stable, --stored-profile resolves the object reference point from the stored
object runtime profile and sends it as object_point_base.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
import uuid

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import yaml


_DEFAULT_STORED_PROFILE_FILE = "~/MacRobot/data/stored_objects/runtime_profiles.yaml"
_STAGES = ["OPEN", "PRE_GRASP", "GRASP_OPEN", "CLOSE", "LIFT"]


def _stored_reference_point(profile_name: str, path_text: str) -> list[float]:
    """Return alignment.reference_point_base from a stored-object profile."""

    path = Path(path_text).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"stored object profile file not found: {path}")

    root = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    profiles = root.get("profiles", {}) if isinstance(root, dict) else {}
    if not isinstance(profiles, dict):
        raise ValueError("stored profile file does not contain a profiles mapping")

    if profile_name in profiles:
        profile = profiles[profile_name]
    else:
        matches = [
            value
            for key, value in profiles.items()
            if str(key).casefold() == profile_name.casefold()
        ]
        if len(matches) != 1:
            raise ValueError(f"stored object profile not found: {profile_name}")
        profile = matches[0]

    if not isinstance(profile, dict):
        raise ValueError("stored profile is not a mapping")

    alignment = profile.get("alignment", {})
    point = alignment.get("reference_point_base") if isinstance(alignment, dict) else None
    if not isinstance(point, dict):
        raise ValueError(
            "stored profile has no alignment.reference_point_base; "
            "run record-grasp before using --stored-profile"
        )

    values = [float(point[name]) for name in ("x", "y", "z")]
    return values


def _add_object_reference_arguments(parser: argparse.ArgumentParser) -> None:
    reference = parser.add_mutually_exclusive_group()
    reference.add_argument(
        "--stored-profile",
        default="",
        help=(
            "Use alignment.reference_point_base from a two-stage stored-object "
            "profile.  This is the normal option after record-grasp when close-range "
            "DINO/localized detection is unreliable."
        ),
    )
    reference.add_argument(
        "--object-point-base",
        nargs=3,
        type=float,
        metavar=("X", "Y", "Z"),
        help="Explicit base_link object point to use instead of live detection.",
    )
    parser.add_argument(
        "--stored-profile-file",
        default=_DEFAULT_STORED_PROFILE_FILE,
        help="Stored-object runtime profile YAML path.",
    )


def _attach_object_reference(payload: dict, args: argparse.Namespace) -> None:
    """Add object_point_base to a command payload when requested."""

    explicit = getattr(args, "object_point_base", None)
    stored = getattr(args, "stored_profile", "")
    stored_file = getattr(args, "stored_profile_file", _DEFAULT_STORED_PROFILE_FILE)

    if explicit is not None:
        payload["object_point_base"] = [float(v) for v in explicit]
        payload["object_reference_source"] = "explicit_object_point_base"
    elif stored:
        payload["object_point_base"] = _stored_reference_point(stored, stored_file)
        payload["object_reference_source"] = "stored_grasp_reference"
        payload["stored_profile"] = stored
        payload["stored_profile_file"] = str(Path(stored_file).expanduser())


class Client(Node):
    def __init__(self, timeout: float) -> None:
        super().__init__("grasp_keyframe_cli")
        self.pub = self.create_publisher(String, "/macrobot/grasp_keyframes/command", 10)
        self.result = None
        self.create_subscription(
            String, "/macrobot/grasp_keyframes/result", self._callback, 10
        )
        self.timeout = timeout

    def _callback(self, message: String) -> None:
        try:
            self.result = json.loads(message.data)
        except Exception:
            self.result = {"ok": False, "event": "invalid_result", "raw": message.data}

    def call(self, payload: dict) -> dict:
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        # Wait for the command subscriber, then publish exactly once. Repeating
        # the same command can race with a long-running semantic trajectory.
        discovery_deadline = time.monotonic() + min(5.0, self.timeout)
        while (
            rclpy.ok()
            and self.pub.get_subscription_count() == 0
            and time.monotonic() < discovery_deadline
        ):
            rclpy.spin_once(self, timeout_sec=0.1)
        if self.pub.get_subscription_count() == 0:
            return {
                "ok": False,
                "event": "command_subscriber_not_discovered",
                "command_id": str(payload.get("command_id", "")),
            }
        self.pub.publish(message)
        deadline = time.monotonic() + self.timeout
        while rclpy.ok() and self.result is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
        return self.result or {"ok": False, "event": "cli_timeout"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Semantic grasp keyframe CLI")
    parser.add_argument("--timeout", type=float, default=120.0)

    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture")
    capture.add_argument("profile")
    capture.add_argument("object_name")
    capture.add_argument("stage", choices=_STAGES)
    _add_object_reference_arguments(capture)

    finalize = sub.add_parser("finalize")
    finalize.add_argument("profile")

    preflight = sub.add_parser("preflight")
    preflight.add_argument("profile")
    preflight.add_argument("--object-name", default="")
    _add_object_reference_arguments(preflight)

    play = sub.add_parser("play")
    play.add_argument("profile")
    play.add_argument("--object-name", default="")
    _add_object_reference_arguments(play)

    preflight_place = sub.add_parser("preflight-place")
    preflight_place.add_argument("profile")
    preflight_place.add_argument("--object-name", default="")
    _add_object_reference_arguments(preflight_place)

    place = sub.add_parser("place")
    place.add_argument("profile")
    place.add_argument("--object-name", default="")
    _add_object_reference_arguments(place)

    delete = sub.add_parser("delete")
    delete.add_argument("profile")

    sub.add_parser("list")
    sub.add_parser("reload")
    sub.add_parser("cancel")
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    payload = {"command_id": f"keyframe-cli-{uuid.uuid4().hex[:10]}"}

    if args.command == "capture":
        payload.update(
            {
                "action": "capture",
                "profile": args.profile,
                "object_name": args.object_name,
                "stage": args.stage,
            }
        )
        _attach_object_reference(payload, args)
    elif args.command in {"play", "preflight", "place", "preflight-place"}:
        action = "preflight_place" if args.command == "preflight-place" else args.command
        payload.update(
            {
                "action": action,
                "profile": args.profile,
                "object_name": args.object_name,
            }
        )
        _attach_object_reference(payload, args)
    elif args.command in {"finalize", "delete"}:
        payload.update({"action": args.command, "profile": args.profile})
    else:
        payload["action"] = args.command

    rclpy.init()
    node = Client(args.timeout)
    try:
        result = node.call(payload)
    finally:
        node.destroy_node()
        rclpy.shutdown()

    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if bool(result.get("ok", False)) else 1)


if __name__ == "__main__":
    main()
