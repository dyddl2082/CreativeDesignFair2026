from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import math
from pathlib import Path
import statistics
import threading
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

from rclpy.executors import MultiThreadedExecutor
import rclpy

from .grasp_frame_fit import GeometryReference, fit_grasp_frame
from .report_store import ReportStore, utc_now
from .ros_client import ArmCommissioningNode, Q
from .safe_region_analysis import SafeRegionDataset


def ask_text(prompt: str, default: Optional[str] = None, allow_blank: bool = True) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        if allow_blank:
            return ""
        print("값을 입력해 주세요.")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        value = input(f"{prompt} [{suffix}]: ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes", "예", "ㅇ"}:
            return True
        if value in {"n", "no", "아니오", "ㄴ"}:
            return False
        print("y 또는 n으로 입력해 주세요.")


def ask_float(
    prompt: str,
    default: Optional[float] = None,
    allow_blank: bool = False,
) -> Optional[float]:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if not value:
            if default is not None:
                return float(default)
            if allow_blank:
                return None
        try:
            return float(value)
        except ValueError:
            print("숫자로 입력해 주세요.")


def ask_int(prompt: str, default: int) -> int:
    while True:
        value = input(f"{prompt} [{default}]: ").strip()
        if not value:
            return default
        try:
            return int(value)
        except ValueError:
            print("정수로 입력해 주세요.")


def ask_q(prompt: str, default: Q) -> Q:
    while True:
        raw = input(
            f"{prompt} q1 q2 q3 rad "
            f"[{default[0]:.4f} {default[1]:.4f} {default[2]:.4f}]: "
        ).strip()
        if not raw:
            return default
        parts = raw.replace(",", " ").split()
        if len(parts) != 3:
            print("세 개의 rad 값을 입력해 주세요.")
            continue
        try:
            q = tuple(float(value) for value in parts)
            return q  # type: ignore[return-value]
        except ValueError:
            print("숫자로 입력해 주세요.")


def optional_measurement(prompt: str, unit: str = "") -> Optional[float]:
    suffix = f" ({unit})" if unit else ""
    return ask_float(prompt + suffix, allow_blank=True)


def numeric_summary(values: Sequence[float]) -> Dict[str, float]:
    if not values:
        return {}
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "stdev": statistics.stdev(values) if len(values) >= 2 else 0.0,
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
    }


