"""Routines that can be integrated into a main control flow."""

from importlib import resources

import cv2
import mediapipe as mp
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import RunningMode
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarker,
    PoseLandmarkerOptions,
)

from models.pose_detection.landmarking import AnnotatedImage, display_landmarking

POSE_LANDMARKER_FILE = resources.files("models.resources").joinpath(
    "pose_landmarker_lite.task"
)


class DebugPostureTracker(PoseLandmarker):
    """Handles routines for a Debugging Posture Tracker"""

    def __init__(self, graph_config, running_mode, packet_callback) -> None:
        super().__init__(graph_config, running_mode, packet_callback)
        self.annotated_image = AnnotatedImage()
        self.video_capture = cv2.VideoCapture(0)

    def track_posture(self):
        """Get frame from video capture device and process with pose model, then posture algorithm.
        Print debugging info and display landmark annotated frame.
        """
        success, frame = self.video_capture.read()
        if not success:
            return

        frame_timestamp_ms = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        self.detect_async(mp_image, int(frame_timestamp_ms))

        cv2.imshow("input", frame)
        if self.annotated_image.data is not None:
            cv2.imshow("output", self.annotated_image.data)

    def __exit__(self, unused_exc_type, unused_exc_value, unused_traceback) -> None:
        self.video_capture.release()
        cv2.destroyAllWindows()
        super().__exit__(unused_exc_type, unused_exc_value, unused_traceback)


def create_debug_posture_tracker() -> DebugPostureTracker:
    """Handles config of livestreamed input and model loading.
    Returns:
        (DebugPostureTracker): Tracker object which acts as context manager.
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
