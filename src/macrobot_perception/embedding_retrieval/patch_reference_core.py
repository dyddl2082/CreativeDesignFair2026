"""Reference patch prototype banks for DINOv2 localization.

Global CLS descriptors answer whether a crop resembles the registered object.
Patch prototypes are built separately from salient DINO patch tokens in curated
reference images, so query patch tokens are compared with the same token type
rather than only with global image descriptors.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
from typing import Mapping, Optional

import numpy as np

from .embedding_core import l2_normalize_rows


PATCH_CACHE_FORMAT_VERSION = 1
PATCH_PREPROCESSING_VERSION = "macrobot-dinov2-patch-prototypes-v1"


@dataclass(frozen=True)
class PatchPrototypeBank:
    kind: str
    target_object: str
    embeddings: np.ndarray
    signature: str
    cache_path: str
    cache_hit: bool
    source_image_count: int = 0
    skipped_images: int = 0

    @property
    def available(self) -> bool:
        return self.embeddings.ndim == 2 and self.embeddings.shape[0] > 0

    @property
    def count(self) -> int:
        return int(self.embeddings.shape[0]) if self.embeddings.ndim == 2 else 0

    @property
    def dimension(self) -> int:
        return int(self.embeddings.shape[1]) if self.available else 0


def salient_patch_rows(
    patch_embeddings: np.ndarray,
    global_embedding: np.ndarray,
    *,
    selection_quantile: float = 0.65,
    max_patches: int = 32,
) -> np.ndarray:
    """Select semantically salient normalized patch tokens from one image.

    The reference image is already curated around the target or a negative
    example. Similarity to that image's global descriptor suppresses neutral
    square padding and weak background patches. Selection is deterministic.
    """

    patches = np.asarray(patch_embeddings, dtype=np.float32)
    if patches.ndim == 3:
        patches = patches.reshape(-1, patches.shape[-1])
    if patches.ndim != 2 or patches.shape[0] == 0:
        raise ValueError("patch_embeddings must contain at least one patch")
    patches = l2_normalize_rows(patches)
    global_row = l2_normalize_rows(np.asarray(global_embedding, dtype=np.float32))[0]
    if patches.shape[1] != global_row.shape[0]:
        raise ValueError("global and patch embedding dimensions do not match")
    scores = patches @ global_row
    quantile = float(np.clip(selection_quantile, 0.0, 1.0))
    threshold = float(np.quantile(scores, quantile))
    indices = np.flatnonzero(scores >= threshold)
    if indices.size == 0:
        indices = np.asarray([int(np.argmax(scores))], dtype=np.int64)
    # Keep the strongest patches per image to bound first-run build time and
    # prevent one reference from dominating the prototype bank.
    ordering = indices[np.argsort(-scores[indices], kind="stable")]
    if max_patches > 0:
        ordering = ordering[: int(max_patches)]
    return patches[ordering]


def diverse_prototypes(
    embeddings: np.ndarray,
    *,
    max_count: int,
) -> np.ndarray:
    """Deterministic cosine farthest-point compression.

    The first prototype is closest to the bank mean. Each following prototype
    is the token least similar to the already selected set. This preserves
    multiple registered views without an optional sklearn dependency.
    """

    rows = l2_normalize_rows(embeddings)
    if rows.shape[0] == 0:
        return rows
    limit = max(1, int(max_count))
    if rows.shape[0] <= limit:
        return rows
    mean = l2_normalize_rows(np.mean(rows, axis=0))[0]
    first = int(np.argmax(rows @ mean))
    selected = [first]
    best_similarity = rows @ rows[first]
    best_similarity[first] = 1.0
    while len(selected) < limit:
        index = int(np.argmin(best_similarity))
        selected.append(index)
        best_similarity = np.maximum(best_similarity, rows @ rows[index])
        best_similarity[np.asarray(selected, dtype=np.int64)] = 1.0
    return rows[np.asarray(selected, dtype=np.int64)]


def save_patch_bank(path: str | Path, bank: PatchPrototypeBank, metadata: Mapping[str, object]) -> None:
    destination = Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(metadata)
    payload["cache_format_version"] = PATCH_CACHE_FORMAT_VERSION
    payload["prototype_count"] = bank.count
    payload["embedding_dim"] = bank.dimension
    with tempfile.NamedTemporaryFile(
        "wb", dir=str(destination.parent), prefix=destination.name + ".", suffix=".tmp", delete=False
    ) as stream:
        np.savez_compressed(
            stream,
            embeddings=np.asarray(bank.embeddings, dtype=np.float32),
            metadata=np.asarray(json.dumps(payload, sort_keys=True, ensure_ascii=False)),
        )
        temporary = Path(stream.name)
    os.replace(temporary, destination)


def load_patch_bank(
    path: str | Path,
    expected_metadata: Mapping[str, object],
    *,
    kind: str,
    target_object: str,
    signature: str,
    source_image_count: int,
) -> Optional[PatchPrototypeBank]:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        return None
    try:
        with np.load(source, allow_pickle=False) as archive:
            embeddings = np.asarray(archive["embeddings"], dtype=np.float32)
            metadata = json.loads(str(archive["metadata"].item()))
        expected = dict(expected_metadata)
        for key, value in expected.items():
            if metadata.get(key) != value:
                return None
        if int(metadata.get("cache_format_version", -1)) != PATCH_CACHE_FORMAT_VERSION:
            return None
        if embeddings.ndim != 2 or embeddings.shape[0] == 0:
            return None
        return PatchPrototypeBank(
            kind=kind,
            target_object=target_object,
            embeddings=l2_normalize_rows(embeddings),
            signature=signature,
            cache_path=str(source),
            cache_hit=True,
            source_image_count=source_image_count,
            skipped_images=0,
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return None
