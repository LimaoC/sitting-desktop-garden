"""
Camera utilities for posture detection
"""

import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.components.containers import landmark as landmark_module
from typing import List

PoseLandmark = mp.solutions.pose.PoseLandmark
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
NormalizedLandmark = landmark_module.NormalizedLandmark


def is_camera_aligned(
    output_image: mp.Image, pose_landmark_result: PoseLandmarkerResult
) -> bool:
    """
    Returns whether the camera is aligned to capture the person's side view.
    """
    landmarks: List[List[NormalizedLandmark]] = pose_landmark_result.pose_landmarks
    width, height = output_image.width, output_image.height

    # TODO: investigate case when more than one pose is detected in image
    assert len(landmarks) == 1
    landmarks = landmarks[0]

    # Calculate landmark coordinates
    # Left shoulder
    l_shoulder_x = landmarks[PoseLandmark.LEFT_SHOULDER].x * width
    l_shoulder_y = landmarks[PoseLandmark.LEFT_SHOULDER].y * height
    # Right shoulder
    r_shoulder_x = landmarks[PoseLandmark.RIGHT_SHOULDER].x * width
    r_shoulder_y = landmarks[PoseLandmark.RIGHT_SHOULDER].y * height

    # TODO: Camera alignedness is currently determined by shoulder distance
    # TODO: A more "correct" way to do this is probably to use angles instead
    return (
        np.linalg.norm((l_shoulder_x - r_shoulder_x, l_shoulder_y - r_shoulder_y)) < 100
    )
