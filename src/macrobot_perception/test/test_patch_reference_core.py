from pathlib import Path

import numpy as np

from embedding_retrieval.patch_reference_core import (
    PatchPrototypeBank,
    diverse_prototypes,
    load_patch_bank,
    salient_patch_rows,
    save_patch_bank,
)


def test_salient_patch_rows_selects_target_aligned_tokens():
    patches = np.asarray(
        [
            [[1.0, 0.0], [0.95, 0.05]],
            [[0.0, 1.0], [-1.0, 0.0]],
        ],
        dtype=np.float32,
    )
    selected = salient_patch_rows(
        patches,
        np.asarray([1.0, 0.0], dtype=np.float32),
        selection_quantile=0.5,
        max_patches=2,
    )
    assert selected.shape == (2, 2)
    assert np.all(selected[:, 0] > 0.9)


def test_diverse_prototypes_preserves_distinct_directions():
    rows = np.asarray(
        [
            [1.0, 0.0],
            [0.99, 0.01],
            [0.0, 1.0],
            [0.01, 0.99],
            [-1.0, 0.0],
        ],
        dtype=np.float32,
    )
    prototypes = diverse_prototypes(rows, max_count=3)
    assert prototypes.shape == (3, 2)
    # At least one prototype from each broad direction should remain.
    assert np.max(prototypes[:, 0]) > 0.9
    assert np.min(prototypes[:, 0]) < -0.9
    assert np.max(prototypes[:, 1]) > 0.9


def test_patch_bank_cache_round_trip(tmp_path: Path):
    path = tmp_path / "patches.npz"
    bank = PatchPrototypeBank(
        kind="positive",
        target_object="Eraser",
        embeddings=np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32),
        signature="abc",
        cache_path=str(path),
        cache_hit=False,
        source_image_count=2,
    )
    metadata = {
        "model_id": "test",
        "pooling": "cls",
        "preprocessing_version": "v1",
        "signature": "abc",
        "target_object": "Eraser",
        "kind": "positive",
        "max_images": 2,
        "max_prototypes": 2,
    }
    save_patch_bank(path, bank, metadata)
    loaded = load_patch_bank(
        path,
        metadata,
        kind="positive",
        target_object="Eraser",
        signature="abc",
        source_image_count=2,
    )
    assert loaded is not None
    assert loaded.cache_hit
    assert loaded.count == 2
    assert np.allclose(loaded.embeddings, bank.embeddings)
