import cv2
import numpy as np

from depth_candidate_proposal.crop_core import (
    CropEncodingConfig,
    PixelRoi,
    encode_jpeg_bounded,
    extract_crop,
    map_and_pad_roi,
)


def test_map_and_pad_roi_same_resolution_and_clamp():
    roi = map_and_pad_roi(
        roi_x=2,
        roi_y=3,
        roi_width=20,
        roi_height=10,
        proposal_width=100,
        proposal_height=80,
        color_width=100,
        color_height=80,
        extra_padding_px=5,
    )
    assert roi == PixelRoi(x=0, y=0, width=27, height=18)


def test_map_roi_between_different_resolutions():
    roi = map_and_pad_roi(
        roi_x=160,
        roi_y=120,
        roi_width=160,
        roi_height=120,
        proposal_width=640,
        proposal_height=480,
        color_width=1280,
        color_height=960,
    )
    assert roi == PixelRoi(x=320, y=240, width=320, height=240)


def test_extract_crop_returns_copy():
    image = np.zeros((40, 60, 3), dtype=np.uint8)
    image[10:20, 15:30] = 255
    crop = extract_crop(image, PixelRoi(x=15, y=10, width=15, height=10))
    assert crop.shape == (10, 15, 3)
    crop[:] = 0
    assert np.all(image[10:20, 15:30] == 255)


def test_bounded_jpeg_encoding_reduces_noisy_image():
    rng = np.random.default_rng(7)
    image = rng.integers(0, 256, size=(480, 640, 3), dtype=np.uint8)
    config = CropEncodingConfig(
        jpeg_quality=80,
        min_jpeg_quality=30,
        jpeg_quality_step=10,
        max_jpeg_bytes=25_000,
        max_crop_side_px=320,
        min_crop_side_px=32,
        resize_factor=0.75,
        max_resize_iterations=6,
    )
    encoded = encode_jpeg_bounded(image, config)
    assert encoded.size_limit_met
    assert len(encoded.data) <= 25_000
    decoded = cv2.imdecode(np.frombuffer(encoded.data, np.uint8), cv2.IMREAD_COLOR)
    assert decoded is not None
    assert decoded.shape[1] == encoded.width
    assert decoded.shape[0] == encoded.height
