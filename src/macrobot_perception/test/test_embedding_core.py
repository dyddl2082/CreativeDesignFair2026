from pathlib import Path

import cv2
import numpy as np

from embedding_retrieval.embedding_core import (
    CacheMetadata,
    MatchList,
    ReferenceBank,
    cache_path_for_bank,
    l2_normalize_rows,
    load_reference_cache,
    pad_to_square,
    prepare_masked_image,
    save_reference_cache,
    summarize_retrieval,
)


def make_bank(kind: str, embeddings: np.ndarray) -> ReferenceBank:
    normalized = l2_normalize_rows(embeddings)
    return ReferenceBank(
        kind=kind,
        target_object="Buds3",
        paths=tuple(f"{kind}_{index}.jpg" for index in range(len(normalized))),
        embeddings=normalized,
        signature="sig",
        cache_path="",
        cache_hit=False,
    )


def test_positive_and_negative_margin() -> None:
    positive = make_bank("positive", np.asarray([[1.0, 0.0], [0.9, 0.1]]))
    negative = make_bank("negative", np.asarray([[0.0, 1.0], [0.3, 0.7]]))
    summary = summarize_retrieval(
        np.asarray([1.0, 0.0]),
        positive,
        negative,
        positive_top_k=2,
        negative_top_k=1,
    )
    assert summary.positive.best_score > 0.99
    assert summary.negative.best_score < 0.5
    assert summary.margin > 0.5


def test_mask_background_replacement() -> None:
    image = np.full((40, 60, 3), (20, 40, 200), dtype=np.uint8)
    image[10:30, 20:40] = (240, 240, 240)
    mask = np.zeros((40, 60), dtype=np.uint8)
    mask[10:30, 20:40] = 255
    output, used = prepare_masked_image(
        image,
        mask,
        mode="foreground_mean",
        dilate_px=0,
        feather_px=0,
    )
    assert used
    assert np.all(output[20, 30] == (240, 240, 240))
    assert np.all(output[0, 0] == (240, 240, 240))


def test_square_padding() -> None:
    image = np.zeros((30, 50, 3), dtype=np.uint8)
    padded = pad_to_square(image, padding_ratio=0.1, mode="neutral")
    assert padded.shape[0] == padded.shape[1]
    assert padded.shape[0] > 50


def test_reference_cache_round_trip(tmp_path: Path) -> None:
    bank = make_bank("positive", np.asarray([[1.0, 0.0], [0.0, 1.0]]))
    cache_path = cache_path_for_bank(
        tmp_path,
        target_object="Buds3",
        kind="positive",
        model_id="facebook/dinov2-small",
        pooling="cls",
    )
    metadata = CacheMetadata(
        model_id="facebook/dinov2-small",
        pooling="cls",
        preprocessing_version="test",
        signature="sig",
        target_object="Buds3",
        kind="positive",
        embedding_dim=2,
    )
    save_reference_cache(cache_path, bank, metadata)
    loaded = load_reference_cache(cache_path, metadata)
    assert loaded is not None
    assert loaded.cache_hit
    assert loaded.paths == bank.paths
    np.testing.assert_allclose(loaded.embeddings, bank.embeddings, atol=1e-6)
