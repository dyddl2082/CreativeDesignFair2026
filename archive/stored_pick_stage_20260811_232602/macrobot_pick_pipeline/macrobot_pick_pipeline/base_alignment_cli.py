from __future__ import annotations

import json
import threading
import time
from typing import Optional

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String


class BaseAlignmentCliNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_base_alignment_cli")
        self.goal_pub = self.create_publisher(
            String, "/macrobot/align_pick/goal", 10
        )
        self.record_pub = self.create_publisher(
            String, "/macrobot/base_alignment/record", 10
        )
        self.admin_pub = self.create_publisher(
            String, "/macrobot/base_alignment/admin", 10
        )
        self.cancel_pub = self.create_publisher(
            String, "/macrobot/base_alignment/cancel", 10
        )
        self.create_subscription(
            String,
            "/macrobot/base_alignment/status",
            self._status_callback,
            20,
        )
        self.create_subscription(
            String,
            "/macrobot/base_alignment/result",
            self._result_callback,
            20,
        )
        self.last_status: Optional[dict] = None
        self.last_result: Optional[dict] = None

    @staticmethod
    def _decode(text: str):
        try:
            value = json.loads(text)
            return value if isinstance(value, dict) else {"raw": value}
        except Exception:
            return {"raw": text}

    def _status_callback(self, msg: String) -> None:
        self.last_status = self._decode(msg.data)
        print("\n[ALIGN STATUS]")
        print(json.dumps(self.last_status, ensure_ascii=False, indent=2))
        print("align> ", end="", flush=True)

    def _result_callback(self, msg: String) -> None:
        self.last_result = self._decode(msg.data)
        print("\n[ALIGN RESULT]")
        print(json.dumps(self.last_result, ensure_ascii=False, indent=2))
        print("align> ", end="", flush=True)

    @staticmethod
    def _publish(pub, payload) -> None:
        msg = String()
        msg.data = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        pub.publish(msg)


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def _menu() -> None:
    print(
        """
MacRobot base alignment / align-and-pick

1. 저장된 정렬 profile 목록
2. 현재 잡을 수 있는 위치를 정렬 profile로 기록
3. 기록된 위치로 차체만 정렬
4. 기록된 위치로 정렬한 뒤 물체 잡기
5. 정렬/잡기 취소 및 차체 STOP
6. 정렬 profile 삭제
7. 마지막 상태/결과 보기
9. 종료
""".strip()
    )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = BaseAlignmentCliNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    time.sleep(0.25)

    try:
        while rclpy.ok():
            _menu()
            choice = input("align> ").strip()
            if choice == "1":
                node._publish(node.admin_pub, {"action": "list"})
            elif choice == "2":
                object_name = _ask("물체 이름", "Buds3")
                alignment_profile = _ask("정렬 profile 이름", object_name)
                pick_profile = _ask("연결할 pick profile 이름", object_name)
                print(
                    "로봇을 실제로 잡을 수 있는 위치에 수동 배치하고, "
                    "물체가 카메라에 안정적으로 보이는지 확인하세요."
                )
                confirm = input("기록하려면 RECORD 입력: ").strip()
                if confirm != "RECORD":
                    print("취소했습니다.")
                    continue
                node._publish(
                    node.record_pub,
                    {
                        "object_name": object_name,
                        "alignment_profile": alignment_profile,
                        "pick_profile": pick_profile,
                    },
                )
            elif choice in {"3", "4"}:
                object_name = _ask("물체 이름", "Buds3")
                alignment_profile = _ask("정렬 profile 이름", object_name)
                pick_profile = _ask("pick profile 이름", object_name)
                execute_pick = choice == "4"
                if execute_pick:
                    confirm = input(
                        "차체와 로봇팔이 움직입니다. 실행하려면 ALIGN_PICK 입력: "
                    ).strip()
                    if confirm != "ALIGN_PICK":
                        print("취소했습니다.")
                        continue
                else:
                    confirm = input(
                        "차체가 움직입니다. 실행하려면 ALIGN 입력: "
                    ).strip()
                    if confirm != "ALIGN":
                        print("취소했습니다.")
                        continue
                node._publish(
                    node.goal_pub,
                    {
                        "object_name": object_name,
                        "alignment_profile": alignment_profile,
                        "pick_profile": pick_profile,
                        "execute_pick": execute_pick,
                    },
                )
            elif choice == "5":
                node._publish(node.cancel_pub, "user_cancel")
            elif choice == "6":
                name = _ask("삭제할 profile 이름")
                if name:
                    node._publish(node.admin_pub, {"action": "delete", "profile": name})
            elif choice == "7":
                print("last_status:")
                print(json.dumps(node.last_status, ensure_ascii=False, indent=2))
                print("last_result:")
                print(json.dumps(node.last_result, ensure_ascii=False, indent=2))
            elif choice == "9":
                break
            else:
                print("지원하지 않는 메뉴입니다.")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        thread.join(timeout=1.0)


if __name__ == "__main__":
    main()
