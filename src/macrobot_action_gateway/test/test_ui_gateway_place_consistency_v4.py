from __future__ import annotations

import ast
from pathlib import Path

import yaml


EXPECTED_ENUM = {"ERASER": "Eraser", "RUBBER": "Rubber"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _object_enum(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "ObjectId":
            result: dict[str, str] = {}
            for child in node.body:
                if not isinstance(child, ast.Assign) or len(child.targets) != 1:
                    continue
                target = child.targets[0]
                if (
                    isinstance(target, ast.Name)
                    and isinstance(child.value, ast.Constant)
                    and isinstance(child.value.value, str)
                ):
                    result[target.id] = child.value.value
            return result
    raise AssertionError("ObjectId enum not found")


def _bundle_object_enum(bundle: dict[str, object]) -> tuple[dict[str, str], str]:
    candidates: list[tuple[str, object]] = []

    root_enums = bundle.get("enums")
    if isinstance(root_enums, dict):
        candidates.append(("enums.ObjectId", root_enums.get("ObjectId")))

    types = bundle.get("types")
    if isinstance(types, dict):
        nested_enums = types.get("enums")
        if isinstance(nested_enums, dict):
            candidates.append(
                ("types.enums.ObjectId", nested_enums.get("ObjectId"))
            )
        candidates.append(("types.ObjectId", types.get("ObjectId")))

    valid: list[tuple[dict[str, str], str]] = []
    for path, spec in candidates:
        if isinstance(spec, dict) and isinstance(spec.get("values"), dict):
            valid.append((dict(spec["values"]), path))

    assert len(valid) == 1, (
        "expected exactly one ObjectId mapping in enums.ObjectId, "
        "types.enums.ObjectId, or types.ObjectId; found "
        + ", ".join(path for _, path in valid)
    )
    return valid[0]

def test_only_eraser_and_rubber_are_public_objects() -> None:
    root = _repo_root()
    enum_values = _object_enum(
        root / "src/macrobot_action_gateway/macrobot_action_gateway/api_types.py"
    )
    catalog = yaml.safe_load(
        (root / "src/macrobot_action_gateway/config/object_catalog.yaml").read_text(
            encoding="utf-8"
        )
    )["objects"]
    bundle = yaml.safe_load(
        (root / "src/macrobot_ui/knowledge/llm_bundle.yaml").read_text(
            encoding="utf-8"
        )
    )
    bundle_objects = {
        item["id"]: item["enum_expression"].split(".")[-1]
        for item in bundle["object_catalog"]["objects"]
    }
    bundle_enum, bundle_enum_path = _bundle_object_enum(bundle)

    assert enum_values == EXPECTED_ENUM
    assert set(catalog) == set(EXPECTED_ENUM)
    assert bundle_enum_path in {"enums.ObjectId", "types.enums.ObjectId", "types.ObjectId"}
    assert bundle_enum == EXPECTED_ENUM
    assert bundle_objects == {"ERASER": "ERASER", "RUBBER": "RUBBER"}
    assert catalog["ERASER"]["grasp_keyframe_profile"] == "Eraser_r4"
    assert catalog["RUBBER"]["grasp_keyframe_profile"] == "Rubber_r4"


def test_ui_and_gateway_long_action_limits_match_latest_visible_test_command() -> None:
    root = _repo_root()
    gateway = yaml.safe_load(
        (root / "src/macrobot_action_gateway/config/gateway.yaml").read_text(
            encoding="utf-8"
        )
    )
    bundle = yaml.safe_load(
        (root / "src/macrobot_ui/knowledge/llm_bundle.yaml").read_text(
            encoding="utf-8"
        )
    )
    pick = yaml.safe_load(
        (root / "src/macrobot_pick_pipeline/config/stored_object_pick.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert gateway["alignment"]["hard_timeout_s"] == 2400.0
    assert gateway["manipulation"]["pick_hard_timeout_s"] == 2400.0
    assert gateway["manipulation"]["place_hard_timeout_s"] == 2400.0
    assert gateway["control_limits"]["max_wait_action_timeout_s"] == 2410.0
    assert (
        bundle["runtime_profile"]["manipulation"]["PICK_OBJECT"]["hard_timeout_s"]
        == 2400.0
    )
    assert (
        bundle["runtime_profile"]["manipulation"]["PLACE_NEXTTO_OBJECT"]
        ["hard_timeout_s"]
        == 2400.0
    )
    assert (
        bundle["functions"]["WAIT_ACTION"]["arguments"]["timeout_s"]["max"]
        == 2410.0
    )
    assert (
        pick["macrobot_stored_object_pick"]["ros__parameters"]
        ["record_timeout_sec"]
        == 240.0
    )
    assert (
        pick["macrobot_stored_object_pick"]["ros__parameters"]
        ["visible_test_timeout_sec"]
        == 2400.0
    )
    assert (
        pick["macrobot_visible_pick_test"]["ros__parameters"]
        ["default_timeout_sec"]
        == 2400.0
    )


def test_execution_safety_gates_remain_off_by_default() -> None:
    root = _repo_root()
    gateway = yaml.safe_load(
        (root / "src/macrobot_action_gateway/config/gateway.yaml").read_text(
            encoding="utf-8"
        )
    )
    backend = yaml.safe_load(
        (root / "src/macrobot_ui/config/backend.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert gateway["real_motion_enabled"] is False
    assert (
        backend["macrobot_ui_backend"]["ros__parameters"]["allow_execution"]
        is False
    )


def test_place_policy_is_implemented_but_sensor_unverified() -> None:
    root = _repo_root()
    gateway = yaml.safe_load(
        (root / "src/macrobot_action_gateway/config/gateway.yaml").read_text(
            encoding="utf-8"
        )
    )
    registry = yaml.safe_load(
        (root / "src/macrobot_action_gateway/config/api_registry.yaml").read_text(
            encoding="utf-8"
        )
    )
    policy = (
        "safe_preflight_and_command_completion_without_physical_release_sensor"
    )
    assert gateway["manipulation"]["placement_verification_policy"] == policy
    place = registry["functions"]["PLACE_NEXTTO_OBJECT"]
    assert place["verification"] == policy
    assert place["current_runtime_status"] == "implemented_hardware_verification_pending"
    assert place["requires_different_reference_object"] is True

def test_gateway_runtime_has_no_removed_object_fallback() -> None:
    root = _repo_root()
    source = (
        root
        / "src/macrobot_action_gateway/macrobot_action_gateway/gateway_runtime.py"
    ).read_text(encoding="utf-8")
    assert "ObjectId.BUDS3" not in source
    assert "ObjectId.CUP" not in source
    assert "requested = next(iter(ObjectId)) if object_id is None else object_id" in source
    assert '"spec_version": "0.3.0"' in source

