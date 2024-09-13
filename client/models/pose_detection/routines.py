"""Routines that can be integrated into a main control flow."""

import statistics
import time
import logging
import multiprocessing as multp
import multiprocessing.connection as connection
from importlib import resources
from typing import Callable, Mapping, Optional, Type
from datetime import datetime

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

from data.routines import Posture, save_posture
from models.pose_detection.landmarking import AnnotatedImage, display_landmarking
from models.pose_detection.camera import is_camera_aligned
from models.pose_detection.classification import posture_classify
from models.pose_detection.frame_capturer import FrameCapturer, OpenCVCapturer

POSE_LANDMARKER_FILE = resources.files("models.resources").joinpath(
    "pose_landmarker_lite.task"
)

NO_USER = -1
STOP_CHILD = -2

logger = logging.getLogger(__name__)


class PostureProcess:
    """Handles starting and managing a new process that runs posture recognition. Data from this
    process gets written to the sqlite database that can be interfaced with using the data/routines
    API.
    """

    def __init__(self, frame_capturer: Type[FrameCapturer] = OpenCVCapturer) -> None:
        """Create a new process which loads the MediaPipe Pose model and runs periodic posture
        tracking. This initializer blocks until the model is loaded.
        """
        self._parent_con, child_con = multp.Pipe()

        args = (child_con, frame_capturer)
        self._process = multp.Process(target=_run_posture, args=args)
        self._process.start()

        # Blocks until something is recieved from child
        self._parent_con.recv()

        logger.debug("Done loading model and communicated to parent.")

    def track_user(self, user_id: int) -> None:
        """Starts tracking posture and writing to database.

        Args:
            user_id: The user to associate posture data with in the database.
        """
        self._parent_con.send(user_id)

    def untrack_user(self) -> None:
        """Stop tracking posture for the current user if one exists."""
        self._parent_con.send(NO_USER)

    def stop(self) -> None:
        """Gracefully end the process."""
        self._parent_con.send(STOP_CHILD)


class PostureTracker(PoseLandmarker):
    """Handles routines for a Posture Tracker.

    Attributes:
        user_id: Id for the user currently being tracked.
    """

    def __init__(
        self,
        graph_config: calculator_pb2.CalculatorGraphConfig,
        running_mode: VisionTaskRunningMode,
        packet_callback: Callable[[Mapping[str, Packet]], None],
    ) -> None:
        super().__init__(graph_config, running_mode, packet_callback)

        self._user_id = NO_USER

        self._posture_scores: list[bool] = []
        self._in_frames: list[bool] = []
        self._start_time = time.time()
        self._period_start = datetime.now()

        self.frame_capturer: Optional[FrameCapturer] = None

    @property
    def user_id(self) -> int:
        """Currently tracked user. Data will be associated with this user in the database."""
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int) -> None:
        self._user_id = user_id
        self._new_period()

    def track_posture(self) -> None:
        """Get frame from video capture device and process with pose model, then posture
        algorithm. Saves posture data to database periodically.
        """
        if self.frame_capturer is None:
            raise ValueError(
                "Please set a frame capturer before trying to track posture"
            )

        if self.user_id == NO_USER:
            return

        frame, _ = self.frame_capturer.get_frame()

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = self.detect(mp_image)

        aligned = bool(is_camera_aligned(result))
        self._in_frames.append(aligned)
        if aligned:
            self._posture_scores.append(bool(posture_classify(result)))

        self._save_period()

    def _save_period(self) -> None:
        if time.time() - self._start_time <= 60:
            return

        period_end = datetime.now()
        posture = Posture(
            id_=None,
            user_id=self.user_id,
            prop_good=statistics.mean(self._posture_scores),
            prop_in_frame=statistics.mean(self._in_frames),
            period_start=self._period_start,
            period_end=period_end,
        )
        save_posture(posture)
        self._new_period()

    def _new_period(self) -> None:
        self._posture_scores = []
        self._in_frames = []
        self._start_time = time.time()
        self._period_start = datetime.now()


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


def create_posture_tracker(frame_capturer: FrameCapturer) -> PostureTracker:
    """Handles config of single image frame input and model loading.

    Returns:
        Tracker object which acts as context manager.
    """
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=POSE_LANDMARKER_FILE),
        running_mode=RunningMode.IMAGE,
    )

    tracker = PostureTracker.create_from_options(options)
    tracker.frame_capturer = frame_capturer
    return tracker


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


def _run_posture(
    con: connection.Connection, frame_capturer: Type[FrameCapturer]
) -> None:
    # Instantiate frame capturer in subprocess to avoid pickling errors.
    frame_capturer_obj = frame_capturer()
    with create_posture_tracker(frame_capturer_obj) as tracker:
        con.send(True)
        while True:
            # Handle message from parent
            if con.poll():
                parent_msg = con.recv()

                if parent_msg == STOP_CHILD:
                    break

                tracker.user_id = parent_msg

            tracker.track_posture()
