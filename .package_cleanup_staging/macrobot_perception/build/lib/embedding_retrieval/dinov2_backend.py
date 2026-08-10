"""Lazy Hugging Face DINOv2 encoder used by the ROS node."""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np

from .embedding_core import l2_normalize_rows


class DependencyError(RuntimeError):
    """Raised when optional ML dependencies are unavailable."""


class Dinov2Encoder:
    """Generate normalized global DINOv2 image descriptors."""

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
            pil_images = []
            for image_bgr in batch:
                if image_bgr is None or image_bgr.size == 0:
                    raise ValueError("Cannot encode an empty image")
                image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                pil_images.append(self._image_class.fromarray(image_rgb))

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
                hidden = model_output.last_hidden_state
                if self.pooling == "cls":
                    features = hidden[:, 0, :]
                elif self.pooling == "mean_patch":
                    features = hidden[:, 1:, :].mean(dim=1)
                else:
                    features = 0.5 * (
                        hidden[:, 0, :] + hidden[:, 1:, :].mean(dim=1)
                    )
                features = self._torch_functional.normalize(features, p=2, dim=-1)

            arrays = features.detach().float().cpu().numpy().astype(np.float32, copy=False)
            outputs.append(arrays)

        result = np.concatenate(outputs, axis=0)
        if self.embedding_dim <= 0 and result.ndim == 2:
            self.embedding_dim = int(result.shape[1])
        return l2_normalize_rows(result)
