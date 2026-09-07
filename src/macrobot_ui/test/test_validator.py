from pathlib import Path

from macrobot_ui.code_validator import GeneratedCodeValidator


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = GeneratedCodeValidator(ROOT / "knowledge" / "llm_bundle.yaml")


def test_valid_minimal_program():
    report = VALIDATOR.validate(
        """def main() -> TaskOutcome:
    return TaskOutcome(status=TaskStatus.SUCCEEDED)
"""
    )
    assert report.is_valid, [item.display() for item in report.issues]


def test_import_is_rejected():
    report = VALIDATOR.validate(
        """import os

def main() -> TaskOutcome:
    return TaskOutcome(status=TaskStatus.SUCCEEDED)
"""
    )
    assert not report.is_valid
