"""Routines that can be integrated into a main control flow."""

from importlib import resources

from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import RunningMode
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarkerOptions,
)

from models.pose_detection.landmarking import AnnotatedImage, display_landmarking
from models.pose_detection.trackers import DebugPostureTracker

POSE_LANDMARKER_FILE = resources.files("models.resources").joinpath(
    "pose_landmarker_lite.task"
)


def create_debug_posture_tracker() -> DebugPostureTracker:
    """Handles config of livestreamed input and model loading.

    Returns:
        Tracker object which acts as context manager.
    """
    annotated_image = AnnotatedImage()
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=POSE_LANDMARKER_FILE),
        running_mode=RunningMode.LIVE_STREAM,
        result_callback=lambda result, output_image, timestamp: display_landmarking(
            result, output_image, timestamp, annotated_image
        ),
    )

    tracker = DebugPostureTracker.create_from_options(options)
    tracker.annotated_image = annotated_image
    return tracker
