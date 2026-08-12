"""Lazy Hugging Face DINOv2 encoder used by the ROS node."""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np

from .embedding_core import l2_normalize_rows


class DependencyError(RuntimeError):
    """Raised when optional ML dependencies are unavailable."""


@dataclass(frozen=True)
class Dinov2PatchOutput:
    global_embedding: np.ndarray
    patch_embeddings: np.ndarray
    processed_height: int
    processed_width: int
    patch_size: int


class Dinov2Encoder:
    """Generate normalized global and patch-level DINOv2 descriptors."""

    def __init__(
        self,
        *,
        model_id: str,
        device: str = "auto",
        pooling: str = "cls",
        use_amp: bool = True,
        model_cache_dir: str = "",
        local_files_only: bool = False,
    ) -> None:
        try:
            import torch
            import torch.nn.functional as torch_functional
            from PIL import Image
            from transformers import AutoImageProcessor, AutoModel
        except ImportError as error:
            raise DependencyError(
                "DINOv2 dependencies are missing. Install torch, transformers, "
                "safetensors, and Pillow in the Python environment used to build/run "
                "this ROS package."
            ) from error

        self._torch = torch
        self._torch_functional = torch_functional
        self._image_class = Image
        self.model_id = model_id
        self.pooling = pooling.strip().lower()
        if self.pooling not in {"cls", "mean_patch", "cls_mean"}:
            raise ValueError("pooling must be one of: cls, mean_patch, cls_mean")

        requested_device = device.strip().lower()
        xpu_available = bool(
            hasattr(torch, "xpu")
            and hasattr(torch.xpu, "is_available")
            and torch.xpu.is_available()
        )
        if requested_device == "auto":
            if xpu_available:
                requested_device = "xpu"
            elif torch.cuda.is_available():
                requested_device = "cuda"
            else:
                requested_device = "cpu"
        if requested_device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError(
                f"CUDA device '{requested_device}' was requested but torch.cuda.is_available() is false"
            )
        if requested_device.startswith("xpu") and not xpu_available:
            raise RuntimeError(
                f"XPU device '{requested_device}' was requested but torch.xpu.is_available() is false"
            )
        self.device = torch.device(requested_device)
        self.use_amp = bool(use_amp and self.device.type in {"cuda", "xpu"})
        self.amp_dtype = torch.float16 if self.use_amp else None
        if self.device.type == "xpu":
            index = 0 if self.device.index is None else self.device.index
            self.device_name = str(torch.xpu.get_device_name(index))
        elif self.device.type == "cuda":
            index = 0 if self.device.index is None else self.device.index
            self.device_name = str(torch.cuda.get_device_name(index))
        else:
            self.device_name = "CPU"

        cache_dir = str(Path(model_cache_dir).expanduser()) if model_cache_dir else None
        self.processor = AutoImageProcessor.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            local_files_only=bool(local_files_only),
        )
        self.model = AutoModel.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            local_files_only=bool(local_files_only),
        )
        self.model.eval()
        self.model.to(self.device)
        self.embedding_dim = int(getattr(self.model.config, "hidden_size", 0))
        patch_size = getattr(self.model.config, "patch_size", 14)
        if isinstance(patch_size, (tuple, list)):
            patch_size = patch_size[0]
        self.patch_size = int(patch_size)

    def _pil_images(self, images_bgr: Sequence[np.ndarray]):
        pil_images = []
        for image_bgr in images_bgr:
            if image_bgr is None or image_bgr.size == 0:
                raise ValueError("Cannot encode an empty image")
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            pil_images.append(self._image_class.fromarray(image_rgb))
        return pil_images

    def _pool_hidden(self, hidden):
        if self.pooling == "cls":
            features = hidden[:, 0, :]
        elif self.pooling == "mean_patch":
            features = hidden[:, 1:, :].mean(dim=1)
        else:
            features = 0.5 * (hidden[:, 0, :] + hidden[:, 1:, :].mean(dim=1))
        return self._torch_functional.normalize(features, p=2, dim=-1)

    def _model_forward(self, pil_images):
        inputs = self.processor(images=pil_images, return_tensors="pt")
        inputs = {
            key: value.to(self.device, non_blocking=True)
            for key, value in inputs.items()
        }
        autocast_context = (
            self._torch.autocast(
                device_type=self.device.type,
                dtype=self.amp_dtype,
            )
            if self.use_amp
            else nullcontext()
        )
        with self._torch.inference_mode(), autocast_context:
            model_output = self.model(**inputs)
        return inputs, model_output

    def encode_bgr(
        self,
        images_bgr: Sequence[np.ndarray],
        *,
        batch_size: int = 8,
    ) -> np.ndarray:
        """Encode BGR OpenCV images into normalized float32 descriptors."""

        if not images_bgr:
            dimension = max(self.embedding_dim, 0)
            return np.empty((0, dimension), dtype=np.float32)
        batch_size = max(int(batch_size), 1)
        outputs: list[np.ndarray] = []

        for start in range(0, len(images_bgr), batch_size):
            batch = images_bgr[start : start + batch_size]
            inputs, model_output = self._model_forward(self._pil_images(batch))
            del inputs
            features = self._pool_hidden(model_output.last_hidden_state)
            arrays = features.detach().float().cpu().numpy().astype(np.float32, copy=False)
            outputs.append(arrays)

        result = np.concatenate(outputs, axis=0)
        if self.embedding_dim <= 0 and result.ndim == 2:
            self.embedding_dim = int(result.shape[1])
        return l2_normalize_rows(result)

    def encode_bgr_with_patches(self, image_bgr: np.ndarray) -> Dinov2PatchOutput:
        """Encode one image and return a normalized patch-token grid.

        The caller square-pads the source crop first.  The processor's normal
        center crop therefore maps consistently back into the square source.
        """

        inputs, model_output = self._model_forward(self._pil_images([image_bgr]))
        hidden = model_output.last_hidden_state
        global_feature = self._pool_hidden(hidden)[0]
        pixel_values = inputs.get("pixel_values")
        if pixel_values is None or pixel_values.ndim != 4:
            raise RuntimeError("DINOv2 processor did not return pixel_values")
        processed_height = int(pixel_values.shape[-2])
        processed_width = int(pixel_values.shape[-1])
        grid_height = max(processed_height // self.patch_size, 1)
        grid_width = max(processed_width // self.patch_size, 1)
        expected_patches = grid_height * grid_width
        tokens = hidden[:, 1:, :]
        token_count = int(tokens.shape[1])
        if token_count < expected_patches:
            # Fallback for unusual processors/models: infer a rectangular grid.
            side = int(round(token_count ** 0.5))
            if side * side != token_count:
                raise RuntimeError(
                    f"Cannot infer DINOv2 patch grid: tokens={token_count}, expected={expected_patches}"
                )
            grid_height = side
            grid_width = side
            expected_patches = token_count
        elif token_count > expected_patches:
            # Some variants insert register tokens after CLS. The image patches
            # remain the final expected_patches tokens in Hugging Face models.
            tokens = tokens[:, -expected_patches:, :]
        patch_features = self._torch_functional.normalize(tokens[0], p=2, dim=-1)
        patches = (
            patch_features.detach()
            .float()
            .cpu()
            .numpy()
            .astype(np.float32, copy=False)
            .reshape(grid_height, grid_width, -1)
        )
        global_array = (
            global_feature.detach().float().cpu().numpy().astype(np.float32, copy=False)
        )
        if self.embedding_dim <= 0:
            self.embedding_dim = int(global_array.shape[0])
        return Dinov2PatchOutput(
            global_embedding=l2_normalize_rows(global_array)[0],
            patch_embeddings=patches,
            processed_height=processed_height,
            processed_width=processed_width,
            patch_size=self.patch_size,
        )
