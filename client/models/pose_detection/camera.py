"""
Camera utilities for posture detection
"""

import numpy as np

from mediapipe.tasks.python.components.containers.landmark import Landmark
from mediapipe.python.solutions.pose import PoseLandmark
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult


def is_camera_aligned(pose_landmark_result: PoseLandmarkerResult) -> np.bool_:
    """Checks whether the camera is aligned to capture the person's side view.

    Args:
        pose_landmarker_result: Landmarker result as returned by a
          mediapipe.tasks.vision.PoseLandmarker

    Returns:
        True if the camera is aligned, False otherwise
    """
    landmarks: list[list[Landmark]] = pose_landmark_result.pose_world_landmarks

    # TODO: investigate case when more than one pose is detected in image
    if len(landmarks) == 0:
        return np.bool_(False)
    landmarks = landmarks[0]

    # Get landmarks
    l_shoulder = landmarks[PoseLandmark.LEFT_SHOULDER]
    r_shoulder = landmarks[PoseLandmark.RIGHT_SHOULDER]

    # TODO: Camera alignedness is currently determined by shoulder distance
    # TODO: A more "correct" way to do this is probably to use angles instead
    return (
        np.linalg.norm((l_shoulder.x - r_shoulder.x, l_shoulder.y - r_shoulder.y)) < 100
    )
