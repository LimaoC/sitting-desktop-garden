"""
Camera utilities for posture detection
"""

import mediapipe as mp
from mediapipe.tasks.python.components.containers import landmark as landmark_module
import numpy as np
from typing import List

PoseLandmark = mp.solutions.pose.PoseLandmark
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
Landmark = landmark_module.Landmark


def is_camera_aligned(pose_landmark_result: PoseLandmarkerResult) -> bool:
    """
    Returns whether the camera is aligned to capture the person's side view.
    """
    landmarks: List[List[Landmark]] = pose_landmark_result.pose_world_landmarks

    # TODO: investigate case when more than one pose is detected in image
    if len(landmarks) == 0:
        return False
    landmarks = landmarks[0]

    # Get landmarks
    l_shoulder = landmarks[PoseLandmark.LEFT_SHOULDER]
    r_shoulder = landmarks[PoseLandmark.RIGHT_SHOULDER]

    # TODO: Camera alignedness is currently determined by shoulder distance
    # TODO: A more "correct" way to do this is probably to use angles instead
    return (
        np.linalg.norm((l_shoulder.x - r_shoulder.x, l_shoulder.y - r_shoulder.y)) < 100
    )
