from typing import Callable, Mapping

import cv2
import mediapipe as mp
from mediapipe.framework import calculator_pb2
from mediapipe.python._framework_bindings.packet import Packet
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode,
)
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarker,
)

from models.pose_detection.landmarking import AnnotatedImage


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
