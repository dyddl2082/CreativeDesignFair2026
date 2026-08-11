"""Backward-compatible entry point for the camera-dependent teach node."""

from .camera_teach_node import CameraTeachNode, main

PickTeachNode = CameraTeachNode

__all__ = ["CameraTeachNode", "PickTeachNode", "main"]
