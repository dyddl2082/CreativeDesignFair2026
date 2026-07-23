import numpy as np

from depth_candidate_proposal.proposal_core import (
    CameraIntrinsics,
    ProposalConfig,
    generate_depth_proposals,
)


def make_scene():
    height, width = 240, 320
    fx = fy = 280.0
    cx = width / 2.0
    cy = height / 2.0

    # A gently slanted background plane near 1.0 m.
    rows = np.arange(height, dtype=np.float32)[:, None]
    depth = 1.00 + 0.0005 * (rows - cy)
    depth = np.repeat(depth, width, axis=1).astype(np.float32)

    # Two foreground objects at different depths.
    depth[80:145, 65:125] = 0.72
    depth[105:175, 190:260] = 0.62

    intrinsics = CameraIntrinsics(width, height, fx, fy, cx, cy)
    return depth, intrinsics


def test_plane_removal_finds_two_foreground_components():
    depth, intrinsics = make_scene()
    config = ProposalConfig(
        min_depth_m=0.2,
        max_depth_m=1.4,
        plane_sample_stride=3,
        plane_ransac_iterations=80,
        plane_distance_threshold_m=0.01,
        plane_min_inlier_ratio=0.40,
        plane_clearance_m=0.04,
        min_component_area_px=250,
        close_kernel_px=5,
        open_kernel_px=3,
        max_candidates=8,
    )

    result = generate_depth_proposals(depth, intrinsics, config)

    assert result.plane is not None
    assert len(result.candidates) == 2
    medians = sorted(candidate.median_depth_m for candidate in result.candidates)
    assert np.allclose(medians, [0.62, 0.72], atol=0.02)


def test_percentile_fallback_works_without_camera_info():
    depth, _ = make_scene()
    config = ProposalConfig(
        min_depth_m=0.2,
        max_depth_m=1.4,
        enable_plane_removal=True,
        fallback_background_percentile=75.0,
        fallback_clearance_m=0.08,
        min_component_area_px=250,
        close_kernel_px=5,
        open_kernel_px=3,
        reject_border_components=True,
    )

    result = generate_depth_proposals(depth, None, config)

    assert result.plane is None
    assert len(result.candidates) == 2
