"""Pure helpers for MacRobot embedding retrieval and reference-bank caching."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import os
import re
from typing import Iterable, Optional, Sequence

import cv2
import numpy as np


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
CACHE_FORMAT_VERSION = 1
PREPROCESSING_VERSION = "macrobot-dinov2-v1"


@dataclass(frozen=True)
class ReferenceBank:
    """Normalized embeddings and their source files."""

    kind: str
    target_object: str
    paths: tuple[str, ...]
    embeddings: np.ndarray
    signature: str
    cache_path: str
    cache_hit: bool
    skipped_images: int = 0

    @property
    def available(self) -> bool:
        return bool(self.paths) and self.embeddings.ndim == 2 and self.embeddings.shape[0] > 0

    @property
    def count(self) -> int:
        return int(self.embeddings.shape[0]) if self.embeddings.ndim == 2 else 0

    @property
    def dimension(self) -> int:
        return int(self.embeddings.shape[1]) if self.available else 0


@dataclass(frozen=True)
class MatchList:
    """Descending top-k similarity matches."""

    paths: tuple[str, ...]
    scores: tuple[float, ...]

    @property
    def available(self) -> bool:
        return bool(self.scores)

    @property
    def best_score(self) -> float:
        return float(self.scores[0]) if self.scores else -1.0

    @property
    def mean_score(self) -> float:
        return float(np.mean(self.scores)) if self.scores else -1.0

    @property
    def best_path(self) -> str:
        return self.paths[0] if self.paths else ""


@dataclass(frozen=True)
class RetrievalSummary:
    positive: MatchList
    negative: MatchList
    margin: float


@dataclass(frozen=True)
class CacheMetadata:
    model_id: str
    pooling: str
    preprocessing_version: str
    signature: str
    target_object: str
    kind: str
    embedding_dim: int


def expand_path(path_text: str) -> Path:
    """Expand ~ and environment variables without requiring the path to exist."""

    return Path(os.path.expandvars(os.path.expanduser(path_text)))


def render_target_path(path_text: str, target_object: str) -> Path:
    """Expand a path template that may contain ``{target}``."""

    return expand_path(path_text.replace("{target}", target_object))


def safe_slug(text: str) -> str:
    """Create a filesystem-safe, deterministic name."""

    collapsed = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip())
    collapsed = collapsed.strip("._-") or "unnamed"
    return collapsed[:120]


def discover_images(
    roots: Iterable[Path],
    max_images: int = 0,
) -> list[Path]:
    """Recursively find usable image files in deterministic order."""

    found: dict[str, Path] = {}
    for root in roots:
        root = Path(root)
        if root.is_file():
            candidates = [root]
        elif root.is_dir():
            candidates = root.rglob("*")
        else:
            continue

        for path in candidates:
            if not path.is_file():
                continue
            lower_name = path.name.lower()
            if lower_name.startswith(".") or lower_name.endswith(".bak"):
                continue
            if "_depth." in lower_name or lower_name.endswith("_mask.png"):
                continue
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            resolved = str(path.resolve())
            found[resolved] = path.resolve()

    ordered = [found[key] for key in sorted(found)]
    if max_images > 0:
        ordered = ordered[:max_images]
    return ordered


def compute_file_signature(paths: Sequence[Path]) -> str:
    """Hash paths plus stat information so caches invalidate after edits."""

    digest = sha256()
    for path in paths:
        stat = path.stat()
        digest.update(str(path.resolve()).encode("utf-8", errors="surrogatepass"))
        digest.update(b"\0")
        digest.update(str(stat.st_size).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(stat.st_mtime_ns).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def l2_normalize_rows(vectors: np.ndarray, epsilon: float = 1e-12) -> np.ndarray:
    """Return float32 row-wise L2-normalized vectors."""

    array = np.asarray(vectors, dtype=np.float32)
    if array.ndim == 1:
        array = array.reshape(1, -1)
    if array.ndim != 2:
        raise ValueError(f"Expected a 2-D array, got shape {array.shape}")
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    norms = np.maximum(norms, epsilon)
    return (array / norms).astype(np.float32, copy=False)


def decode_compressed_image(data: bytes | bytearray | Sequence[int]) -> np.ndarray:
    """Decode a JPEG/PNG compressed color image to BGR."""

    encoded = np.frombuffer(bytes(data), dtype=np.uint8)
    if encoded.size == 0:
        raise ValueError("Compressed image data is empty")
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ValueError("OpenCV failed to decode the compressed image")
    return image


def decode_compressed_mask(data: bytes | bytearray | Sequence[int]) -> np.ndarray:
    """Decode a compressed mask and force it to binary mono8."""

    encoded = np.frombuffer(bytes(data), dtype=np.uint8)
    if encoded.size == 0:
        raise ValueError("Compressed mask data is empty")
    mask = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)
    if mask is None or mask.size == 0:
        raise ValueError("OpenCV failed to decode the foreground mask")
    return np.where(mask > 0, 255, 0).astype(np.uint8)


def prepare_masked_image(
    image_bgr: np.ndarray,
    mask_u8: Optional[np.ndarray],
    *,
    mode: str = "foreground_mean",
    dilate_px: int = 3,
    feather_px: int = 3,
    neutral_value: int = 127,
) -> tuple[np.ndarray, bool]:
    """Reduce candidate-background influence while preserving the object.

    Supported modes:
      - ``none``: ignore the mask.
      - ``black``: fill the background with black.
      - ``neutral``: fill with a fixed gray value.
      - ``foreground_mean``: fill with the mean foreground color.
      - ``blur``: fill with a heavily blurred version of the crop.
    """

    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Input image is empty")
    normalized_mode = mode.strip().lower()
    if mask_u8 is None or normalized_mode == "none":
        return image_bgr.copy(), False

    height, width = image_bgr.shape[:2]
    if mask_u8.shape != (height, width):
        mask_u8 = cv2.resize(
            mask_u8,
            (width, height),
            interpolation=cv2.INTER_NEAREST,
        )
    binary = np.where(mask_u8 > 0, 255, 0).astype(np.uint8)
    if np.count_nonzero(binary) < 4:
        return image_bgr.copy(), False

    if dilate_px > 0:
        kernel_size = max(1, int(dilate_px) * 2 + 1)
        binary = cv2.dilate(
            binary,
            np.ones((kernel_size, kernel_size), dtype=np.uint8),
            iterations=1,
        )

    if normalized_mode == "black":
        background = np.zeros_like(image_bgr)
    elif normalized_mode == "neutral":
        value = int(np.clip(neutral_value, 0, 255))
        background = np.full_like(image_bgr, value)
    elif normalized_mode == "foreground_mean":
        pixels = image_bgr[binary > 0]
        if pixels.size == 0:
            return image_bgr.copy(), False
        mean_color = np.mean(pixels, axis=0)
        background = np.empty_like(image_bgr)
        background[:] = np.clip(mean_color, 0, 255).astype(np.uint8)
    elif normalized_mode == "blur":
        sigma = max(float(max(height, width)) / 18.0, 3.0)
        background = cv2.GaussianBlur(image_bgr, (0, 0), sigmaX=sigma, sigmaY=sigma)
    else:
        raise ValueError(
            "mask_background_mode must be one of: none, black, neutral, "
            "foreground_mean, blur"
        )

    if feather_px > 0:
        sigma = max(float(feather_px), 0.5)
        alpha = cv2.GaussianBlur(binary, (0, 0), sigmaX=sigma, sigmaY=sigma)
    else:
        alpha = binary
    alpha_f = alpha.astype(np.float32)[:, :, None] / 255.0
    output = (
        image_bgr.astype(np.float32) * alpha_f
        + background.astype(np.float32) * (1.0 - alpha_f)
    )
    return np.clip(output, 0, 255).astype(np.uint8), True


def top_k_matches(
    query_embedding: np.ndarray,
    bank: ReferenceBank,
    top_k: int,
) -> MatchList:
    """Match one normalized query against a normalized bank."""

    if not bank.available:
        return MatchList(paths=(), scores=())
    query = l2_normalize_rows(query_embedding)[0]
    if query.shape[0] != bank.embeddings.shape[1]:
        raise ValueError(
            f"Embedding dimension mismatch: query={query.shape[0]}, "
            f"bank={bank.embeddings.shape[1]}"
        )
    similarities = bank.embeddings @ query
    count = min(max(int(top_k), 1), bank.count)
    indices = np.argpartition(-similarities, count - 1)[:count]
    indices = indices[np.argsort(-similarities[indices])]
    return MatchList(
        paths=tuple(bank.paths[int(index)] for index in indices),
        scores=tuple(float(similarities[int(index)]) for index in indices),
    )


def summarize_retrieval(
    query_embedding: np.ndarray,
    positive_bank: ReferenceBank,
    negative_bank: ReferenceBank,
    positive_top_k: int,
    negative_top_k: int,
) -> RetrievalSummary:
    """Compute positive similarity, hardest-negative similarity, and margin."""

    positive = top_k_matches(query_embedding, positive_bank, positive_top_k)
    negative = top_k_matches(query_embedding, negative_bank, negative_top_k)
    margin = (
        positive.mean_score - negative.mean_score
        if positive.available and negative.available
        else -1.0
    )
    return RetrievalSummary(positive=positive, negative=negative, margin=float(margin))


def cache_path_for_bank(
    cache_root: Path,
    *,
    target_object: str,
    kind: str,
    model_id: str,
    pooling: str,
) -> Path:
    """Return a deterministic NPZ cache path."""

    model_key = safe_slug(model_id.replace("/", "__"))
    target_key = safe_slug(target_object)
    return (
        cache_root
        / model_key
        / safe_slug(pooling)
        / target_key
        / f"{safe_slug(kind)}.npz"
    )


def save_reference_cache(
    path: Path,
    bank: ReferenceBank,
    metadata: CacheMetadata,
) -> None:
    """Atomically persist a reference bank without pickle objects."""

    path.parent.mkdir(parents=True, exist_ok=True)
    metadata_json = json.dumps(metadata.__dict__, sort_keys=True, ensure_ascii=False)
    max_length = max((len(item) for item in bank.paths), default=1)
    paths_array = np.asarray(bank.paths, dtype=f"<U{max_length}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as stream:
        np.savez_compressed(
            stream,
            embeddings=np.asarray(bank.embeddings, dtype=np.float32),
            paths=paths_array,
            metadata=np.asarray(metadata_json),
        )
    os.replace(temporary, path)


def load_reference_cache(
    path: Path,
    expected: CacheMetadata,
) -> Optional[ReferenceBank]:
    """Load a cache only when every compatibility field matches."""

    if not path.is_file():
        return None
    try:
        with np.load(path, allow_pickle=False) as archive:
            metadata_raw = archive["metadata"]
            metadata_text = str(metadata_raw.item())
            metadata = json.loads(metadata_text)
            expected_dict = expected.__dict__.copy()
            # Dimension is unknown before model inference only when caller passes 0.
            if expected_dict.get("embedding_dim", 0) == 0:
                expected_dict.pop("embedding_dim", None)
                metadata.pop("embedding_dim", None)
            if metadata != expected_dict:
                return None
            embeddings = l2_normalize_rows(archive["embeddings"])
            paths = tuple(str(item) for item in archive["paths"].tolist())
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return None
    if embeddings.shape[0] != len(paths):
        return None
    return ReferenceBank(
        kind=expected.kind,
        target_object=expected.target_object,
        paths=paths,
        embeddings=embeddings,
        signature=expected.signature,
        cache_path=str(path),
        cache_hit=True,
        skipped_images=0,
    )


def pad_to_square(
    image_bgr: np.ndarray,
    *,
    padding_ratio: float = 0.06,
    mode: str = "mean",
    neutral_value: int = 127,
) -> np.ndarray:
    """Pad an image to a square so model center-cropping does not cut the object."""

    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Input image is empty")
    height, width = image_bgr.shape[:2]
    extra = int(round(max(height, width) * max(float(padding_ratio), 0.0)))
    side = max(height, width) + 2 * extra
    top = (side - height) // 2
    bottom = side - height - top
    left = (side - width) // 2
    right = side - width - left
    normalized_mode = mode.strip().lower()

    if normalized_mode == "reflect":
        border_type = cv2.BORDER_REFLECT_101
        value = None
    elif normalized_mode == "replicate":
        border_type = cv2.BORDER_REPLICATE
        value = None
    elif normalized_mode == "neutral":
        border_type = cv2.BORDER_CONSTANT
        gray = int(np.clip(neutral_value, 0, 255))
        value = (gray, gray, gray)
    elif normalized_mode == "mean":
        border_type = cv2.BORDER_CONSTANT
        mean_color = np.mean(image_bgr.reshape(-1, 3), axis=0)
        value = tuple(float(item) for item in mean_color)
    else:
        raise ValueError("square_padding_mode must be one of: mean, neutral, reflect, replicate")

    if value is None:
        return cv2.copyMakeBorder(
            image_bgr,
            top,
            bottom,
            left,
            right,
            border_type,
        )
    return cv2.copyMakeBorder(
        image_bgr,
        top,
        bottom,
        left,
        right,
        border_type,
        value=value,
    )
