import numpy as np

from embedding_retrieval.patch_localization_core import (
    localize_patch_tokens,
    source_to_color_coordinates,
)


def test_patch_heatmap_localizes_target_cluster_and_maps_to_color():
    patches = np.zeros((4, 4, 3), dtype=np.float32)
    patches[:, :, 1] = 1.0  # negative-like background
    patches[1:3, 2:4, :] = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    positive = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
    negative = np.array([[0.0, 1.0, 0.0]], dtype=np.float32)

    result = localize_patch_tokens(
        patch_embeddings=patches,
        positive_embeddings=positive,
        negative_embeddings=negative,
        source_width=200,
        source_height=200,
        square_padding_ratio=0.0,
        selection_quantile=0.70,
        minimum_component_patches=2,
    )
    assert result.available
    assert result.quality > 0.5
    assert result.center_x_source > 100.0
    assert 50.0 < result.center_y_source < 150.0

    mapped = source_to_color_coordinates(
        result,
        source_width=200,
        source_height=200,
        crop_x=20,
        crop_y=30,
        crop_width=100,
        crop_height=100,
    )
    assert mapped.available
    assert 70.0 < mapped.center_x_source < 120.0
    assert 55.0 < mapped.center_y_source < 105.0
