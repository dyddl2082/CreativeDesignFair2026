"""ROS 2 node for DINOv2 multi-view retrieval and negative-margin scoring."""

from __future__ import annotations

from collections import Counter, deque
from pathlib import Path
import json
import queue
import threading
import time
from typing import Optional, Sequence

import cv2
from macrobot_interfaces.msg import (
    EmbeddingMatchedCandidate,
    EmbeddingRetrievalResult,
    FilteredCandidateCrop,
)
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String
from std_srvs.srv import Trigger

from .dinov2_backend import DependencyError, Dinov2Encoder
from .embedding_core import (
    CACHE_FORMAT_VERSION,
    PREPROCESSING_VERSION,
    CacheMetadata,
    ReferenceBank,
    cache_path_for_bank,
    compute_file_signature,
    decode_compressed_image,
    decode_compressed_mask,
    discover_images,
    load_reference_cache,
    pad_to_square,
    prepare_masked_image,
    render_target_path,
    save_reference_cache,
    summarize_retrieval,
)
from .patch_localization_core import (
    PatchLocalization,
    localize_patch_tokens,
    source_to_color_coordinates,
)
from .patch_reference_core import (
    PATCH_PREPROCESSING_VERSION,
    PatchPrototypeBank,
    diverse_prototypes,
    load_patch_bank,
    salient_patch_rows,
    save_patch_bank,
)


