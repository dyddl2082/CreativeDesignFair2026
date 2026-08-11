from __future__ import annotations

from contextlib import contextmanager
import json
import select
import sys
import termios
import threading
import time
from typing import Any, Dict, Optional, Tuple
import tty
import uuid

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

from .demo_core import JOINT_NAMES, Q


def ask_text(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else default


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{suffix}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "1", "true", "예", "네"}


def ask_float(prompt: str, default: float) -> float:
    while True:
        raw = ask_text(prompt, f"{default:.4f}")
        try:
            return float(raw)
        except ValueError:
            print("숫자를 입력하세요.")


def print_result(result: Optional[Dict[str, Any]]) -> bool:
    if result is None:
        print("응답이 없습니다.")
        return False
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(result.get("ok"))


class DemoClientNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_arm_demo_cli")
        self.declare_parameter("command_topic", "/macrobot/arm/demo/command")
        self.declare_parameter("result_topic", "/macrobot/arm/demo/result")
        self.declare_parameter("status_topic", "/macrobot/arm/demo/status")
        self.declare_parameter(
            "logical_state_topic", "/macrobot/arm/logical_joint_states"
        )
        self.command_pub = self.create_publisher(
            String, str(self.get_parameter("command_topic").value), 10
        )
        self.create_subscription(
            String,
            str(self.get_parameter("result_topic").value),
            self._result_callback,
            20,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("status_topic").value),
            self._status_callback,
            20,
        )
        self.create_subscription(
            JointState,
            str(self.get_parameter("logical_state_topic").value),
            self._state_callback,
            50,
        )
        self._condition = threading.Condition()
        self._results: Dict[str, Dict[str, Any]] = {}
        self.last_status: Dict[str, Any] = {}
        self.current_q: Q = (0.0, 0.0, 0.0)
        self.have_state = False

    def _result_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        command_id = str(payload.get("command_id", ""))
        if not command_id:
            return
        with self._condition:
            self._results[command_id] = payload
            self._condition.notify_all()

    def _status_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if isinstance(payload, dict):
            self.last_status = payload

    def _state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        if all(name in values for name in JOINT_NAMES):
            self.current_q = tuple(float(values[name]) for name in JOINT_NAMES)  # type: ignore[assignment]
            self.have_state = True

    def command(
        self,
        action: str,
        *,
        wait_timeout_sec: float = 35.0,
        wait: bool = True,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        command_id = f"demo-cli-{uuid.uuid4().hex[:12]}"
        payload = {"action": action, "command_id": command_id, **kwargs}
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        self.command_pub.publish(message)
        if not wait:
            return {"ok": True, "event": "command_sent", "command_id": command_id}
        deadline = time.monotonic() + wait_timeout_sec
        with self._condition:
            while command_id not in self._results:
                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    return {
                        "ok": False,
                        "event": "cli_timeout",
                        "command_id": command_id,
                        "action": action,
                    }
                self._condition.wait(timeout=min(0.25, remaining))
            return self._results.pop(command_id)


@contextmanager
def raw_terminal():
    if not sys.stdin.isatty():
        raise RuntimeError("keyboard jog requires an interactive terminal")
    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)


def _read_key(timeout: float = 0.1) -> str:
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if not ready:
        return ""
    return sys.stdin.read(1)