class CommissioningWizard:
    def __init__(self, node: ArmCommissioningNode, report: ReportStore) -> None:
        self.node = node
        self.report = report
        self.safe_region: Optional[SafeRegionDataset] = None
        if node.safe_region_csv:
            try:
                self.safe_region = SafeRegionDataset(
                    node.safe_region_csv,
                    node.all_samples_csv or None,
                )
            except Exception as exc:
                print(f"[경고] safe-region 로드 실패: {exc}")

        self.report.merge_path(
            ("source",),
            {
                "actuator_limits_file": str(node.actuator_limits_file),
                "safe_region": (
                    self.safe_region.metadata() if self.safe_region else None
                ),
                "commissioning_started_at": utc_now(),
            },
        )

    def run(self) -> None:
        print("\nMacRobot 로봇팔 통합 커미셔닝 도구")
        print(f"결과 파일: {self.report.path}")
        print("각 단계의 결과는 즉시 하나의 YAML 파일에 저장됩니다.\n")
        while rclpy.ok():
            print("\n=== 메뉴 ===")
            print("0. 시스템 연결 상태 기록")
            print("1. pulse / 영점 / 방향 보정")
            print("2. 모델과 실제 방향·기구 제약 확인")
            print("3. MoveIt safe-region 대표 경계 검증")
            print("4. 반복 정밀도·하중·온도 시험")
            print("5. 실제 grasp_frame 보정")
            print("6. 기본 primitive 정의·시험")
            print("7. 물체별 grasp profile 기록")
            print("8. 현재 보고서 상태")
            print("9. 종료")
            choice = input("선택: ").strip()
            try:
                if choice == "0":
                    self.system_snapshot()
                elif choice == "1":
                    self.calibration()
                elif choice == "2":
                    self.direction_test()
                elif choice == "3":
                    self.safe_region_test()
                elif choice == "4":
                    self.repeatability_test()
                elif choice == "5":
                    self.grasp_frame_calibration()
                elif choice == "6":
                    self.primitive_test()
                elif choice == "7":
                    self.grasp_profile()
                elif choice == "8":
                    self.show_status()
                elif choice == "9":
                    break
                else:
                    print("0~9 중 하나를 입력해 주세요.")
            except KeyboardInterrupt:
                print("\n현재 동작을 중지합니다.")
                self.node.stop()
                self.report.mark_section(
                    "last_interrupted_operation",
                    "interrupted",
                    {"time": utc_now()},
                )
            except Exception as exc:
                print(f"[오류] {exc}")
                self.node.stop()
                self.report.append_path(
                    ("errors",),
                    {
                        "time": utc_now(),
                        "type": type(exc).__name__,
                        "message": str(exc),
                    },
                )

        self.report.merge_path(
            ("source",),
            {"commissioning_finished_at": utc_now()},
        )
        print(f"\n저장 완료: {self.report.path}")

    def _require_motion(self) -> bool:
        if self.node.allow_motion_commands:
            return True
        print(
            "allow_motion_commands=false입니다. "
            "실행하려면 노드 파라미터를 true로 설정하세요."
        )
        return False

    def _execute_and_review(self, q: Q, label: str) -> Dict[str, Any]:
        print(f"\n[{label}] 목표 q={q}")
        if not ask_yes_no("주변과 기구가 안전한지 확인했고 이 목표를 실행할까요?", False):
            return {"ok": False, "event": "operator_skipped", "goal": list(q)}
        result = self.node.execute_joint_goal(q)
        print(f"자동 결과: {result.get('event')}, ok={result.get('ok')}")
        return result

    def _execute_grid_path(
        self,
        path: Sequence[Q],
        label: str,
    ) -> Dict[str, Any]:
        if not path:
            return {"ok": False, "event": "empty_grid_path"}
        print(f"\n[{label}] safe-region grid waypoint {len(path)}개")
        if not ask_yes_no("이 경로 전체를 저속으로 실행할까요?", False):
            return {
                "ok": False,
                "event": "operator_skipped",
                "waypoint_count": len(path),
            }
        results = []
        # The first element is the nearest grid sample to the current state.
        for index, waypoint in enumerate(path[1:], start=1):
            result = self.node.execute_joint_goal(waypoint)
            results.append(
                {
                    "index": index,
                    "q": list(waypoint),
                    "result": result,
                }
            )
            if not result.get("ok"):
                self.node.stop()
                return {
                    "ok": False,
                    "event": "grid_path_failed",
                    "failed_index": index,
                    "waypoint_count": len(path),
                    "runs": results,
                }
        return {
            "ok": True,
            "event": "grid_path_completed",
            "waypoint_count": len(path),
            "runs": results,
            "final_q": list(path[-1]),
        }

    def system_snapshot(self) -> None:
        snapshot = self.node.system_snapshot()
        self.report.set_path(("system_snapshot",), snapshot)
        print(snapshot)

    def _raw_pulse_jog(self, axis_name: str, initial: float) -> Dict[str, Any]:
        if not self.node.allow_raw_pulse_commands:
            print("allow_raw_pulse_commands=false이므로 raw pulse jog를 생략합니다.")
            return {}
        phrase = input(
            "구동 기어를 분리했거나 매우 안전한 상태라면 RAW를 입력하세요: "
        ).strip()
        if phrase != "RAW":
            print("raw pulse jog 취소")
            return {}

        current = float(initial)
        marks: Dict[str, float] = {}
        history: List[Dict[str, Any]] = []
        print(
            "명령: +10, -10, +50, -50, 숫자(절대 pulse), "
            "min, center, max, off, done"
        )
        while True:
            command = input(f"{axis_name} pulse={current:.1f}us > ").strip().lower()
            if command == "done":
                break
            if command == "off":
                self.node.raw_servo_off(axis_name)
                history.append({"event": "off", "time": utc_now()})
                continue
            if command in {"min", "center", "max"}:
                marks[command] = current
                print(f"{command}={current:.1f}us 기록")
                continue
            delta_map = {"+10": 10.0, "-10": -10.0, "+50": 50.0, "-50": -50.0}
            try:
                target = current + delta_map[command] if command in delta_map else float(command)
            except ValueError:
                print("알 수 없는 명령")
                continue
            result = self.node.raw_pulse(axis_name, target, previous_us=current)
            current = float(result.get("target_us", current))
            history.append(
                {
                    "time": utc_now(),
                    "target_us": current,
                    "result": result,
                    "operator_safe": ask_yes_no("이 pulse에서 안전하게 움직였나요?", True),
                    "notes": ask_text("관찰 메모", "", True),
                }
            )
            if history[-1]["operator_safe"] is False:
                print("위험 관찰이 기록되어 해당 서보 출력을 즉시 해제합니다.")
                self.node.raw_servo_off(axis_name)
                break
        return {"marks": marks, "history": history, "last_pulse_us": current}

    def calibration(self) -> None:
        self.report.begin_section("pulse_zero_calibration")
        results: Dict[str, Any] = {}
        for axis_name, model_name in (
            ("lift", "MG996R left / arm tilt (CCW = forward)"),
            ("tilt", "MG996R right / rear lift (CW = up)"),
            ("gripper", "MG90S gripper"),
        ):
            axis = getattr(self.node.mapping, axis_name)
            print(f"\n--- {axis_name}: {model_name}, PCA9685 CH{axis.channel} ---")
            zero_deg = ask_float("zero_deg", axis.zero_deg)
            sign = ask_float("sign (+1 또는 -1)", axis.sign)
            pulse_min = ask_float("pulse_min_us", axis.pulse_min_us)
            pulse_center = ask_float("pulse_center_us", axis.pulse_center_us)
            pulse_max = ask_float("pulse_max_us", axis.pulse_max_us)
            command_min = ask_float("command_min_deg", axis.command_min_deg)
            command_max = ask_float("command_max_deg", axis.command_max_deg)
            raw = {}
            if ask_yes_no("전용 raw pulse jog를 수행할까요?", False):
                raw = self._raw_pulse_jog(axis_name, float(pulse_center))
                marks = raw.get("marks", {})
                pulse_min = marks.get("min", pulse_min)
                pulse_center = marks.get("center", pulse_center)
                pulse_max = marks.get("max", pulse_max)

            affects_safe_region = any(
                abs(float(new_value) - float(old_value)) > 1e-9
                for new_value, old_value in (
                    (zero_deg, axis.zero_deg),
                    (sign, axis.sign),
                    (command_min, axis.command_min_deg),
                    (command_max, axis.command_max_deg),
                )
            )
            results[axis_name] = {
                "servo_model": model_name,
                "channel": axis.channel,
                "zero_deg": zero_deg,
                "sign": sign,
                "model_multiplier": axis.model_multiplier,
                "pulse_min_us": pulse_min,
                "pulse_center_us": pulse_center,
                "pulse_max_us": pulse_max,
                "command_min_deg": command_min,
                "command_max_deg": command_max,
                "raw_pulse_jog": raw,
                "affects_safe_region": affects_safe_region,
                "operator_confirmed": ask_yes_no("이 보정값을 임시 결과로 확정할까요?", True),
                "notes": ask_text("메모", "", True),
            }

        suggested = {
            "lift_zero_deg": results["lift"]["zero_deg"],
            "lift_sign": results["lift"]["sign"],
            "lift_pulse_min_us": results["lift"]["pulse_min_us"],
            "lift_pulse_center_us": results["lift"]["pulse_center_us"],
            "lift_pulse_max_us": results["lift"]["pulse_max_us"],
            "lift_command_min_deg": results["lift"]["command_min_deg"],
            "lift_command_max_deg": results["lift"]["command_max_deg"],
            "tilt_zero_deg": results["tilt"]["zero_deg"],
            "tilt_sign": results["tilt"]["sign"],
            "tilt_pulse_min_us": results["tilt"]["pulse_min_us"],
            "tilt_pulse_center_us": results["tilt"]["pulse_center_us"],
            "tilt_pulse_max_us": results["tilt"]["pulse_max_us"],
            "tilt_command_min_deg": results["tilt"]["command_min_deg"],
            "tilt_command_max_deg": results["tilt"]["command_max_deg"],
            "gripper_zero_deg": results["gripper"]["zero_deg"],
            "gripper_sign": results["gripper"]["sign"],
            "gripper_pulse_min_us": results["gripper"]["pulse_min_us"],
            "gripper_pulse_center_us": results["gripper"]["pulse_center_us"],
            "gripper_pulse_max_us": results["gripper"]["pulse_max_us"],
            "gripper_command_min_deg": results["gripper"]["command_min_deg"],
            "gripper_command_max_deg": results["gripper"]["command_max_deg"],
        }
        self.report.complete_section(
            "pulse_zero_calibration",
            {
                "servos": results,
                "suggested_actuator_parameters": suggested,
                "requires_pipeline_restart_after_apply": True,
                "requires_safe_region_regeneration": any(
                    item.get("affects_safe_region") for item in results.values()
                ),
                "apply_command_example": (
                    "ros2 run macrobot_arm_commissioning apply_report_recommendations "
                    f"--report {self.report.path}"
                ),
            },
        )
        print(
            "\n보정값은 보고서에 저장됐습니다. 실제 validator/servo bridge에 반영하려면 "
            "apply_report_recommendations를 실행한 뒤 파이프라인을 재시작하세요."
        )
        if any(item.get("affects_safe_region") for item in results.values()):
            print(
                "zero/sign/command 범위가 바뀌었으므로 기존 safe-region CSV는 폐기하고 "
                "전체 형상 MoveIt scan을 다시 실행해야 합니다."
            )

    def direction_test(self) -> None:
        if not self._require_motion():
            return
        self.report.begin_section("direction_and_mechanism")
        home = self.node.mapping.logical_limits.home
        dq1 = self.node.direction_delta_q1
        dq2 = self.node.direction_delta_q2
        dq3 = self.node.direction_delta_q3

        print(
            "\n방향 테스트 변화량: "
            f"q1={dq1:+.3f} rad, "
            f"q2={dq2:+.3f} rad, "
            f"q3={dq3:+.3f} rad"
        )

        tests = [
            ("q1_positive", (home[0] + dq1, home[1], home[2])),
            ("q2_positive", (home[0], home[1] + dq2, home[2])),
            ("q3_positive_close", (home[0], home[1], home[2] + dq3)),
        ]
        records = []
        self._execute_and_review(home, "HOME")
        for name, q in tests:
            automatic = self._execute_and_review(q, name)
            checks = {
                "model_and_physical_direction_match": ask_yes_no(
                    "RViz 모델과 실물의 회전 방향이 일치하나요?", True
                ),
                "four_bar_parallelogram_maintained": ask_yes_no(
                    "팔 4-bar가 평행사변형을 유지하나요?", True
                ),
                "gripper_clamps_parallel": (
                    ask_yes_no("양쪽 clamp가 평행을 유지하나요?", True)
                    if name == "q3_positive_close"
                    else None
                ),
                "no_binding_or_abnormal_noise": ask_yes_no(
                    "기어·링크 binding 및 비정상 소음이 없나요?", True
                ),
            }
            records.append(
                {
                    "name": name,
                    "target_q": list(q),
                    "automatic": automatic,
                    "operator_checks": checks,
                    "notes": ask_text("관찰 메모", "", True),
                }
            )
            self._execute_and_review(home, "HOME return")
        passed = all(
            item["automatic"].get("ok")
            and all(
                value is not False
                for value in item["operator_checks"].values()
            )
            for item in records
        )
        self.report.complete_section(
            "direction_and_mechanism",
            {"home_q": list(home), "tests": records, "passed": passed},
        )

    def safe_region_test(self) -> None:
        if not self._require_motion():
            return
        if self.node.allow_raw_pulse_commands:
            print(
                "안전상 메뉴 3은 allow_raw_pulse_commands:=false에서만 실행할 수 있습니다."
            )
            return
        if self.safe_region is None:
            print("safe_region_csv가 없어 대표 경계 시험을 생성할 수 없습니다.")
            return
        self.report.begin_section(
            "moveit_representative_boundaries",
            {"safe_region": self.safe_region.metadata()},
        )
        cases = self.safe_region.representative_cases()
        print(f"{len(cases)}개 대표 자세를 생성했습니다.")
        records = []
        home = self.safe_region.nearest_home().q
        for index, case in enumerate(cases, start=1):
            print(
                f"\n[{index}/{len(cases)}] {case['name']}: "
                f"q={case['q']}\n  {case['rationale']}"
            )
            if not ask_yes_no("이 대표 자세를 실물에서 시험할까요?", True):
                records.append({**case, "status": "skipped"})
                continue
            to_home_path = self.safe_region.grid_path(self.node.current_q, home)
            home_result = self._execute_grid_path(
                to_home_path,
                "home before boundary",
            )
            if not home_result.get("ok"):
                records.append(
                    {
                        **case,
                        "status": "home_path_failed",
                        "home_path": home_result,
                    }
                )
                break

            q = tuple(float(value) for value in case["q"])
            target_path = self.safe_region.grid_path(home, q)
            automatic = self._execute_grid_path(
                target_path,
                str(case["name"]),
            )
            physical_pass = (
                ask_yes_no(
                    "저속 동작에서 충돌·binding·케이블 장력 문제가 없었나요?",
                    True,
                )
                if automatic.get("ok")
                else False
            )
            records.append(
                {
                    **case,
                    "automatic": automatic,
                    "physical_pass": physical_pass,
                    "notes": ask_text("메모", "", True),
                }
            )
            if not physical_pass:
                self.node.stop()
                print("실물 문제가 기록되어 이후 경계 시험을 중단합니다.")
                break
        final_home_path = self.safe_region.grid_path(self.node.current_q, home)
        self._execute_grid_path(final_home_path, "final home")
        self.report.complete_section(
            "moveit_representative_boundaries",
            {"cases": records},
        )

    def repeatability_test(self) -> None:
        if not self._require_motion():
            return
        previous_section = (
            self.report.snapshot()
            .get("sections", {})
            .get("repeatability_and_load", {})
        )
        previous_tests = (
            list(previous_section.get("tests", []))
            if isinstance(previous_section, dict)
            and isinstance(previous_section.get("tests"), list)
            else []
        )
        self.report.begin_section(
            "repeatability_and_load",
            {"previous_test_count": len(previous_tests)},
        )
        test_name = ask_text("시험 이름", "home_repeatability")
        load_g = ask_float("파지 하중 g", 0.0)
        repetitions = max(1, ask_int("반복 횟수", 5))
        home = self.node.mapping.logical_limits.home
        target = ask_q("반복할 목표 자세", home)

        temperatures_before = {
            axis: optional_measurement(f"{axis} 시작 온도", "°C")
            for axis in ("lift", "tilt", "gripper")
        }
        records = []
        for index in range(repetitions):
            print(f"\n반복 {index + 1}/{repetitions}")
            to_target = self._execute_and_review(target, f"{test_name} target")
            to_home = self._execute_and_review(home, f"{test_name} home")
            record = {
                "iteration": index + 1,
                "target_execution": to_target,
                "home_execution": to_home,
                "operator_pass": ask_yes_no("이번 반복이 정상적이었나요?", True),
                "home_return_error_mm": optional_measurement(
                    "HOME 복귀 위치 오차", "mm"
                ),
                "backlash_deg": optional_measurement("관찰된 백래시", "deg"),
                "measured_target_x_mm": optional_measurement(
                    "목표 자세 실제 grasp center X", "mm"
                ),
                "measured_target_z_mm": optional_measurement(
                    "목표 자세 실제 grasp center Z", "mm"
                ),
                "notes": ask_text("메모", "", True),
            }
            records.append(record)

        temperatures_after = {
            axis: optional_measurement(f"{axis} 종료 온도", "°C")
            for axis in ("lift", "tilt", "gripper")
        }
        numeric = {}
        for key in (
            "home_return_error_mm",
            "backlash_deg",
            "measured_target_x_mm",
            "measured_target_z_mm",
        ):
            values = [
                float(item[key])
                for item in records
                if item.get(key) is not None
            ]
            numeric[key] = numeric_summary(values)
        temp_rise = {
            axis: (
                temperatures_after[axis] - temperatures_before[axis]
                if temperatures_after[axis] is not None
                and temperatures_before[axis] is not None
                else None
            )
            for axis in temperatures_before
        }
        payload = {
            "tests": [
                {
                    "name": test_name,
                    "load_g": load_g,
                    "target_q": list(target),
                    "repetitions": repetitions,
                    "temperatures_before_c": temperatures_before,
                    "temperatures_after_c": temperatures_after,
                    "temperature_rise_c": temp_rise,
                    "runs": records,
                    "statistics": numeric,
                }
            ]
        }
        payload["tests"] = previous_tests + payload["tests"]
        self.report.complete_section("repeatability_and_load", payload)

    def grasp_frame_calibration(self) -> None:
        if not self._require_motion():
            return
        self.report.begin_section("grasp_frame_calibration")
        q1 = float(ask_float("측정 자세 q1", self.node.current_q[0]))
        q2 = float(ask_float("측정 자세 q2", self.node.current_q[1]))
        close_q3 = (
            self.safe_region.safe_close_q3()
            if self.safe_region
            else self.node.mapping.logical_limits.q3_max
        )
        defaults = [0.0, 0.8, close_q3]
        raw_q3 = ask_text(
            "측정 q3 목록(rad, 쉼표 구분)",
            ",".join(f"{value:.6f}" for value in defaults),
        )
        q3_values = [float(value.strip()) for value in raw_q3.split(",")]
        frame = ask_text("측정 좌표계(base_link 또는 wrist)", "base_link")
        if frame not in {"base_link", "wrist"}:
            raise ValueError("measurement frame must be base_link or wrist")

        samples = []
        for q3 in q3_values:
            automatic = self._execute_and_review((q1, q2, q3), f"grasp frame q3={q3:.3f}")
            print(
                "두 clamp의 실제 접촉 중심을 측정하세요. "
                "입력 단위는 mm이며 보고서에는 m로 저장됩니다."
            )
            measured_x_mm = ask_float("측정 X", allow_blank=False)
            measured_z_mm = ask_float("측정 Z", allow_blank=False)
            measured_y_mm = optional_measurement("측정 Y", "mm")
            gap_mm = optional_measurement("실제 clamp 간격", "mm")
            sample: Dict[str, Any] = {
                "q1": q1,
                "q2": q2,
                "q3": q3,
                "measurement_frame": frame,
                "measured_x": float(measured_x_mm) / 1000.0,
                "measured_z": float(measured_z_mm) / 1000.0,
                "measured_y": (
                    float(measured_y_mm) / 1000.0
                    if measured_y_mm is not None
                    else None
                ),
                "measured_gap": (
                    float(gap_mm) / 1000.0 if gap_mm is not None else None
                ),
                "model_tool_pose": automatic.get("tool_pose"),
                "automatic": automatic,
                "notes": ask_text("메모", "", True),
            }
            samples.append(sample)

        reference = GeometryReference(
            pivot_x=float(ask_float("pivot_x", 0.02095)),
            pivot_z=float(ask_float("pivot_z", 0.064595)),
            main_link_length=float(ask_float("main_link_length", 0.10000)),
        )
        fit_samples = [
            {key: value for key, value in sample.items() if value is not None}
            for sample in samples
        ]
        fitted = fit_grasp_frame(fit_samples, reference)
        print("\n추천 기하값:")
        for key in (
            "tool_offset_x",
            "tool_offset_z",
            "gripper_link_length",
            "gripper_base_separation",
            "rms_error_m",
            "max_error_m",
        ):
            if key in fitted:
                print(f"  {key}: {fitted[key]}")
        self.report.complete_section(
            "grasp_frame_calibration",
            {
                "reference_geometry": reference.__dict__,
                "samples": samples,
                "fit": fitted,
                "recommended_kinematics_parameters": {
                    key: fitted[key]
                    for key in (
                        "tool_offset_x",
                        "tool_offset_z",
                        "gripper_link_length",
                        "gripper_base_separation",
                    )
                    if key in fitted
                },
            },
        )

    def primitive_test(self) -> None:
        if not self._require_motion():
            return
        existing = (
            self.report.snapshot().get("sections", {}).get("primitives", {})
        )
        self.report.begin_section("primitives")
        primitives: Dict[str, Any] = {}
        if isinstance(existing, dict) and isinstance(existing.get("primitives"), dict):
            primitives.update(existing["primitives"])

        home = self.node.mapping.logical_limits.home
        close_q3 = (
            self.safe_region.safe_close_q3()
            if self.safe_region
            else self.node.mapping.logical_limits.q3_max
        )
        defaults: Dict[str, Q] = {
            "HOME": home,
            "STOW": home,
            "OPEN": (home[0], home[1], 0.0),
            "CLOSE": (home[0], home[1], close_q3),
            "PRE_GRASP": home,
            "LOWER": home,
            "LIFT": home,
            "PLACE": home,
        }
        for name in (
            "HOME",
            "STOW",
            "OPEN",
            "CLOSE",
            "PRE_GRASP",
            "LOWER",
            "LIFT",
            "PLACE",
        ):
            print(f"\n--- {name} ---")
            old = primitives.get(name, {})
            old_q = old.get("target_q") if isinstance(old, dict) else None
            default = (
                tuple(float(value) for value in old_q)
                if isinstance(old_q, list) and len(old_q) == 3
                else defaults[name]
            )
            action = ask_text("e=직접 입력, c=현재 자세, s=건너뜀", "e").lower()
            if action == "s":
                continue
            q = self.node.current_q if action == "c" else ask_q("목표 자세", default)
            execution = self._execute_and_review(q, name)
            primitives[name] = {
                "target_q": list(q),
                "speed_scale": ask_float("향후 primitive speed scale", 1.0),
                "automatic": execution,
                "operator_pass": ask_yes_no("이 primitive를 승인할까요?", True),
                "notes": ask_text("메모", "", True),
            }

        stop_test = None
        if ask_yes_no("STOP 동작을 시험할까요?", True):
            self.node.stop()
            stop_test = {
                "time": utc_now(),
                "operator_pass": ask_yes_no("STOP이 정상 동작했나요?", True),
                "notes": ask_text("STOP 메모", "", True),
            }
        disable_test = None
        if ask_yes_no("DISABLE을 시험할까요? 팔을 손으로 받쳐야 합니다.", False):
            phrase = input("팔을 받치고 있다면 DISABLE을 입력하세요: ").strip()
            if phrase == "DISABLE":
                self.node.disable()
                disable_test = {
                    "time": utc_now(),
                    "operator_pass": ask_yes_no("서보 토크가 안전하게 해제됐나요?", True),
                    "notes": ask_text("DISABLE 메모", "", True),
                }

        self.report.complete_section(
            "primitives",
            {
                "primitives": primitives,
                "stop_test": stop_test,
                "disable_test": disable_test,
            },
        )

    def _get_pose_definition(self, label: str, primitives: Dict[str, Any]) -> Q:
        source = ask_text(
            f"{label}: primitive 이름 또는 e(직접 입력), c(현재 자세)",
            "c",
        ).upper()
        if source == "C":
            return self.node.current_q
        if source == "E":
            return ask_q(label, self.node.current_q)
        primitive = primitives.get(source)
        if isinstance(primitive, dict):
            q = primitive.get("target_q")
            if isinstance(q, list) and len(q) == 3:
                return tuple(float(value) for value in q)  # type: ignore[return-value]
        print(f"primitive {source}를 찾지 못해 직접 입력으로 전환합니다.")
        return ask_q(label, self.node.current_q)

    def grasp_profile(self) -> None:
        if not self._require_motion():
            return
        object_name = ask_text("물체 이름", allow_blank=False)
        snapshot = self.report.snapshot()
        self.report.begin_section("grasp_profiles", {"active_object": object_name})
        primitives = (
            snapshot.get("sections", {})
            .get("primitives", {})
            .get("primitives", {})
        )
        if not isinstance(primitives, dict):
            primitives = {}

        profile = {
            "object_name": object_name,
            "pre_grasp_q": list(self._get_pose_definition("pre_grasp", primitives)),
            "grasp_q": list(self._get_pose_definition("grasp/lower", primitives)),
            "lift_q": list(self._get_pose_definition("lift", primitives)),
            "place_q": list(self._get_pose_definition("place", primitives)),
            "close_q3": float(
                ask_float(
                    "close q3",
                    (
                        self.safe_region.safe_close_q3()
                        if self.safe_region
                        else self.node.mapping.logical_limits.q3_max
                    ),
                )
            ),
            "sequence": [
                item.strip().upper()
                for item in ask_text(
                    "접근 순서(쉼표 구분)",
                    "OPEN,PRE_GRASP,GRASP,CLOSE,LIFT",
                ).split(",")
                if item.strip()
            ],
            "speed_scale": float(ask_float("기본 speed scale", 0.5)),
            "notes": ask_text("물체 파지 메모", "", True),
            "created_at": utc_now(),
        }

        if ask_yes_no("이 profile의 자세들을 순서대로 시험할까요?", False):
            test_results = []
            open_q = list(profile["pre_grasp_q"])
            open_q[2] = 0.0
            grasp_q = list(profile["grasp_q"])
            close_q = list(grasp_q)
            close_q[2] = profile["close_q3"]
            sequence_q = [
                ("OPEN", tuple(open_q)),
                ("PRE_GRASP", tuple(profile["pre_grasp_q"])),
                ("GRASP", tuple(grasp_q)),
                ("CLOSE", tuple(close_q)),
                ("LIFT", tuple(profile["lift_q"])),
            ]
            for name, q in sequence_q:
                result = self._execute_and_review(q, f"profile {name}")
                test_results.append({"name": name, "q": list(q), "result": result})
                if not result.get("ok"):
                    break
            profile["test_results"] = test_results
            profile["operator_pass"] = ask_yes_no("전체 파지 sequence를 승인할까요?", True)

        profiles = (
            snapshot.get("sections", {})
            .get("grasp_profiles", {})
            .get("profiles", {})
        )
        if not isinstance(profiles, dict):
            profiles = {}
        profiles[object_name] = profile
        self.report.complete_section(
            "grasp_profiles",
            {"profiles": profiles, "last_recorded": object_name},
        )

    def show_status(self) -> None:
        print(f"보고서: {self.report.path}")
        for section, status in self.report.section_statuses().items():
            print(f"  {section}: {status}")
        print("현재 ROS 상태:")
        print(self.node.system_snapshot())


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ArmCommissioningNode()
    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()
    report = ReportStore(node.report_path)
    wizard = CommissioningWizard(node, report)

    try:
        wizard.run()
    except KeyboardInterrupt:
        node.stop()
    finally:
        report.save()
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        spin_thread.join(timeout=1.0)


if __name__ == "__main__":
    main()