class EmbeddingRetrievalNode(Node):
    """Compare filtered crops with positive and negative DINOv2 view banks."""

    def __init__(self) -> None:
        super().__init__("embedding_retrieval")
        self._declare_parameters()
        self._validate_parameters()

        self._target_object = str(self.get_parameter("target_object").value).strip()
        self._state_lock = threading.RLock()
        self._model_lock = threading.Lock()
        self._reload_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._pending: queue.Queue[Optional[FilteredCandidateCrop]] = queue.Queue(
            maxsize=max(int(self.get_parameter("max_pending_messages").value), 1)
        )

        self._received = 0
        self._processed = 0
        self._accepted = 0
        self._rejected = 0
        self._decode_failures = 0
        self._dropped_queue = 0
        self._bank_reload_count = 0
        self._reject_reasons: Counter[str] = Counter()
        self._last_result = "not_started"
        self._last_debug_monotonic = 0.0
        self._recent_inference_ms: deque[float] = deque(maxlen=100)
        self._recent_total_ms: deque[float] = deque(maxlen=100)

        model_id = str(self.get_parameter("model_id").value)
        device = str(self.get_parameter("device").value)
        pooling = str(self.get_parameter("pooling").value)
        self.get_logger().info(
            f"Loading embedding model '{model_id}' on device='{device}', pooling='{pooling}'"
        )
        try:
            self._encoder = Dinov2Encoder(
                model_id=model_id,
                device=device,
                pooling=pooling,
                use_amp=bool(self.get_parameter("use_amp").value),
                model_cache_dir=str(self.get_parameter("model_cache_dir").value),
                local_files_only=bool(self.get_parameter("local_files_only").value),
            )
        except (DependencyError, RuntimeError, ValueError, OSError) as error:
            self.get_logger().fatal(f"Embedding model initialization failed: {error}")
            raise

        self._positive_bank = self._empty_bank("positive", self._target_object)
        self._negative_bank = self._empty_bank("negative", self._target_object)
        self._positive_patch_bank = self._empty_patch_bank("positive", self._target_object)
        self._negative_patch_bank = self._empty_patch_bank("negative", self._target_object)
        self._reload_banks(force=False, log_result=True)

        input_qos = QoSProfile(depth=4)
        input_qos.reliability = ReliabilityPolicy.BEST_EFFORT
        result_qos = QoSProfile(depth=20)
        result_qos.reliability = ReliabilityPolicy.RELIABLE
        matched_qos = QoSProfile(depth=2)
        matched_qos.reliability = (
            ReliabilityPolicy.RELIABLE
            if bool(self.get_parameter("reliable_matched_output").value)
            else ReliabilityPolicy.BEST_EFFORT
        )
        debug_qos = QoSProfile(depth=1)
        debug_qos.reliability = ReliabilityPolicy.BEST_EFFORT
        status_qos = QoSProfile(depth=1)
        status_qos.reliability = ReliabilityPolicy.RELIABLE

        input_topic = str(self.get_parameter("input_topic").value)
        result_topic = str(self.get_parameter("result_topic").value)
        matched_topic = str(self.get_parameter("matched_topic").value)
        debug_topic = str(self.get_parameter("debug_topic").value)
        status_topic = str(self.get_parameter("status_topic").value)
        target_topic = str(self.get_parameter("target_topic").value)

        self._result_publisher = self.create_publisher(
            EmbeddingRetrievalResult, result_topic, result_qos
        )
        self._matched_publisher = self.create_publisher(
            EmbeddingMatchedCandidate, matched_topic, matched_qos
        )
        self._debug_publisher = self.create_publisher(
            CompressedImage, debug_topic, debug_qos
        )
        self._status_publisher = self.create_publisher(String, status_topic, status_qos)
        self._input_subscription = self.create_subscription(
            FilteredCandidateCrop, input_topic, self._input_callback, input_qos
        )
        self._target_subscription = self.create_subscription(
            String, target_topic, self._target_callback, result_qos
        )
        self._reload_service = self.create_service(
            Trigger,
            str(self.get_parameter("reload_service").value),
            self._reload_service_callback,
        )
        self._rebuild_service = self.create_service(
            Trigger,
            str(self.get_parameter("rebuild_service").value),
            self._rebuild_service_callback,
        )
        status_period = max(float(self.get_parameter("status_period_sec").value), 0.5)
        self._status_timer = self.create_timer(status_period, self._publish_status)

        self._worker = threading.Thread(
            target=self._worker_loop,
            name="embedding_retrieval_worker",
            daemon=True,
        )
        self._worker.start()

        self.get_logger().info(
            "Embedding retrieval ready: "
            f"input='{input_topic}', results='{result_topic}', matched='{matched_topic}', "
            f"target='{self._target_object}', device='{self._encoder.device}', "
            f"positive={self._positive_bank.count}, negative={self._negative_bank.count}, "
            f"positive_patch_prototypes={self._positive_patch_bank.count}, "
            f"negative_patch_prototypes={self._negative_patch_bank.count}, "
            f"thresholds_enforced={bool(self.get_parameter('enforce_thresholds').value)}"
        )

    def _declare_parameters(self) -> None:
        defaults = {
            "input_topic": "/candidate_filter/accepted_crops",
            "result_topic": "/embedding_retrieval/results",
            "matched_topic": "/embedding_retrieval/matched_crops",
            "debug_topic": "/embedding_retrieval/debug/compressed",
            "status_topic": "/embedding_retrieval/status",
            "target_topic": "/embedding_retrieval/target",
            "reload_service": "/embedding_retrieval/reload_banks",
            "rebuild_service": "/embedding_retrieval/rebuild_banks",
            "target_object": "Buds3",
            "model_id": "facebook/dinov2-small",
            "device": "auto",
            "pooling": "cls",
            "use_amp": True,
            "model_cache_dir": "~/.cache/huggingface",
            "local_files_only": False,
            "positive_root_template": "~/MacRobot/data/curated/objects/{target}",
            "negative_roots": [
                "~/MacRobot/data/negative/confusers/{target}",
                "~/MacRobot/data/negative/library",
                "~/MacRobot/data/negative/backgrounds",
            ],
            "embedding_cache_dir": "~/MacRobot/data/embeddings",
            "use_embedding_cache": True,
            "max_positive_images": 128,
            "max_negative_images": 512,
            "reference_batch_size": 8,
            "positive_top_k": 3,
            "negative_top_k": 1,
            "use_foreground_mask": True,
            "mask_background_mode": "foreground_mean",
            "mask_dilate_px": 3,
            "mask_feather_px": 3,
            "mask_neutral_value": 127,
            "square_padding_ratio": 0.06,
            "square_padding_mode": "mean",
            "square_padding_neutral_value": 127,
            "enforce_thresholds": True,
            "min_positive_similarity": 0.45,
            "min_margin": 0.05,
            "require_negative_bank_for_accept": True,
            # Patch-token localization. This refines the object centre inside a
            # large/contaminated candidate crop without sending full RGB/depth.
            "enable_patch_localization": True,
            # Build same-token reference prototype banks for patch heatmaps.
            "use_patch_reference_bank": True,
            "use_patch_reference_cache": True,
            "max_positive_patch_reference_images": 32,
            "max_negative_patch_reference_images": 64,
            "reference_patch_selection_quantile": 0.65,
            "reference_patch_max_per_image": 32,
            "positive_patch_prototype_count": 192,
            "negative_patch_prototype_count": 256,
            "patch_localization_min_global_similarity": 0.0,
            "patch_localization_selection_quantile": 0.80,
            "patch_localization_min_patch_margin": -0.10,
            "patch_localization_min_component_patches": 2,
            "patch_localization_max_component_area_ratio": 0.70,
            "patch_localization_negative_weight": 1.0,
            "patch_localization_foreground_prior_weight": 0.12,
            "patch_localization_min_quality": 0.15,
            "publish_matched_crops": True,
            "reliable_matched_output": False,
            "max_pending_messages": 8,
            "publish_debug": True,
            "debug_mode": "all",
            "debug_hz": 2.0,
            "debug_jpeg_quality": 78,
            "status_period_sec": 3.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _validate_parameters(self) -> None:
        pooling = str(self.get_parameter("pooling").value).strip().lower()
        if pooling not in {"cls", "mean_patch", "cls_mean"}:
            raise ValueError("pooling must be one of: cls, mean_patch, cls_mean")
        mask_mode = str(self.get_parameter("mask_background_mode").value).strip().lower()
        if mask_mode not in {"none", "black", "neutral", "foreground_mean", "blur"}:
            raise ValueError("Invalid mask_background_mode")
        padding_mode = str(self.get_parameter("square_padding_mode").value).strip().lower()
        if padding_mode not in {"mean", "neutral", "reflect", "replicate"}:
            raise ValueError("Invalid square_padding_mode")
        debug_mode = str(self.get_parameter("debug_mode").value).strip().lower()
        if debug_mode not in {"all", "accepted", "rejected"}:
            raise ValueError("debug_mode must be all, accepted, or rejected")
        for name in ("positive_top_k", "negative_top_k", "reference_batch_size"):
            if int(self.get_parameter(name).value) <= 0:
                raise ValueError(f"{name} must be positive")
        quantile = float(self.get_parameter("patch_localization_selection_quantile").value)
        if not 0.0 <= quantile <= 1.0:
            raise ValueError("patch_localization_selection_quantile must be in [0, 1]")
        quality = float(self.get_parameter("patch_localization_min_quality").value)
        if not 0.0 <= quality <= 1.0:
            raise ValueError("patch_localization_min_quality must be in [0, 1]")
        reference_quantile = float(
            self.get_parameter("reference_patch_selection_quantile").value
        )
        if not 0.0 <= reference_quantile <= 1.0:
            raise ValueError("reference_patch_selection_quantile must be in [0, 1]")
        for name in (
            "max_positive_patch_reference_images",
            "max_negative_patch_reference_images",
            "reference_patch_max_per_image",
            "positive_patch_prototype_count",
            "negative_patch_prototype_count",
        ):
            if int(self.get_parameter(name).value) <= 0:
                raise ValueError(f"{name} must be positive")

    def _empty_bank(self, kind: str, target: str) -> ReferenceBank:
        return ReferenceBank(
            kind=kind,
            target_object=target,
            paths=(),
            embeddings=np.empty((0, max(self._encoder.embedding_dim, 0)), dtype=np.float32)
            if hasattr(self, "_encoder")
            else np.empty((0, 0), dtype=np.float32),
            signature="",
            cache_path="",
            cache_hit=False,
            skipped_images=0,
        )

    def _empty_patch_bank(self, kind: str, target: str) -> PatchPrototypeBank:
        dimension = max(self._encoder.embedding_dim, 0) if hasattr(self, "_encoder") else 0
        return PatchPrototypeBank(
            kind=kind,
            target_object=target,
            embeddings=np.empty((0, dimension), dtype=np.float32),
            signature="",
            cache_path="",
            cache_hit=False,
            source_image_count=0,
            skipped_images=0,
        )

    def _patch_preprocessing_key(self) -> str:
        return "|".join(
            [
                PATCH_PREPROCESSING_VERSION,
                self._preprocessing_key(),
                f"patch_size={int(self._encoder.patch_size)}",
                f"quantile={float(self.get_parameter('reference_patch_selection_quantile').value):.5f}",
                f"max_per_image={int(self.get_parameter('reference_patch_max_per_image').value)}",
            ]
        )

    def _load_or_build_patch_bank(
        self,
        *,
        kind: str,
        target: str,
        roots: Sequence[Path],
        max_images: int,
        max_prototypes: int,
        force: bool,
    ) -> PatchPrototypeBank:
        if not bool(self.get_parameter("use_patch_reference_bank").value):
            return self._empty_patch_bank(kind, target)
        paths = discover_images(roots, max_images=max_images)
        signature = compute_file_signature(paths) if paths else "empty"
        cache_root = render_target_path(
            str(self.get_parameter("embedding_cache_dir").value), target
        )
        cache_path = cache_path_for_bank(
            cache_root,
            target_object=target,
            kind=f"{kind}_patch_prototypes",
            model_id=self._encoder.model_id,
            pooling=self._encoder.pooling,
        )
        metadata = {
            "model_id": self._encoder.model_id,
            "pooling": self._encoder.pooling,
            "preprocessing_version": self._patch_preprocessing_key(),
            "signature": signature,
            "target_object": target,
            "kind": kind,
            "max_images": int(max_images),
            "max_prototypes": int(max_prototypes),
        }
        if (
            not force
            and bool(self.get_parameter("use_patch_reference_cache").value)
            and paths
        ):
            cached = load_patch_bank(
                cache_path,
                metadata,
                kind=kind,
                target_object=target,
                signature=signature,
                source_image_count=len(paths),
            )
            if cached is not None:
                return cached
        if not paths:
            bank = self._empty_patch_bank(kind, target)
            return PatchPrototypeBank(
                kind=bank.kind, target_object=bank.target_object, embeddings=bank.embeddings,
                signature=signature, cache_path=str(cache_path), cache_hit=False,
                source_image_count=0, skipped_images=0,
            )

        selected_rows: list[np.ndarray] = []
        skipped = 0
        valid_images = 0
        for path in paths:
            image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if image is None or image.size == 0:
                skipped += 1
                continue
            try:
                prepared = self._prepare_reference(image)
                with self._model_lock:
                    output = self._encoder.encode_bgr_with_patches(prepared)
                selected_rows.append(
                    salient_patch_rows(
                        output.patch_embeddings,
                        output.global_embedding,
                        selection_quantile=float(
                            self.get_parameter("reference_patch_selection_quantile").value
                        ),
                        max_patches=int(
                            self.get_parameter("reference_patch_max_per_image").value
                        ),
                    )
                )
                valid_images += 1
            except (ValueError, RuntimeError, cv2.error):
                skipped += 1
        if not selected_rows:
            bank = self._empty_patch_bank(kind, target)
            return PatchPrototypeBank(
                kind=bank.kind, target_object=bank.target_object, embeddings=bank.embeddings,
                signature=signature, cache_path=str(cache_path), cache_hit=False,
                source_image_count=0, skipped_images=skipped,
            )
        prototypes = diverse_prototypes(
            np.concatenate(selected_rows, axis=0),
            max_count=int(max_prototypes),
        )
        bank = PatchPrototypeBank(
            kind=kind,
            target_object=target,
            embeddings=prototypes,
            signature=signature,
            cache_path=str(cache_path),
            cache_hit=False,
            source_image_count=valid_images,
            skipped_images=skipped,
        )
        if bool(self.get_parameter("use_patch_reference_cache").value):
            try:
                save_patch_bank(cache_path, bank, metadata)
            except OSError as error:
                self.get_logger().warning(f"Could not save {kind} patch cache: {error}")
        return bank

    def _preprocessing_key(self) -> str:
        return "|".join(
            [
                PREPROCESSING_VERSION,
                f"square_ratio={float(self.get_parameter('square_padding_ratio').value):.5f}",
                f"square_mode={str(self.get_parameter('square_padding_mode').value)}",
            ]
        )

    def _positive_roots(self, target: str) -> list[Path]:
        template = str(self.get_parameter("positive_root_template").value)
        return [render_target_path(template, target)]

    def _negative_roots(self, target: str) -> list[Path]:
        values = self.get_parameter("negative_roots").value
        return [render_target_path(str(item), target) for item in values]

    def _prepare_reference(self, image_bgr: np.ndarray) -> np.ndarray:
        return pad_to_square(
            image_bgr,
            padding_ratio=float(self.get_parameter("square_padding_ratio").value),
            mode=str(self.get_parameter("square_padding_mode").value),
            neutral_value=int(self.get_parameter("square_padding_neutral_value").value),
        )

    def _load_or_build_bank(
        self,
        *,
        kind: str,
        target: str,
        roots: Sequence[Path],
        max_images: int,
        force: bool,
    ) -> ReferenceBank:
        paths = discover_images(roots, max_images=max_images)
        signature = compute_file_signature(paths) if paths else "empty"
        cache_root = render_target_path(
            str(self.get_parameter("embedding_cache_dir").value), target
        )
        cache_path = cache_path_for_bank(
            cache_root,
            target_object=target,
            kind=kind,
            model_id=self._encoder.model_id,
            pooling=self._encoder.pooling,
        )
        expected = CacheMetadata(
            model_id=self._encoder.model_id,
            pooling=self._encoder.pooling,
            preprocessing_version=self._preprocessing_key(),
            signature=signature,
            target_object=target,
            kind=kind,
            embedding_dim=self._encoder.embedding_dim,
        )
        if (
            not force
            and bool(self.get_parameter("use_embedding_cache").value)
            and paths
        ):
            cached = load_reference_cache(cache_path, expected)
            if cached is not None:
                return cached

        if not paths:
            return ReferenceBank(
                kind=kind,
                target_object=target,
                paths=(),
                embeddings=np.empty(
                    (0, max(self._encoder.embedding_dim, 0)), dtype=np.float32
                ),
                signature=signature,
                cache_path=str(cache_path),
                cache_hit=False,
                skipped_images=0,
            )

        images: list[np.ndarray] = []
        valid_paths: list[str] = []
        skipped = 0
        for path in paths:
            image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if image is None or image.size == 0:
                skipped += 1
                continue
            try:
                images.append(self._prepare_reference(image))
                valid_paths.append(str(path))
            except (ValueError, cv2.error):
                skipped += 1

        if not images:
            return ReferenceBank(
                kind=kind,
                target_object=target,
                paths=(),
                embeddings=np.empty(
                    (0, max(self._encoder.embedding_dim, 0)), dtype=np.float32
                ),
                signature=signature,
                cache_path=str(cache_path),
                cache_hit=False,
                skipped_images=skipped,
            )

        with self._model_lock:
            embeddings = self._encoder.encode_bgr(
                images,
                batch_size=int(self.get_parameter("reference_batch_size").value),
            )
        bank = ReferenceBank(
            kind=kind,
            target_object=target,
            paths=tuple(valid_paths),
            embeddings=embeddings,
            signature=signature,
            cache_path=str(cache_path),
            cache_hit=False,
            skipped_images=skipped,
        )
        if bool(self.get_parameter("use_embedding_cache").value):
            metadata = CacheMetadata(
                model_id=self._encoder.model_id,
                pooling=self._encoder.pooling,
                preprocessing_version=self._preprocessing_key(),
                signature=signature,
                target_object=target,
                kind=kind,
                embedding_dim=bank.dimension,
            )
            try:
                save_reference_cache(cache_path, bank, metadata)
            except OSError as error:
                self.get_logger().warning(f"Could not save {kind} cache: {error}")
        return bank

    def _reload_banks(self, *, force: bool, log_result: bool) -> bool:
        if not self._reload_lock.acquire(blocking=False):
            if log_result:
                self.get_logger().warning("A reference-bank reload is already running")
            return False
        try:
            target = self._target_object
            started = time.perf_counter()
            positive = self._load_or_build_bank(
                kind="positive",
                target=target,
                roots=self._positive_roots(target),
                max_images=int(self.get_parameter("max_positive_images").value),
                force=force,
            )
            negative = self._load_or_build_bank(
                kind="negative",
                target=target,
                roots=self._negative_roots(target),
                max_images=int(self.get_parameter("max_negative_images").value),
                force=force,
            )
            positive_patches = self._load_or_build_patch_bank(
                kind="positive",
                target=target,
                roots=self._positive_roots(target),
                max_images=int(
                    self.get_parameter("max_positive_patch_reference_images").value
                ),
                max_prototypes=int(
                    self.get_parameter("positive_patch_prototype_count").value
                ),
                force=force,
            )
            negative_patches = self._load_or_build_patch_bank(
                kind="negative",
                target=target,
                roots=self._negative_roots(target),
                max_images=int(
                    self.get_parameter("max_negative_patch_reference_images").value
                ),
                max_prototypes=int(
                    self.get_parameter("negative_patch_prototype_count").value
                ),
                force=force,
            )
            with self._state_lock:
                self._positive_bank = positive
                self._negative_bank = negative
                self._positive_patch_bank = positive_patches
                self._negative_patch_bank = negative_patches
                self._bank_reload_count += 1
            elapsed = (time.perf_counter() - started) * 1000.0
            if log_result:
                self.get_logger().info(
                    "Reference banks ready: "
                    f"target='{target}', positive={positive.count} "
                    f"(cache={positive.cache_hit}, skipped={positive.skipped_images}), "
                    f"negative={negative.count} "
                    f"(cache={negative.cache_hit}, skipped={negative.skipped_images}), "
                    f"positive_patch_prototypes={positive_patches.count} "
                    f"(cache={positive_patches.cache_hit}), "
                    f"negative_patch_prototypes={negative_patches.count} "
                    f"(cache={negative_patches.cache_hit}), "
                    f"elapsed={elapsed:.1f} ms"
                )
                if not positive.available:
                    self.get_logger().error(
                        f"No positive reference images found for target '{target}'"
                    )
                if not negative.available:
                    self.get_logger().warning(
                        f"No negative references found for target '{target}'. "
                        "Negative-margin decisions will be unavailable."
                    )
            return positive.available
        finally:
            self._reload_lock.release()

    def _drain_pending(self) -> None:
        while True:
            try:
                self._pending.get_nowait()
                self._pending.task_done()
            except queue.Empty:
                return

    def _target_callback(self, message: String) -> None:
        target = message.data.strip()
        if not target:
            self.get_logger().warning("Ignoring an empty embedding target")
            return
        if target in {".", ".."} or "/" in target or "\\" in target:
            self.get_logger().warning(f"Ignoring unsafe target name: '{target}'")
            return
        with self._state_lock:
            if target == self._target_object:
                return
            self._target_object = target
        self._drain_pending()
        threading.Thread(
            target=lambda: self._reload_banks(force=False, log_result=True),
            name="embedding_bank_reload",
            daemon=True,
        ).start()

    def _reload_service_callback(
        self, request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        del request
        success = self._reload_banks(force=False, log_result=True)
        response.success = success
        response.message = self._bank_summary_text()
        return response

    def _rebuild_service_callback(
        self, request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        del request
        success = self._reload_banks(force=True, log_result=True)
        response.success = success
        response.message = self._bank_summary_text()
        return response

    def _bank_summary_text(self) -> str:
        with self._state_lock:
            return (
                f"target={self._target_object}, positive={self._positive_bank.count}, "
                f"negative={self._negative_bank.count}, "
                f"positive_patch_prototypes={self._positive_patch_bank.count}, "
                f"negative_patch_prototypes={self._negative_patch_bank.count}, "
                f"model={self._encoder.model_id}"
            )

    def _input_callback(self, message: FilteredCandidateCrop) -> None:
        with self._state_lock:
            self._received += 1
        try:
            self._pending.put_nowait(message)
        except queue.Full:
            try:
                self._pending.get_nowait()
                self._pending.task_done()
            except queue.Empty:
                pass
            with self._state_lock:
                self._dropped_queue += 1
            try:
                self._pending.put_nowait(message)
            except queue.Full:
                with self._state_lock:
                    self._dropped_queue += 1

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                message = self._pending.get(timeout=0.2)
            except queue.Empty:
                continue
            if message is None:
                self._pending.task_done()
                break
            try:
                self._process_message(message)
            except Exception as error:  # Keep the worker alive after one bad crop.
                self.get_logger().error(
                    f"Unexpected embedding retrieval error: {type(error).__name__}: {error}"
                )
            finally:
                self._pending.task_done()

    @staticmethod
    def _optional_float(obj: object, name: str, fallback: float = -1.0) -> float:
        try:
            return float(getattr(obj, name))
        except (AttributeError, TypeError, ValueError):
            return float(fallback)

    def _decode_optional_mask(self, crop: object) -> Optional[np.ndarray]:
        if not bool(self.get_parameter("use_foreground_mask").value):
            return None
        try:
            available = bool(getattr(crop, "foreground_mask_available"))
            compressed = getattr(crop, "foreground_mask")
            data = compressed.data
        except AttributeError:
            return None
        if not available or not data:
            return None
        return decode_compressed_mask(data)

    def _process_message(self, message: FilteredCandidateCrop) -> None:
        total_started = time.perf_counter()
        crop_message = message.crop
        filter_result = message.result

        preprocess_started = time.perf_counter()
        try:
            image_bgr = decode_compressed_image(crop_message.image.data)
            mask = self._decode_optional_mask(crop_message)
            masked_bgr, mask_used = prepare_masked_image(
                image_bgr,
                mask,
                mode=str(self.get_parameter("mask_background_mode").value),
                dilate_px=int(self.get_parameter("mask_dilate_px").value),
                feather_px=int(self.get_parameter("mask_feather_px").value),
                neutral_value=int(self.get_parameter("mask_neutral_value").value),
            )
            prepared_bgr = pad_to_square(
                masked_bgr,
                padding_ratio=float(self.get_parameter("square_padding_ratio").value),
                mode=str(self.get_parameter("square_padding_mode").value),
                neutral_value=int(
                    self.get_parameter("square_padding_neutral_value").value
                ),
            )
        except (ValueError, cv2.error) as error:
            with self._state_lock:
                self._decode_failures += 1
                self._processed += 1
                self._rejected += 1
                self._reject_reasons["decode_or_preprocess_failed"] += 1
                self._last_result = f"reject decode_or_preprocess_failed: {error}"
            result = self._failure_result(
                message,
                reject_reason="decode_or_preprocess_failed",
                preprocessing_ms=(time.perf_counter() - preprocess_started) * 1000.0,
            )
            self._result_publisher.publish(result)
            return
        preprocessing_ms = (time.perf_counter() - preprocess_started) * 1000.0

        inference_started = time.perf_counter()
        patch_output = None
        with self._model_lock:
            if bool(self.get_parameter("enable_patch_localization").value):
                patch_output = self._encoder.encode_bgr_with_patches(prepared_bgr)
                query_embedding = patch_output.global_embedding
            else:
                query_embedding = self._encoder.encode_bgr([prepared_bgr], batch_size=1)[0]
        inference_ms = (time.perf_counter() - inference_started) * 1000.0

        with self._state_lock:
            positive_bank = self._positive_bank
            negative_bank = self._negative_bank
            positive_patch_bank = self._positive_patch_bank
            negative_patch_bank = self._negative_patch_bank
            target_object = self._target_object

        matching_started = time.perf_counter()
        summary = summarize_retrieval(
            query_embedding=query_embedding,
            positive_bank=positive_bank,
            negative_bank=negative_bank,
            positive_top_k=int(self.get_parameter("positive_top_k").value),
            negative_top_k=int(self.get_parameter("negative_top_k").value),
        )
        matching_ms = (time.perf_counter() - matching_started) * 1000.0

        localization_started = time.perf_counter()
        localization = PatchLocalization(False, reason="disabled_or_not_eligible")
        if (
            patch_output is not None
            and positive_bank.available
            and summary.positive.mean_score
            >= float(self.get_parameter("patch_localization_min_global_similarity").value)
        ):
            localization = localize_patch_tokens(
                patch_embeddings=patch_output.patch_embeddings,
                positive_embeddings=(
                    positive_patch_bank.embeddings
                    if positive_patch_bank.available
                    else positive_bank.embeddings
                ),
                negative_embeddings=(
                    negative_patch_bank.embeddings
                    if negative_patch_bank.available
                    else (negative_bank.embeddings if negative_bank.available else None)
                ),
                source_width=int(image_bgr.shape[1]),
                source_height=int(image_bgr.shape[0]),
                square_padding_ratio=float(
                    self.get_parameter("square_padding_ratio").value
                ),
                foreground_mask_source=mask,
                selection_quantile=float(
                    self.get_parameter("patch_localization_selection_quantile").value
                ),
                minimum_patch_margin=float(
                    self.get_parameter("patch_localization_min_patch_margin").value
                ),
                minimum_component_patches=int(
                    self.get_parameter("patch_localization_min_component_patches").value
                ),
                maximum_component_area_ratio=float(
                    self.get_parameter("patch_localization_max_component_area_ratio").value
                ),
                negative_weight=float(
                    self.get_parameter("patch_localization_negative_weight").value
                ),
                foreground_prior_weight=float(
                    self.get_parameter("patch_localization_foreground_prior_weight").value
                ),
            )
            if localization.available:
                localization = source_to_color_coordinates(
                    localization,
                    source_width=int(image_bgr.shape[1]),
                    source_height=int(image_bgr.shape[0]),
                    crop_x=int(crop_message.crop_roi.x_offset),
                    crop_y=int(crop_message.crop_roi.y_offset),
                    crop_width=int(crop_message.crop_roi.width),
                    crop_height=int(crop_message.crop_roi.height),
                )
                if localization.quality < float(
                    self.get_parameter("patch_localization_min_quality").value
                ):
                    localization = PatchLocalization(
                        False,
                        reason="patch_localization_quality_below_threshold",
                    )
        localization_ms = (time.perf_counter() - localization_started) * 1000.0

        positive_score = summary.positive.mean_score
        negative_score = summary.negative.mean_score
        passed_positive = (
            summary.positive.available
            and positive_score
            >= float(self.get_parameter("min_positive_similarity").value)
        )
        require_negative = bool(
            self.get_parameter("require_negative_bank_for_accept").value
        )
        if summary.negative.available:
            passed_margin = summary.margin >= float(self.get_parameter("min_margin").value)
        else:
            passed_margin = not require_negative

        enforce = bool(self.get_parameter("enforce_thresholds").value)
        if not summary.positive.available:
            accepted = False
            reject_reason = "positive_bank_unavailable"
        elif enforce and not passed_positive:
            accepted = False
            reject_reason = "positive_similarity_below_threshold"
        elif enforce and not passed_margin:
            accepted = False
            reject_reason = (
                "negative_bank_unavailable"
                if not summary.negative.available and require_negative
                else "negative_margin_below_threshold"
            )
        else:
            # Observation mode is pass-through so scores can be collected safely.
            accepted = True
            reject_reason = ""

        result = self._build_result(
            message=message,
            target_object=target_object,
            positive_bank=positive_bank,
            negative_bank=negative_bank,
            summary=summary,
            mask_used=mask_used,
            passed_positive=passed_positive,
            passed_margin=passed_margin,
            accepted=accepted,
            reject_reason=reject_reason,
            preprocessing_ms=preprocessing_ms,
            inference_ms=inference_ms,
            matching_ms=matching_ms,
            localization=localization,
            localization_ms=localization_ms,
        )
        self._result_publisher.publish(result)

        if accepted and bool(self.get_parameter("publish_matched_crops").value):
            forwarded = EmbeddingMatchedCandidate()
            forwarded.result = result
            forwarded.filtered_crop = message
            self._matched_publisher.publish(forwarded)

        self._publish_debug_if_due(image_bgr, result)

        total_ms = (time.perf_counter() - total_started) * 1000.0
        with self._state_lock:
            self._processed += 1
            self._recent_inference_ms.append(inference_ms)
            self._recent_total_ms.append(total_ms)
            if accepted:
                self._accepted += 1
                self._last_result = (
                    f"accept id={result.candidate_id} pos={result.positive_similarity:.3f} "
                    f"neg={result.negative_similarity:.3f} margin={result.margin:.3f}"
                )
            else:
                self._rejected += 1
                self._reject_reasons[reject_reason] += 1
                self._last_result = (
                    f"reject id={result.candidate_id} reason={reject_reason} "
                    f"pos={result.positive_similarity:.3f} margin={result.margin:.3f}"
                )

    def _base_result(self, message: FilteredCandidateCrop) -> EmbeddingRetrievalResult:
        result = EmbeddingRetrievalResult()
        result.proposal_header = message.crop.proposal_header
        result.image_header = message.crop.image.header
        result.candidate_id = int(message.crop.candidate.id)
        result.crop_index = int(message.crop.crop_index)
        result.frame_crop_count = int(message.crop.frame_crop_count)
        result.model_id = self._encoder.model_id
        result.pooling = self._encoder.pooling
        result.device = str(self._encoder.device)
        result.embedding_dim = int(self._encoder.embedding_dim)
        result.objectness_score = self._optional_float(
            message.result,
            "objectness_score",
            self._optional_float(message.result, "filter_score", -1.0),
        )
        result.target_hint_score = self._optional_float(
            message.result, "target_hint_score", -1.0
        )
        result.candidate = message.crop.candidate
        result.crop_roi = message.crop.crop_roi
        return result

    def _failure_result(
        self,
        message: FilteredCandidateCrop,
        *,
        reject_reason: str,
        preprocessing_ms: float,
    ) -> EmbeddingRetrievalResult:
        result = self._base_result(message)
        with self._state_lock:
            result.target_object = self._target_object
            result.positive_bank_available = self._positive_bank.available
            result.positive_reference_count = self._positive_bank.count
            result.negative_bank_available = self._negative_bank.available
            result.negative_reference_count = self._negative_bank.count
        result.foreground_mask_used = False
        result.positive_similarity = -1.0
        result.best_positive_similarity = -1.0
        result.negative_similarity = -1.0
        result.best_negative_similarity = -1.0
        result.margin = -1.0
        result.thresholds_enforced = bool(
            self.get_parameter("enforce_thresholds").value
        )
        result.passed_positive_threshold = False
        result.passed_margin_threshold = False
        result.accepted = False
        result.reject_reason = reject_reason
        result.preprocessing_ms = float(preprocessing_ms)
        result.inference_ms = 0.0
        result.matching_ms = 0.0
        result.localization_ms = 0.0
        self._assign_localization(result, PatchLocalization(False, reason=reject_reason))
        return result

    @staticmethod
    def _assign_localization(
        result: EmbeddingRetrievalResult,
        localization: PatchLocalization,
    ) -> None:
        result.localization_available = bool(localization.available)
        result.localization_method = str(localization.method if localization.available else "")
        result.localization_quality = float(localization.quality if localization.available else 0.0)
        result.localization_peak_positive = float(
            localization.peak_positive if localization.available else -1.0
        )
        result.localization_peak_margin = float(
            localization.peak_margin if localization.available else -1.0
        )
        result.localized_center_x = float(
            localization.center_x_source if localization.available else -1.0
        )
        result.localized_center_y = float(
            localization.center_y_source if localization.available else -1.0
        )
        if localization.available and int(result.crop_roi.width) > 0 and int(result.crop_roi.height) > 0:
            result.localized_center_x_crop = float(
                localization.center_x_source - float(result.crop_roi.x_offset)
            )
            result.localized_center_y_crop = float(
                localization.center_y_source - float(result.crop_roi.y_offset)
            )
        else:
            result.localized_center_x_crop = -1.0
            result.localized_center_y_crop = -1.0
        roi = result.localized_roi
        if localization.available:
            roi.x_offset = max(0, int(round(localization.bbox_x_source)))
            roi.y_offset = max(0, int(round(localization.bbox_y_source)))
            roi.width = max(1, int(round(localization.bbox_width_source)))
            roi.height = max(1, int(round(localization.bbox_height_source)))
            roi.do_rectify = False
        else:
            roi.x_offset = 0
            roi.y_offset = 0
            roi.width = 0
            roi.height = 0
            roi.do_rectify = False
        result.localization_mask_area_px = int(
            localization.mask_area_source_px if localization.available else 0
        )
        result.orientation_deg = float(
            localization.orientation_deg if localization.available else 0.0
        )
        result.orientation_class = str(
            localization.orientation_class if localization.available else "unknown"
        )
        result.orientation_quality = float(
            localization.orientation_quality if localization.available else 0.0
        )

    def _build_result(
        self,
        *,
        message: FilteredCandidateCrop,
        target_object: str,
        positive_bank: ReferenceBank,
        negative_bank: ReferenceBank,
        summary: object,
        mask_used: bool,
        passed_positive: bool,
        passed_margin: bool,
        accepted: bool,
        reject_reason: str,
        preprocessing_ms: float,
        inference_ms: float,
        matching_ms: float,
        localization: PatchLocalization,
        localization_ms: float,
    ) -> EmbeddingRetrievalResult:
        result = self._base_result(message)
        result.target_object = target_object
        result.positive_bank_available = positive_bank.available
        result.positive_reference_count = positive_bank.count
        result.negative_bank_available = negative_bank.available
        result.negative_reference_count = negative_bank.count
        result.foreground_mask_used = bool(mask_used)
        result.positive_similarity = float(summary.positive.mean_score)
        result.best_positive_similarity = float(summary.positive.best_score)
        result.negative_similarity = float(summary.negative.mean_score)
        result.best_negative_similarity = float(summary.negative.best_score)
        result.margin = float(summary.margin)
        result.best_positive_path = summary.positive.best_path
        result.best_negative_path = summary.negative.best_path
        result.top_positive_paths = list(summary.positive.paths)
        result.top_positive_scores = [float(item) for item in summary.positive.scores]
        result.top_negative_paths = list(summary.negative.paths)
        result.top_negative_scores = [float(item) for item in summary.negative.scores]
        result.thresholds_enforced = bool(
            self.get_parameter("enforce_thresholds").value
        )
        result.passed_positive_threshold = bool(passed_positive)
        result.passed_margin_threshold = bool(passed_margin)
        result.accepted = bool(accepted)
        result.reject_reason = reject_reason
        self._assign_localization(result, localization)
        result.preprocessing_ms = float(preprocessing_ms)
        result.inference_ms = float(inference_ms)
        result.matching_ms = float(matching_ms)
        result.localization_ms = float(localization_ms)
        return result

    def _publish_debug_if_due(
        self, image_bgr: np.ndarray, result: EmbeddingRetrievalResult
    ) -> None:
        if not bool(self.get_parameter("publish_debug").value):
            return
        mode = str(self.get_parameter("debug_mode").value).strip().lower()
        if mode == "accepted" and not result.accepted:
            return
        if mode == "rejected" and result.accepted:
            return
        now = time.monotonic()
        debug_hz = max(float(self.get_parameter("debug_hz").value), 0.01)
        if now - self._last_debug_monotonic < 1.0 / debug_hz:
            return
        self._last_debug_monotonic = now

        preview = image_bgr.copy()
        border_color = (0, 200, 0) if result.accepted else (0, 0, 220)
        cv2.rectangle(
            preview,
            (0, 0),
            (max(preview.shape[1] - 1, 0), max(preview.shape[0] - 1, 0)),
            border_color,
            3,
        )
        if result.localization_available:
            crop_x = int(result.crop_roi.x_offset)
            crop_y = int(result.crop_roi.y_offset)
            x0 = int(result.localized_roi.x_offset) - crop_x
            y0 = int(result.localized_roi.y_offset) - crop_y
            x1 = x0 + int(result.localized_roi.width)
            y1 = y0 + int(result.localized_roi.height)
            x0 = int(np.clip(x0, 0, max(preview.shape[1] - 1, 0)))
            y0 = int(np.clip(y0, 0, max(preview.shape[0] - 1, 0)))
            x1 = int(np.clip(x1, x0 + 1, max(preview.shape[1], x0 + 1)))
            y1 = int(np.clip(y1, y0 + 1, max(preview.shape[0], y0 + 1)))
            center = (
                int(np.clip(round(result.localized_center_x_crop), 0, max(preview.shape[1] - 1, 0))),
                int(np.clip(round(result.localized_center_y_crop), 0, max(preview.shape[0] - 1, 0))),
            )
            cv2.rectangle(preview, (x0, y0), (x1 - 1, y1 - 1), (0, 220, 255), 2)
            cv2.drawMarker(
                preview,
                center,
                (255, 255, 0),
                markerType=cv2.MARKER_CROSS,
                markerSize=18,
                thickness=2,
            )
            if result.orientation_quality > 0.0:
                angle_rad = math.radians(float(result.orientation_deg))
                half_length = max(12, int(round(0.25 * max(x1 - x0, y1 - y0))))
                dx = int(round(math.cos(angle_rad) * half_length))
                dy = int(round(math.sin(angle_rad) * half_length))
                cv2.line(
                    preview,
                    (center[0] - dx, center[1] - dy),
                    (center[0] + dx, center[1] + dy),
                    (255, 0, 255),
                    2,
                    cv2.LINE_AA,
                )
        decision = "PASS" if result.accepted else "REJECT"
        margin_text = f"{result.margin:.3f}" if result.margin >= -0.5 else "n/a"
        negative_text = (
            f"{result.negative_similarity:.3f}"
            if result.negative_similarity >= -0.5
            else "n/a"
        )
        lines = [
            f"{decision} id={result.candidate_id} target={result.target_object}",
            f"pos={result.positive_similarity:.3f} neg={negative_text} margin={margin_text}",
            f"best+={Path(result.best_positive_path).name or 'n/a'}",
            f"best-={Path(result.best_negative_path).name or 'n/a'}",
            f"infer={result.inference_ms:.1f}ms mask={int(result.foreground_mask_used)} loc={int(result.localization_available)} q={result.localization_quality:.2f}",
        ]
        if result.reject_reason:
            lines.append(result.reject_reason)
        y = 22
        for line in lines:
            cv2.putText(
                preview,
                line,
                (7, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (0, 0, 0),
                3,
                cv2.LINE_AA,
            )
            cv2.putText(
                preview,
                line,
                (7, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
            y += 20
        quality = int(np.clip(self.get_parameter("debug_jpeg_quality").value, 25, 95))
        success, encoded = cv2.imencode(
            ".jpg", preview, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        )
        if not success:
            return
        message = CompressedImage()
        message.header = result.image_header
        message.format = "jpeg"
        message.data = encoded.tobytes()
        self._debug_publisher.publish(message)

    def _publish_status(self) -> None:
        with self._state_lock:
            positive = self._positive_bank
            negative = self._negative_bank
            positive_patches = self._positive_patch_bank
            negative_patches = self._negative_patch_bank
            inference_mean = (
                float(np.mean(self._recent_inference_ms))
                if self._recent_inference_ms
                else 0.0
            )
            total_mean = (
                float(np.mean(self._recent_total_ms)) if self._recent_total_ms else 0.0
            )
            payload = {
                "target_object": self._target_object,
                "model_id": self._encoder.model_id,
                "pooling": self._encoder.pooling,
                "device": str(self._encoder.device),
                "device_name": str(getattr(self._encoder, "device_name", "")),
                "amp_enabled": bool(getattr(self._encoder, "use_amp", False)),
                "amp_dtype": (
                    str(getattr(self._encoder, "amp_dtype", ""))
                    if getattr(self._encoder, "amp_dtype", None) is not None
                    else ""
                ),
                "embedding_dim": int(self._encoder.embedding_dim),
                "positive_reference_count": positive.count,
                "positive_cache_hit": positive.cache_hit,
                "negative_reference_count": negative.count,
                "negative_cache_hit": negative.cache_hit,
                "positive_patch_prototype_count": positive_patches.count,
                "positive_patch_cache_hit": positive_patches.cache_hit,
                "negative_patch_prototype_count": negative_patches.count,
                "negative_patch_cache_hit": negative_patches.cache_hit,
                "received": self._received,
                "processed": self._processed,
                "accepted": self._accepted,
                "rejected": self._rejected,
                "decode_failures": self._decode_failures,
                "dropped_queue": self._dropped_queue,
                "queue_size": self._pending.qsize(),
                "bank_reload_count": self._bank_reload_count,
                "thresholds_enforced": bool(
                    self.get_parameter("enforce_thresholds").value
                ),
                "min_positive_similarity": float(
                    self.get_parameter("min_positive_similarity").value
                ),
                "min_margin": float(self.get_parameter("min_margin").value),
                "patch_localization_enabled": bool(
                    self.get_parameter("enable_patch_localization").value
                ),
                "patch_localization_min_quality": float(
                    self.get_parameter("patch_localization_min_quality").value
                ),
                "mean_inference_ms_last_100": inference_mean,
                "mean_total_ms_last_100": total_mean,
                "top_reject_reasons": self._reject_reasons.most_common(8),
                "last_result": self._last_result,
                "cache_format_version": CACHE_FORMAT_VERSION,
                "patch_preprocessing_version": PATCH_PREPROCESSING_VERSION,
            }
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self._status_publisher.publish(message)

    def destroy_node(self) -> bool:
        self._stop_event.set()
        try:
            self._pending.put_nowait(None)
        except queue.Full:
            try:
                self._pending.get_nowait()
                self._pending.task_done()
                self._pending.put_nowait(None)
            except queue.Empty:
                pass
        if hasattr(self, "_worker") and self._worker.is_alive():
            self._worker.join(timeout=3.0)
        return super().destroy_node()


def main(args: Optional[Sequence[str]] = None) -> None:
    rclpy.init(args=args)
    node: Optional[EmbeddingRetrievalNode] = None
    try:
        node = EmbeddingRetrievalNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
