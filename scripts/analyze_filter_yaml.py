#!/usr/bin/env python3
"""Analyze ROS 2 candidate_filter YAML logs.

The input is expected to be produced by a command similar to:

    timeout 15s ros2 topic echo \
      --no-daemon --spin-time 3.0 \
      /candidate_filter/results \
      macrobot_interfaces/msg/CandidateFilterResult \
      > Buds3_front_40cm.yaml

The file may contain one YAML document or many ROS 2 messages separated by
"---". Scores with value -1 are treated as unavailable.
"""

from __future__ import annotations

import argparse
import math
import re
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - user environment check
    raise SystemExit(
        "PyYAML이 필요합니다. Ubuntu/WSL에서 다음을 실행하세요:\n"
        "  sudo apt update && sudo apt install -y python3-yaml"
    ) from exc


SCORE_FIELDS: tuple[tuple[str, str], ...] = (
    ("objectness_score", "Objectness"),
    ("target_hint_score", "Target hint"),
    ("depth_score", "Depth"),
    ("quality_score", "품질"),
    ("color_score", "색상"),
    ("shape_score", "형상"),
    ("physical_size_score", "물리 크기"),
)

RAW_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("sharpness", "선명도", ""),
    ("mean_brightness", "평균 밝기", ""),
    ("dark_ratio", "어두운 픽셀 비율", ""),
    ("bright_clip_ratio", "과다 노출 비율", ""),
    ("edge_density", "에지 밀도", ""),
    ("aspect_ratio", "가로세로 비", ""),
    ("estimated_width_m", "추정 폭", "m"),
    ("estimated_height_m", "추정 높이", "m"),
    ("sync_offset_abs_sec", "RGB-Depth 시간차", "s"),
    ("candidate.median_depth_m", "대표 거리", "m"),
    ("candidate.valid_depth_ratio", "유효 Depth 비율", ""),
    ("candidate.depth_std_m", "Depth 표준편차", "m"),
    ("candidate.fill_ratio", "전경 채움 비율", ""),
    ("candidate.foreground_height_m", "평면 돌출 높이", "m"),
    ("candidate.proposal_score", "Depth 후보 점수", ""),
    ("mask_fill_ratio", "Mask 채움 비율", ""),
    ("mask_solidity", "Mask solidity", ""),
)

DEFAULT_PARAMS: dict[str, Any] = {
    "min_objectness_score": 0.45,
    "enforce_objectness_score": False,
    "min_color_score": 0.18,
    "enable_color_hard_reject": False,
    "enable_physical_size_filter": False,
    "depth_weight": 0.30,
    "quality_weight": 0.20,
    "color_weight": 0.25,
    "shape_weight": 0.20,
    "physical_size_weight": 0.05,
    "min_sharpness": 2.0,
    "sharpness_good": 80.0,
    "max_dark_ratio": 0.98,
    "max_bright_clip_ratio": 0.98,
    "max_sync_offset_sec": 0.150,
    "sync_good_sec": 0.020,
    "hard_aspect_ratio_min": 0.15,
    "hard_aspect_ratio_max": 6.0,
    "preferred_aspect_ratio_min": 0.45,
    "preferred_aspect_ratio_max": 2.20,
    "min_fill_ratio": 0.05,
    "max_edge_density": 0.70,
    "min_depth_m": 0.18,
    "max_depth_m": 1.50,
    "min_valid_depth_ratio": 0.35,
    "max_depth_std_m": 0.20,
}

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
LOG_LINE_RE = re.compile(
    r"^\s*(?:\[(?:INFO|WARN|WARNING|ERROR|DEBUG|FATAL)\]|"
    r"(?:INFO|WARN|WARNING|ERROR|DEBUG|FATAL):)"
)


@dataclass(frozen=True)
class SummaryStats:
    count: int
    mean: float
    median: float
    stdev: float
    minimum: float
    p10: float
    p25: float
    p75: float
    p90: float
    maximum: float

    @property
    def iqr(self) -> float:
        return self.p75 - self.p25


