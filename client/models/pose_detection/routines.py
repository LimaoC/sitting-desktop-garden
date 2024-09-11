"""Routines that can be integrated into a main control flow."""

import logging
import multiprocessing as multp
from importlib import resources
from typing import Callable, Mapping

import cv2
import mediapipe as mp
from mediapipe.framework import calculator_pb2
from mediapipe.python._framework_bindings.packet import Packet
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import RunningMode
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode,
)
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarker,
    PoseLandmarkerOptions,
)

from models.pose_detection.landmarking import AnnotatedImage, display_landmarking

POSE_LANDMARKER_FILE = resources.files("models.resources").joinpath(
    "pose_landmarker_lite.task"
)

logger = logging.getLogger(__name__)


class DebugPostureProcess:
    def __init__(self) -> None:
        self._parent_con, child_con = multp.Pipe()
        self._process = multp.Process(target=_run_debug_posture, args=(child_con,))
        self._process.start()

        # Blocks until something is recieved from child
        self._parent_con.recv()

        logger.debug("Done loading model and communicated to parent.")

    def stop(self) -> None:
        self._parent_con.send(-2)


class DebugPostureTracker(PoseLandmarker):
    """Handles routines for a Debugging Posture Tracker.

    Attributes:
        annotated_image: Mutable container for an image which may be mutated asynchronously.
    """

    def __init__(
        self,
        graph_config: calculator_pb2.CalculatorGraphConfig,
        running_mode: VisionTaskRunningMode,
        packet_callback: Callable[[Mapping[str, Packet]], None],
    ) -> None:
        super().__init__(graph_config, running_mode, packet_callback)
        self.annotated_image = AnnotatedImage()
        self._video_capture = cv2.VideoCapture(0)

    def track_posture(self) -> None:
        """Get frame from video capture device and process with pose model, then posture
        algorithm. Print debugging info and display landmark annotated frame.
        """
        success, frame = self._video_capture.read()
        if not success:
            return

        frame_timestamp_ms = self._video_capture.get(cv2.CAP_PROP_POS_MSEC)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        self.detect_async(mp_image, int(frame_timestamp_ms))

        cv2.imshow("input", frame)
        if self.annotated_image.data is not None:
            cv2.imshow("output", self.annotated_image.data)

    def __exit__(self, unused_exc_type, unused_exc_value, unused_traceback) -> None:
        self._video_capture.release()
        cv2.destroyAllWindows()
        super().__exit__(unused_exc_type, unused_exc_value, unused_traceback)


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


def _run_debug_posture(con) -> None:
    with create_debug_posture_tracker() as tracker:
        con.send(True)
        while True:
            if con.poll() and con.recv() == -2:
                break

            logger.debug("Tracking...")
            tracker.track_posture()
