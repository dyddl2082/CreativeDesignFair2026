from pathlib import Path

from macrobot_camera_tf.calibration_schema import load_calibration


def test_schema_loads(tmp_path: Path):
    path = tmp_path / "camera.yaml"
    path.write_text(
        """schema_version: 1
metadata: {test: true}
transforms:
  - parent: camera_link
    child: camera_color_frame
    xyz: [0.0, 0.0, 0.0]
    quaternion_xyzw: [0.0, 0.0, 0.0, 2.0]
""",
        encoding="utf-8",
    )
    metadata, transforms = load_calibration(path)
    assert metadata["metadata"]["test"] is True
    assert transforms[0].quaternion_xyzw == (0.0, 0.0, 0.0, 1.0)


def test_transform_composition_with_yaw():
    import math
    from macrobot_camera_tf.calibration_schema import (
        TransformSpec,
        compose_transforms,
        quaternion_from_rpy,
    )

    anchor_to_color = TransformSpec(
        parent="camera_link",
        child="camera_color_frame",
        xyz=(0.0, 0.0, 0.0),
        quaternion_xyzw=quaternion_from_rpy(0.0, 0.0, math.pi / 2.0),
    )
    color_to_depth = TransformSpec(
        parent="camera_color_frame",
        child="camera_depth_frame",
        xyz=(1.0, 0.0, 0.0),
        quaternion_xyzw=(0.0, 0.0, 0.0, 1.0),
    )
    result = compose_transforms(
        anchor_to_color,
        color_to_depth,
        parent="camera_link",
        child="camera_depth_frame",
    )
    assert abs(result.xyz[0]) < 1e-9
    assert abs(result.xyz[1] - 1.0) < 1e-9
    assert abs(result.xyz[2]) < 1e-9