class ArmDemoWizard:
    def __init__(self, node: DemoClientNode) -> None:
        self.node = node

    def run(self) -> None:
        while True:
            print("\n=== MacRobot Arm Demonstration Recorder ===")
            print("1. 상태 / 저장된 primitive 목록")
            print("2. 현재 자세를 pose primitive로 기록")
            print("3. 외부 조종을 하면서 trajectory 기록")
            print("4. 키보드 jog와 trajectory 기록을 함께 실행")
            print("5. 저장된 primitive 안전 재생")
            print("6. 키보드 jog만 실행")
            print("7. primitive 삭제")
            print("9. 종료")
            choice = input("선택: ").strip()
            try:
                if choice == "1":
                    print_result(self.node.command("status", wait_timeout_sec=5.0))
                elif choice == "2":
                    self.record_pose()
                elif choice == "3":
                    self.record_external()
                elif choice == "4":
                    self.record_with_jog()
                elif choice == "5":
                    self.play()
                elif choice == "6":
                    self.jog(recording=False)
                elif choice == "7":
                    self.delete()
                elif choice == "9":
                    return
                else:
                    print("지원하지 않는 메뉴입니다.")
            except KeyboardInterrupt:
                print("\n정지 요청을 보냅니다.")
                print_result(self.node.command("stop", wait_timeout_sec=5.0))
            except Exception as exc:
                print(f"오류: {exc}")

    def record_pose(self) -> None:
        name = ask_text("primitive 이름", "HOME")
        result = self.node.command(
            "record_pose",
            name=name,
            speed_scale=ask_float("기본 speed scale", 0.5),
            notes=ask_text("메모", ""),
            wait_timeout_sec=8.0,
        )
        print_result(result)

    def record_external(self) -> None:
        name = ask_text("trajectory primitive 이름", "ARM_DEMO")
        result = self.node.command(
            "start_recording",
            name=name,
            speed_scale=ask_float("기본 speed scale", 0.5),
            notes=ask_text("메모", ""),
            wait_timeout_sec=8.0,
        )
        if not print_result(result):
            return
        print(
            "다른 안전한 조종 도구를 사용해 팔을 움직이세요. "
            "조종은 반드시 /macrobot/arm/joint_goal 경로를 사용해야 합니다."
        )
        input("기록을 끝내려면 Enter: ")
        print_result(
            self.node.command("stop_recording", save=True, wait_timeout_sec=12.0)
        )

    def record_with_jog(self) -> None:
        name = ask_text("trajectory primitive 이름", "ARM_DEMO")
        result = self.node.command(
            "start_recording",
            name=name,
            speed_scale=ask_float("기본 speed scale", 0.5),
            notes=ask_text("메모", ""),
            wait_timeout_sec=8.0,
        )
        if not print_result(result):
            return
        try:
            self.jog(recording=True)
        except Exception:
            self.node.command("discard_recording", wait_timeout_sec=5.0)
            raise
        save = ask_yes_no("이 trajectory를 저장할까요?", True)
        action = "stop_recording" if save else "discard_recording"
        kwargs = {"save": True} if save else {}
        print_result(self.node.command(action, wait_timeout_sec=12.0, **kwargs))

    def play(self) -> None:
        status = self.node.command("list", wait_timeout_sec=5.0)
        print_result(status)
        name = ask_text("재생할 primitive 이름", "")
        if not name:
            return
        print(
            "재생은 raw pulse가 아니라 validator와 safe-region을 거친 waypoint 이동입니다."
        )
        if not ask_yes_no("실제로 재생할까요?", False):
            return
        print_result(
            self.node.command(
                "play",
                name=name,
                speed_scale=ask_float("재생 속도 배율", 1.0),
                wait_timeout_sec=300.0,
            )
        )

    def delete(self) -> None:
        name = ask_text("삭제할 primitive 이름", "")
        if not name:
            return
        if ask_yes_no(f"{name}을 삭제할까요?", False):
            print_result(self.node.command("delete", name=name, wait_timeout_sec=8.0))

    def jog(self, *, recording: bool) -> None:
        if not self.node.have_state:
            print("논리 관절 상태를 기다립니다...")
            deadline = time.monotonic() + 5.0
            while not self.node.have_state and time.monotonic() < deadline:
                time.sleep(0.1)
        if not self.node.have_state:
            raise RuntimeError("/macrobot/arm/logical_joint_states가 없습니다")

        step = 0.05
        print(
            "\n키보드 jog (각 목표는 validator를 통과합니다)\n"
            "  w/s : q1 + / -\n"
            "  e/d : q2 + / -\n"
            "  r/f : q3 + / -\n"
            "  h   : home [0,0,0]\n"
            "  [/] : step 감소 / 증가\n"
            "  m   : recording mark 추가\n"
            "  space: 현재 trajectory 정지\n"
            "  x   : jog 종료\n"
        )
        with raw_terminal():
            while True:
                key = _read_key()
                if not key:
                    continue
                if key == "x":
                    print("\njog 종료")
                    return
                if key == " ":
                    self.node.command("stop", wait_timeout_sec=5.0)
                    print("\nSTOP")
                    continue
                if key == "[":
                    step = max(0.005, step / 2.0)
                    print(f"\nstep={step:.4f} rad")
                    continue
                if key == "]":
                    step = min(0.20, step * 2.0)
                    print(f"\nstep={step:.4f} rad")
                    continue
                if key == "m" and recording:
                    # Temporarily restore normal input for a mark label is cumbersome;
                    # use an automatically numbered mark in raw mode.
                    result = self.node.command(
                        "mark", label=f"MARK_{int(time.time())}", wait_timeout_sec=5.0
                    )
                    print(f"\nmark: {bool(result and result.get('ok'))}")
                    continue

                q = list(self.node.current_q)
                if key == "w":
                    q[0] += step
                elif key == "s":
                    q[0] -= step
                elif key == "e":
                    q[1] += step
                elif key == "d":
                    q[1] -= step
                elif key == "r":
                    q[2] += step
                elif key == "f":
                    q[2] -= step
                elif key == "h":
                    q = [0.0, 0.0, 0.0]
                else:
                    continue

                result = self.node.command(
                    "move_to_q",
                    q=q,
                    label="arm_demo_keyboard_jog",
                    wait_timeout_sec=45.0,
                )
                if not result or not result.get("ok"):
                    print("\n목표 거부/실패:")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    values = self.node.current_q
                    print(
                        f"\rq=[{values[0]:+.3f}, {values[1]:+.3f}, {values[2]:+.3f}] "
                        f"step={step:.3f}",
                        end="",
                        flush=True,
                    )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DemoClientNode()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    try:
        ArmDemoWizard(node).run()
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
