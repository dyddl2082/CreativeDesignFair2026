from pathlib import Path

from macrobot_arm_commissioning.safe_region_analysis import SafeRegionDataset


def test_representative_cases(tmp_path: Path):
    connected = tmp_path / "safe_connected_samples.csv"
    all_samples = tmp_path / "safe_samples.csv"
    header = (
        "q1_rad,q2_rad,q3_rad,lift_servo_deg,tilt_servo_deg,"
        "gripper_servo_deg,safe,connected,reason,contacts\n"
    )
    lines = [header]
    for q1 in (-0.2, -0.1, 0.0, 0.1, 0.2):
        for q2 in (-0.2, -0.1, 0.0, 0.1, 0.2):
            for q3 in (-0.4, -0.3, -0.2, -0.1, 0.0):
                lines.append(
                    f"{q1},{q2},{q3},90,90,90,1,1,safe,\n"
                )
    connected.write_text("".join(lines), encoding="utf-8")
    all_samples.write_text(
        "".join(lines)
        + "0.3,0.3,-0.4,90,90,90,0,0,collision,left|right\n",
        encoding="utf-8",
    )
    dataset = SafeRegionDataset(connected, all_samples)
    cases = dataset.representative_cases()
    names = {case["name"] for case in cases}
    assert "home" in names
    assert "q1_min_inside" in names
    assert "gripper_half" in names
    assert dataset.safe_close_q3() == -0.3


def test_grid_path(tmp_path: Path):
    connected = tmp_path / "safe_connected_samples.csv"
    header = (
        "q1_rad,q2_rad,q3_rad,lift_servo_deg,tilt_servo_deg,"
        "gripper_servo_deg,safe,connected,reason,contacts\n"
    )
    lines = [header]
    for q1 in (0.0, 0.1, 0.2):
        for q2 in (0.0, 0.1):
            for q3 in (-0.1, 0.0):
                lines.append(f"{q1},{q2},{q3},90,90,90,1,1,safe,\n")
    connected.write_text("".join(lines), encoding="utf-8")
    dataset = SafeRegionDataset(connected)
    path = dataset.grid_path((0.0, 0.0, 0.0), (0.2, 0.1, -0.1))
    assert path[0] == (0.0, 0.0, 0.0)
    assert path[-1] == (0.2, 0.1, -0.1)
    for a, b in zip(path[:-1], path[1:]):
        changed = sum(abs(a[i] - b[i]) > 1e-9 for i in range(3))
        assert changed == 1
