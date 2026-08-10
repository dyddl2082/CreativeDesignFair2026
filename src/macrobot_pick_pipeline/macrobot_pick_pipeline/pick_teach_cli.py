from __future__ import annotations

import json
import threading
import time
from typing import Any, Dict, Optional
import uuid

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String


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
        value = ask_text(prompt, f"{default:.6f}")
        try:
            return float(value)
        except ValueError:
            print("숫자를 입력하세요.")


def ask_q(prompt: str, default=(0.0, 0.0, 0.0)):
    while True:
        raw = ask_text(
            prompt,
            ",".join(f"{value:.6f}" for value in default),
        )
        try:
            values = tuple(float(item.strip()) for item in raw.split(","))
        except ValueError:
            values = ()
        if len(values) == 3:
            return values
        print("q1,q2,q3 형식으로 세 값을 입력하세요.")


class TeachClientNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_pick_teach_cli")
        self.declare_parameter("command_topic", "/macrobot/pick/teach/command")
        self.declare_parameter("result_topic", "/macrobot/pick/teach/result")
        self.declare_parameter("status_topic", "/macrobot/pick/teach/status")
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
        self._condition = threading.Condition()
        self._results: Dict[str, Dict[str, Any]] = {}
        self.last_status: Dict[str, Any] = {}

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

    def command(
        self,
        action: str,
        *,
        wait_timeout_sec: float = 35.0,
        wait: bool = True,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        command_id = f"cli-{uuid.uuid4().hex[:12]}"
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


def print_result(result: Optional[Dict[str, Any]]) -> bool:
    if result is None:
        print("응답이 없습니다.")
        return False
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(result.get("ok"))


class TeachWizard:
    def __init__(self, node: TeachClientNode) -> None:
        self.node = node
        self.current_q = (0.0, 0.0, 0.0)

    def run(self) -> None:
        while True:
            print("\n=== MacRobot Camera-Arm Teach ===")
            print("1. 카메라 target 고정")
            print("5. 카메라 보조 grasp_frame 보정")
            print("6. primitive 기록 / 시험")
            print("7. 물체별 grasp profile 기록 / 시험")
            print("8. 현재 상태")
            print("9. 종료")
            choice = input("선택: ").strip()
            try:
                if choice == "1":
                    self.lock_target()
                elif choice == "5":
                    self.grasp_frame_workflow()
                elif choice == "6":
                    self.primitive_workflow()
                elif choice == "7":
                    self.profile_workflow()
                elif choice == "8":
                    self.show_status()
                elif choice == "9":
                    return
                else:
                    print("지원하지 않는 메뉴입니다.")
            except KeyboardInterrupt:
                print("\n현재 작업을 취소합니다.")
                print_result(self.node.command("cancel", wait_timeout_sec=5.0))
            except Exception as exc:
                print(f"오류: {exc}")

    def lock_target(self, default_name: str = "") -> bool:
        object_name = ask_text("카메라로 고정할 물체 이름", default_name)
        if not object_name:
            print("물체 이름이 필요합니다.")
            return False
        print("여러 프레임에서 3D 위치가 안정될 때까지 기다립니다.")
        result = self.node.command(
            "lock_target",
            object_name=object_name,
            timeout_sec=60.0,
            wait_timeout_sec=65.0,
        )
        return print_result(result)

    def maybe_move(self, label: str) -> bool:
        if not ask_yes_no(f"{label}: validated q 목표를 보내겠습니까?", False):
            print("별도 조종 도구로 안전하게 자세를 맞춘 뒤 Enter를 누르세요.")
            input()
            return True
        q = ask_q("목표 q1,q2,q3", self.current_q)
        result = self.node.command(
            "move_to_q",
            q=list(q),
            label=label,
            wait_timeout_sec=45.0,
        )
        if result and result.get("ok"):
            self.current_q = q
        return print_result(result)

    def grasp_frame_workflow(self) -> None:
        print("\n[메뉴 5] 카메라 보조 grasp_frame 보정")
        print(
            "작은 고정 calibration target의 중심을 실제 두 clamp 접촉 중심과 "
            "일치시켜 기록합니다. 카메라 extrinsic이 먼저 정상이어야 합니다."
        )
        if not self.lock_target("calibration_target"):
            return
        print_result(self.node.command("clear_grasp_samples", wait_timeout_sec=5.0))
        raw = ask_text("측정 q3 목록(rad)", "0.0,0.8,1.4")
        q3_values = [float(item.strip()) for item in raw.split(",") if item.strip()]
        offset = (
            ask_float("target 중심→실제 접촉점 X 보정(m)", 0.0),
            ask_float("target 중심→실제 접촉점 Y 보정(m)", 0.0),
            ask_float("target 중심→실제 접촉점 Z 보정(m)", 0.0),
        )
        for index, gripper_q in enumerate(q3_values, 1):
            print(f"\n샘플 {index}/{len(q3_values)}: q3={gripper_q:.4f}")
            q1 = ask_float("q1", self.current_q[0])
            q2 = ask_float("q2", self.current_q[1])
            result = self.node.command(
                "move_to_q",
                q=[q1, q2, gripper_q],
                label=f"grasp_frame_sample_{index}",
                wait_timeout_sec=45.0,
            )
            if not print_result(result):
                return
            self.current_q = (q1, q2, gripper_q)
            print(
                "필요하면 별도 validated 조종으로 clamp 중심을 calibration target에 "
                "정확히 맞춘 뒤 Enter를 누르세요."
            )
            input()
            result = self.node.command(
                "capture_grasp_sample",
                label=f"q3_{gripper_q:.4f}",
                contact_offset_base=list(offset),
                notes=ask_text("샘플 메모", ""),
                wait_timeout_sec=8.0,
            )
            if not print_result(result):
                return
        print("\n세 샘플 이상을 이용해 기하 파라미터를 fitting합니다.")
        print_result(self.node.command("fit_grasp_frame", wait_timeout_sec=15.0))

    def primitive_workflow(self) -> None:
        print("\n[메뉴 6] primitive 기록 / 시험")
        name = ask_text(
            "primitive 이름",
            "HOME",
        ).upper()
        if not name:
            return
        if ask_yes_no("기록 전에 목표 자세로 이동할까요?", False):
            if not self.maybe_move(name):
                return
        else:
            print("현재 실제/논리 자세를 기록합니다.")
        result = self.node.command(
            "record_primitive",
            name=name,
            speed_scale=ask_float("speed scale", 0.5),
            approved=ask_yes_no("이 자세를 승인합니까?", True),
            notes=ask_text("메모", ""),
            wait_timeout_sec=8.0,
        )
        if not print_result(result):
            return
        if ask_yes_no("validator를 거쳐 primitive를 다시 시험할까요?", False):
            print_result(
                self.node.command(
                    "test_primitive",
                    name=name,
                    wait_timeout_sec=45.0,
                )
            )

    def profile_workflow(self) -> None:
        print("\n[메뉴 7] 카메라 기준 grasp profile 기록")
        object_name = ask_text("물체 이름", "Buds3")
        if not self.lock_target(object_name):
            return
        result = self.node.command(
            "start_profile",
            object_name=object_name,
            speed_scale=ask_float("기본 speed scale", 0.5),
            notes=ask_text("profile 메모", ""),
            wait_timeout_sec=8.0,
        )
        if not print_result(result):
            return

        instructions = {
            "PRE_GRASP": "그리퍼가 열린 채 물체에 접근하기 전 안전 자세",
            "GRASP": "그리퍼가 열린 채 물체를 감쌀 접근 완료 자세",
            "CLOSE": "같은 q1/q2 부근에서 실제 안전 close q3까지 닫은 자세",
            "LIFT": "물체를 잡은 채 안전하게 들어 올린 자세",
            "PLACE": "선택적인 놓기 자세",
        }
        for stage in ("PRE_GRASP", "GRASP", "CLOSE", "LIFT"):
            print(f"\n--- {stage}: {instructions[stage]} ---")
            if not self.maybe_move(stage):
                return
            result = self.node.command(
                "capture_profile_stage",
                stage=stage,
                notes=ask_text(f"{stage} 메모", ""),
                wait_timeout_sec=8.0,
            )
            if not print_result(result):
                return
        if ask_yes_no("PLACE 자세도 기록할까요?", False):
            print(f"\n--- PLACE: {instructions['PLACE']} ---")
            if not self.maybe_move("PLACE"):
                return
            print_result(
                self.node.command(
                    "capture_profile_stage",
                    stage="PLACE",
                    notes=ask_text("PLACE 메모", ""),
                    wait_timeout_sec=8.0,
                )
            )

        result = self.node.command(
            "save_profile",
            notes=ask_text("최종 profile 메모", ""),
            wait_timeout_sec=12.0,
        )
        if not print_result(result):
            return
        if ask_yes_no("현재 카메라 target에 전체 pick sequence를 시험할까요?", False):
            print(
                "실제 로봇이 움직입니다. 최신 safe-region과 비상 정지를 확인하세요."
            )
            if ask_text("실행하려면 PICK 입력", "") == "PICK":
                print_result(
                    self.node.command(
                        "test_profile",
                        object_name=object_name,
                        profile=object_name,
                        wait_timeout_sec=120.0,
                    )
                )

    def show_status(self) -> None:
        print_result(self.node.command("status", wait_timeout_sec=5.0))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TeachClientNode()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    try:
        TeachWizard(node).run()
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
