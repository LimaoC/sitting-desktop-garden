"""
Posture classification
"""

import mediapipe as mp
from mediapipe.tasks.python.components.containers import landmark as landmark_module
import numpy as np
from typing import List

PoseLandmark = mp.solutions.pose.PoseLandmark
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
Landmark = landmark_module.Landmark

NECK_ANGLE_THRESHOLD = 40
TORSO_ANGLE_THRESHOLD = 10


def posture_angle(p1: Landmark, p2: Landmark) -> np.float64:
    """
    Returns the angle (in degrees) between P2 and P3, where P3 is a point on the
    vertical axis of P1 (i.e. its x coordinate is the same as P1's), and is the "ideal"
    location of the P2 landmark for good posture.

    The y coordinate of P3 is irrelevant but for simplicity we set it to zero.

    For a neck inclination calculation, take P1 to be the shoulder location and pivot
    point, and P2 to be the ear location.

    For a torso inclination calculation, take P1 to be the hip location and pivot
    point, and P2 to be the hip location.
    """
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    theta = np.arccos(y1 * (y1 - y2) / (y1 * np.linalg.norm((x2 - x1, y2 - y1))))
    return (180 / np.pi) * theta


def posture_classify(pose_landmark_result: PoseLandmarkerResult) -> bool:
    """
    Returns whether the pose in the image has good (True) or bad (False) posture.

    Note: The camera should be aligned to capture the person's side view; the output
    may not be accurate otherwise. See `is_camera_aligned()`.

    REF: https://learnopencv.com/building-a-body-posture-analysis-system-using-mediapipe
    """
    landmarks: List[List[Landmark]] = pose_landmark_result.pose_world_landmarks

    # TODO: investigate case when more than one pose is detected in image
    if len(landmarks) == 0:
        return False
    landmarks = landmarks[0]

    # Get landmarks
    l_shoulder = landmarks[PoseLandmark.LEFT_SHOULDER]
    r_shoulder = landmarks[PoseLandmark.RIGHT_SHOULDER]
    l_ear = landmarks[PoseLandmark.LEFT_EAR]
    r_ear = landmarks[PoseLandmark.RIGHT_EAR]
    l_hip = landmarks[PoseLandmark.LEFT_HIP]
    r_hip = landmarks[PoseLandmark.RIGHT_HIP]

    # Calculate neck & torso inclinations on left and right side and take their average
    l_neck_inclination = posture_angle(l_shoulder, l_ear)
    r_neck_inclination = posture_angle(r_shoulder, r_ear)
    l_torso_inclination = posture_angle(l_hip, l_shoulder)
    r_torso_inclination = posture_angle(r_hip, r_shoulder)

    neck_inclination = (l_neck_inclination + r_neck_inclination) / 2
    torso_inclination = (l_torso_inclination + r_torso_inclination) / 2

    return (
        neck_inclination < NECK_ANGLE_THRESHOLD
        and torso_inclination < TORSO_ANGLE_THRESHOLD
    )
