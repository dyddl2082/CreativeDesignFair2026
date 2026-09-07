from macrobot_pick_pipeline.alignment_core import AlignmentProfile


def test_alignment_profile_round_trips_orientation_domain():
    profile = AlignmentProfile(
        name="Eraser",
        object_name="Eraser",
        pick_profile="Eraser",
        reference_point_base=(0.25, 0.06, 0.08),
        recorded_at="now",
    ).with_reference(
        (0.25, 0.06, 0.08),
        orientation_deg=20.0,
        orientation_class="diagonal",
        orientation_quality=0.8,
        orientation_source="depth_axis_3d",
        orientation_frame="base_link",
        orientation_semantics="axial_yaw",
        orientation_axis_base=(0.94, 0.342, 0.0),
        require_orientation_match=True,
    )
    mapping = profile.to_mapping()
    loaded = AlignmentProfile.from_mapping("Eraser", mapping)
    assert loaded.reference_orientation_source == "depth_axis_3d"
    assert loaded.reference_orientation_frame == "base_link"
    assert loaded.reference_orientation_semantics == "axial_yaw"
    assert loaded.reference_orientation_axis_base is not None