class InputError(RuntimeError):
    """Raised for malformed or unsupported input files."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "candidate_filter의 ROS 2 YAML 기록을 읽어 ACCEPT/REJECT, "
            "각 score 분포와 임계값 통과율을 평가합니다."
        )
    )
    parser.add_argument("yaml_file", type=Path, help="분석할 ROS 2 YAML 파일")
    parser.add_argument(
        "--expected",
        choices=("positive", "negative", "unknown"),
        default="unknown",
        help=(
            "positive=Buds3 데이터, negative=다른 물체, "
            "unknown=단순 통계만 평가 (기본값)"
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        help=(
            "candidate_filter.yaml 경로. 지정하면 현재 threshold와 "
            "enforce 설정을 읽습니다."
        ),
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help="종합점수 임계값을 직접 지정합니다. --config보다 우선합니다.",
    )
    parser.add_argument(
        "--show-raw",
        action="store_true",
        help="점수 외의 선명도, 시간차, 거리 등 원시 지표 표도 출력합니다.",
    )
    parser.add_argument(
        "--top-reasons",
        type=int,
        default=8,
        help="표시할 거절 사유 개수 (기본 8)",
    )
    return parser.parse_args()


def clean_yaml_text(text: str) -> str:
    text = ANSI_RE.sub("", text).replace("\r\n", "\n")
    # ros2cli 로그가 stdout에 섞인 경우, 명백한 로그 행만 제거합니다.
    lines = [line for line in text.splitlines() if not LOG_LINE_RE.match(line)]
    return "\n".join(lines)


def load_yaml_documents(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise InputError(f"파일을 찾을 수 없습니다: {path}")

    text = clean_yaml_text(path.read_text(encoding="utf-8", errors="replace"))
    try:
        loaded = list(yaml.safe_load_all(text))
    except yaml.YAMLError as exc:
        raise InputError(
            f"YAML 파싱에 실패했습니다: {path}\n"
            "ros2 topic echo 출력 외의 문장이 파일에 섞였는지 확인하세요.\n"
            f"상세 오류: {exc}"
        ) from exc

    messages: list[dict[str, Any]] = []
    for item in loaded:
        if not isinstance(item, dict):
            continue

        # FilteredCandidateCrop 같은 wrapper를 잘못 기록한 경우도 최소한 지원합니다.
        if isinstance(item.get("result"), dict) and "objectness_score" in item["result"]:
            item = item["result"]

        if "objectness_score" in item or "accepted" in item or "reject_reason" in item:
            messages.append(item)

    if not messages:
        raise InputError(
            "CandidateFilterResult 메시지를 찾지 못했습니다. "
            "파일이 /candidate_filter/results에서 기록되었는지 확인하세요."
        )
    return messages


def load_params(config_path: Path | None) -> tuple[dict[str, Any], str]:
    params = dict(DEFAULT_PARAMS)
    if config_path is None:
        return params, "스크립트 내 candidate_filter v1 기본값"

    if not config_path.is_file():
        raise InputError(f"설정 파일을 찾을 수 없습니다: {config_path}")

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise InputError(f"설정 YAML 파싱 실패: {config_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise InputError(f"설정 YAML 최상위가 mapping이 아닙니다: {config_path}")

    candidate_section: Any = data.get("candidate_filter", data)
    if isinstance(candidate_section, dict):
        candidate_section = candidate_section.get("ros__parameters", candidate_section)

    if not isinstance(candidate_section, dict):
        raise InputError(
            "설정 파일에서 candidate_filter.ros__parameters를 찾지 못했습니다."
        )

    params.update(candidate_section)
    return params, str(config_path)


def nested_get(mapping: Mapping[str, Any], dotted_key: str) -> Any:
    current: Any = mapping
    for part in dotted_key.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def finite_number(value: Any, *, unavailable_below_zero: bool = False) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    if unavailable_below_zero and number < 0.0:
        return None
    return number


def values_for(
    messages: Sequence[Mapping[str, Any]],
    key: str,
    *,
    unavailable_below_zero: bool = False,
) -> list[float]:
    result: list[float] = []
    for message in messages:
        value = finite_number(
            nested_get(message, key),
            unavailable_below_zero=unavailable_below_zero,
        )
        if value is not None:
            result.append(value)
    return result


def percentile(sorted_values: Sequence[float], q: float) -> float:
    if not sorted_values:
        return math.nan
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = (len(sorted_values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])
    fraction = position - lower
    return float(
        sorted_values[lower] * (1.0 - fraction)
        + sorted_values[upper] * fraction
    )


def summarize(values: Sequence[float]) -> SummaryStats | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    return SummaryStats(
        count=len(ordered),
        mean=statistics.fmean(ordered),
        median=statistics.median(ordered),
        stdev=statistics.stdev(ordered) if len(ordered) >= 2 else 0.0,
        minimum=ordered[0],
        p10=percentile(ordered, 0.10),
        p25=percentile(ordered, 0.25),
        p75=percentile(ordered, 0.75),
        p90=percentile(ordered, 0.90),
        maximum=ordered[-1],
    )


def pct(numerator: int | float, denominator: int | float) -> float:
    return 0.0 if denominator == 0 else 100.0 * float(numerator) / float(denominator)


def normalized_score_label(stats: SummaryStats, field: str, threshold: float) -> str:
    median = stats.median
    if field == "objectness_score":
        margin = median - threshold
        if stats.p10 >= threshold + 0.05:
            base = "높고 안정적"
        elif median >= threshold + 0.10:
            base = "높음"
        elif median >= threshold:
            base = "통과권이나 경계"
        elif median >= threshold - 0.10:
            base = "임계값 바로 아래"
        else:
            base = "낮음"
        return f"{base} (중앙값 여유 {margin:+.3f})"

    if median >= 0.75:
        level = "높음"
    elif median >= 0.60:
        level = "양호"
    elif median >= 0.45:
        level = "경계"
    else:
        level = "낮음"

    if stats.iqr <= 0.10:
        consistency = "안정"
    elif stats.iqr <= 0.20:
        consistency = "변동 보통"
    else:
        consistency = "변동 큼"
    return f"{level}, {consistency}"


def print_rule(char: str = "=", width: int = 92) -> None:
    print(char * width)


def print_score_table(
    messages: Sequence[Mapping[str, Any]], threshold: float
) -> dict[str, SummaryStats | None]:
    summaries: dict[str, SummaryStats | None] = {}
    print("\n[점수 분포]")
    print(
        f"{'항목':<12} {'N':>5} {'평균':>8} {'중앙':>8} {'P10':>8} "
        f"{'P90':>8} {'최소':>8} {'최대':>8}  평가"
    )
    print_rule("-", 108)
    for field, label in SCORE_FIELDS:
        stats = summarize(
            values_for(messages, field, unavailable_below_zero=True)
        )
        summaries[field] = stats
        if stats is None:
            print(f"{label:<12} {'0':>5} {'-':>8} {'-':>8} {'-':>8} {'-':>8} {'-':>8} {'-':>8}  사용 불가")
            continue
        evaluation = normalized_score_label(stats, field, threshold)
        print(
            f"{label:<12} {stats.count:>5d} {stats.mean:>8.3f} "
            f"{stats.median:>8.3f} {stats.p10:>8.3f} {stats.p90:>8.3f} "
            f"{stats.minimum:>8.3f} {stats.maximum:>8.3f}  {evaluation}"
        )
    return summaries


def print_raw_table(messages: Sequence[Mapping[str, Any]]) -> None:
    print("\n[원시 지표 분포]")
    print(
        f"{'항목':<22} {'N':>5} {'평균':>11} {'중앙':>11} "
        f"{'P10':>11} {'P90':>11} {'최소':>11} {'최대':>11}"
    )
    print_rule("-", 102)
    for field, label, unit in RAW_FIELDS:
        stats = summarize(values_for(messages, field, unavailable_below_zero=True))
        if stats is None:
            print(f"{label:<22} {'0':>5} {'-':>11} {'-':>11} {'-':>11} {'-':>11} {'-':>11} {'-':>11}")
            continue
        suffix = unit
        print(
            f"{label:<22} {stats.count:>5d} "
            f"{stats.mean:>10.4f}{suffix:<1} {stats.median:>10.4f}{suffix:<1} "
            f"{stats.p10:>10.4f}{suffix:<1} {stats.p90:>10.4f}{suffix:<1} "
            f"{stats.minimum:>10.4f}{suffix:<1} {stats.maximum:>10.4f}{suffix:<1}"
        )


def bool_count(messages: Sequence[Mapping[str, Any]], key: str, desired: bool) -> int:
    return sum(1 for msg in messages if nested_get(msg, key) is desired)


def render_overall_verdict(
    *,
    expected: str,
    actual_accept_rate: float,
    virtual_pass_rate: float,
    filter_stats: SummaryStats | None,
    threshold: float,
    hard_reject_rate: float,
) -> tuple[str, list[str]]:
    notes: list[str] = []
    if filter_stats is None:
        return "판정 불가", ["사용 가능한 objectness_score가 없습니다."]

    if expected == "positive":
        # 실제 accepted는 soft enforcement 설정에 영향을 받으므로 둘 다 평가합니다.
        if virtual_pass_rate >= 90.0 and hard_reject_rate <= 10.0:
            verdict = "좋음: positive recall 관점에서 안정적"
        elif virtual_pass_rate >= 75.0 and hard_reject_rate <= 20.0:
            verdict = "주의: 일부 Buds3가 임계값 또는 hard filter에서 탈락 가능"
        else:
            verdict = "문제 가능성 큼: 현재 threshold에서 Buds3 손실이 많음"

        notes.append(
            f"현재 임계값 {threshold:.3f}을 적용한다고 가정한 통과율은 "
            f"{virtual_pass_rate:.1f}%입니다."
        )
        notes.append(
            f"positive의 하위 10% 점수(P10)는 {filter_stats.p10:.3f}입니다. "
            "recall을 우선하면 threshold를 이 값보다 충분히 낮게 두는 편이 안전합니다."
        )
        if actual_accept_rate - virtual_pass_rate > 10.0:
            notes.append(
                "실제 ACCEPT 비율보다 가상 threshold 통과율이 훨씬 낮습니다. "
                "노드가 관찰 모드(enforce_soft_score=false)일 가능성이 있습니다."
            )
        return verdict, notes

    if expected == "negative":
        virtual_false_accept_rate = virtual_pass_rate
        if virtual_false_accept_rate <= 10.0:
            verdict = "좋음: 현재 threshold에서 negative 억제가 강함"
        elif virtual_false_accept_rate <= 30.0:
            verdict = "주의: 일부 negative가 embedding 단계까지 통과함"
        else:
            verdict = "분리력 부족: filter만으로 negative를 충분히 제거하지 못함"

        notes.append(
            f"현재 임계값 {threshold:.3f} 기준 가상 false-accept 비율은 "
            f"{virtual_false_accept_rate:.1f}%입니다."
        )
        notes.append(
            f"negative의 상위 10% 경계(P90)는 {filter_stats.p90:.3f}입니다. "
            "이 데이터만 놓고 90% 이상을 점수로 제거하려면 threshold가 "
            "대체로 P90보다 높아야 합니다."
        )
        notes.append(
            "흰색 마우스처럼 목표와 비슷한 물체가 통과해도 실패로 단정하지 마세요. "
            "그 후보는 이후 embedding 및 negative margin에서 제거할 수 있습니다."
        )
        return verdict, notes

    return (
        "기술 통계 완료",
        [
            "--expected positive 또는 --expected negative를 지정하면 "
            "목적에 맞는 recall/false-accept 평가를 추가로 제공합니다."
        ],
    )


def diagnostic_notes(
    messages: Sequence[Mapping[str, Any]],
    summaries: Mapping[str, SummaryStats | None],
    params: Mapping[str, Any],
) -> list[str]:
    notes: list[str] = []
    total = len(messages)

    profile_true = bool_count(messages, "reference_profile_available", True)
    camera_true = bool_count(messages, "camera_info_available", True)
    if profile_true < total:
        notes.append(
            f"등록 색상 프로필 사용 가능 메시지: {profile_true}/{total} "
            f"({pct(profile_true, total):.1f}%). color_score=-1 여부를 확인하세요."
        )
    if camera_true < total:
        notes.append(
            f"CameraInfo 사용 가능 메시지: {camera_true}/{total} "
            f"({pct(camera_true, total):.1f}%). physical_size_score가 비활성일 수 있습니다."
        )

    color_stats = summaries.get("color_score")
    if color_stats is None:
        notes.append(
            "유효한 color_score가 없습니다. WSL의 등록 이미지 경로와 "
            "/candidate_filter/reload_profile 결과를 확인하세요."
        )

    physical_stats = summaries.get("physical_size_score")
    if physical_stats is None:
        notes.append(
            "physical_size_score가 없습니다. 현재 physical-size hard filter를 "
            "사용하지 않는다면 정상입니다."
        )

    # Raw metric checks use percentile summaries to avoid warning on one outlier.
    sharpness = summarize(values_for(messages, "sharpness", unavailable_below_zero=True))
    if sharpness and sharpness.p10 < float(params.get("min_sharpness", 2.0)):
        notes.append(
            f"선명도 P10={sharpness.p10:.3f}이 hard 기준 "
            f"{float(params.get('min_sharpness', 2.0)):.3f}보다 낮습니다."
        )

    sync = summarize(values_for(messages, "sync_offset_abs_sec", unavailable_below_zero=True))
    if sync and sync.p90 > float(params.get("max_sync_offset_sec", 0.150)):
        notes.append(
            f"RGB-Depth 시간차 P90={sync.p90:.4f}s가 hard 기준 "
            f"{float(params.get('max_sync_offset_sec', 0.150)):.4f}s를 넘습니다."
        )

    valid_depth = summarize(
        values_for(messages, "candidate.valid_depth_ratio", unavailable_below_zero=True)
    )
    if valid_depth and valid_depth.p10 < float(params.get("min_valid_depth_ratio", 0.35)):
        notes.append(
            f"유효 Depth 비율 P10={valid_depth.p10:.3f}이 hard 기준 "
            f"{float(params.get('min_valid_depth_ratio', 0.35)):.3f}보다 낮습니다."
        )

    depth_std = summarize(
        values_for(messages, "candidate.depth_std_m", unavailable_below_zero=True)
    )
    if depth_std and depth_std.p90 > float(params.get("max_depth_std_m", 0.20)):
        notes.append(
            f"Depth 표준편차 P90={depth_std.p90:.3f}m가 hard 기준 "
            f"{float(params.get('max_depth_std_m', 0.20)):.3f}m를 넘습니다."
        )

    return notes


def main() -> int:
    args = parse_args()
    try:
        messages = load_yaml_documents(args.yaml_file)
        params, config_source = load_params(args.config)
    except InputError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 2

    threshold = (
        float(args.threshold)
        if args.threshold is not None
        else float(params.get("min_objectness_score", 0.45))
    )
    if not 0.0 <= threshold <= 1.0:
        print("오류: threshold는 0.0~1.0 범위여야 합니다.", file=sys.stderr)
        return 2

    total = len(messages)
    accepted = sum(bool(msg.get("accepted", False)) for msg in messages)
    rejected = total - accepted
    actual_accept_rate = pct(accepted, total)

    stages = Counter(str(msg.get("reject_stage", "") or "none") for msg in messages)
    reasons = Counter(
        str(msg.get("reject_reason", "") or "passed") for msg in messages
    )
    hard_rejects = stages.get("hard", 0)
    hard_reject_rate = pct(hard_rejects, total)

    filter_values = values_for(messages, "objectness_score", unavailable_below_zero=True)
    virtual_passes = sum(value >= threshold for value in filter_values)
    virtual_pass_rate = pct(virtual_passes, len(filter_values))

    expected_ko = {
        "positive": "positive(Buds3)",
        "negative": "negative(다른 물체)",
        "unknown": "미지정",
    }[args.expected]

    print_rule()
    print("Candidate Filter YAML 평가")
    print_rule()
    print(f"파일             : {args.yaml_file.expanduser().resolve()}")
    print(f"메시지 수        : {total}")
    print(f"데이터 기대 역할 : {expected_ko}")
    print(f"설정 기준        : {config_source}")
    print(f"평가 threshold   : {threshold:.3f}")
    print(
        f"실제 판정        : ACCEPT {accepted} ({actual_accept_rate:.1f}%), "
        f"REJECT {rejected} ({pct(rejected, total):.1f}%)"
    )
    if filter_values:
        print(
            f"가상 soft 판정   : score >= {threshold:.3f}인 메시지 "
            f"{virtual_passes}/{len(filter_values)} ({virtual_pass_rate:.1f}%)"
        )
    else:
        print("가상 soft 판정   : 유효한 objectness_score 없음")
    print(
        "주의             : 실제 ACCEPT는 노드의 hard filter와 "
        "enforce_soft_score 설정을 반영하고, 가상 soft 판정은 "
        "오직 objectness_score threshold만 적용합니다."
    )

    print("\n[거절 단계]")
    for stage, count in stages.most_common():
        label = {
            "none": "통과/거절 단계 없음",
            "hard": "hard reject",
            "soft": "soft reject",
            "decode": "JPEG decode reject",
        }.get(stage, stage)
        print(f"- {label}: {count} ({pct(count, total):.1f}%)")

    print("\n[주요 결과/거절 사유]")
    for reason, count in reasons.most_common(max(1, args.top_reasons)):
        print(f"- {reason}: {count} ({pct(count, total):.1f}%)")

    summaries = print_score_table(messages, threshold)
    if args.show_raw:
        print_raw_table(messages)

    filter_stats = summaries.get("objectness_score")
    verdict, verdict_notes = render_overall_verdict(
        expected=args.expected,
        actual_accept_rate=actual_accept_rate,
        virtual_pass_rate=virtual_pass_rate,
        filter_stats=filter_stats,
        threshold=threshold,
        hard_reject_rate=hard_reject_rate,
    )

    print("\n[종합 평가]")
    print(f"- {verdict}")
    for note in verdict_notes:
        print(f"- {note}")

    notes = diagnostic_notes(messages, summaries, params)
    if notes:
        print("\n[추가 진단]")
        for note in notes:
            print(f"- {note}")

    print("\n[점수 해석 원칙]")
    print("- depth_score: 후보 거리·유효 depth·depth 안정성·돌출 정도의 품질")
    print("- quality_score: 해상도·선명도·노출·RGB/depth 동기화의 품질")
    print("- color_score: 등록된 목표 이미지와의 색상 분포 유사도")
    print("- shape_score: bbox 비율·fill ratio·edge density 기반의 거친 형상 적합도")
    print("- physical_size_score: CameraInfo와 depth로 추정한 실제 크기 적합도")
    print("- objectness_score: 사용 가능한 위 점수들의 가중 평균; 최종 물체 인식 확률은 아님")
    print("- 단일 파일만으로 최종 threshold를 확정하지 말고 positive와 negative 분포를 함께 비교하세요.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
