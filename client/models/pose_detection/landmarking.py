"""Pose landmarking"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
import mediapipe as mp

from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult
from mediapipe.framework.formats import landmark_pb2
from models.pose_detection.classification import posture_classify
from models.pose_detection.camera import is_camera_aligned


@dataclass
class AnnotatedImage:
    """Represents mutable annotated image through data attribute.

    Can be used to set annotated image within a callback asynchronously without raising
    an error.
    """

    data: Optional[np.ndarray] = None


def draw_landmarks_on_image(
    bgr_image: np.ndarray, detection_result: PoseLandmarkerResult
) -> np.ndarray:
    """
    Args:
        bgr_image: CxWxH image array where channels are sorted in BGR.
        detection_result: Landmarker result as returned by a
            mediapipe.tasks.vision.PoseLandmarker.
    Returns:
        Image with landmarks annotated.
    """
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(bgr_image)

    for pose_landmarks in pose_landmarks_list:
        # Define proto
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        normalized_landmarks = [
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z)
            for landmark in pose_landmarks
        ]
        pose_landmarks_proto.landmark.extend(normalized_landmarks)

        # Draw landmarks
        mp.solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            mp.solutions.pose.POSE_CONNECTIONS,
            mp.solutions.drawing_styles.get_default_pose_landmarks_style(),
        )
    return annotated_image


def display_landmarking(
    result: PoseLandmarkerResult,
    output_image: mp.Image,
    timestamp: int,
    annotated_image: AnnotatedImage,
) -> None:
    """Mutates annotated image to contain visualization of detected landmarks.

    Also prints debugging info to the standard output.

    Args:
        result: Landmarker result as returned by a mediapipe.tasks.vision.PoseLandmarker
        output_image: Raw image used for landmarking.
        timestamp: Video timestamp in milliseconds.
        annotated_image: Image to mutate.
    """
    annotated_image.data = draw_landmarks_on_image(output_image.numpy_view(), result)
    print(
        f"Timestamp: {timestamp}\n"
        f"Pose landmarker result: {result}\n"
        f"Camera alignment: {is_camera_aligned(result)}\n"
        f"Good posture: {posture_classify(result)}"
    )
