"""
Posture classification

REF: https://learnopencv.com/building-a-body-posture-analysis-system-using-mediapipe/
"""

import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.components.containers import landmark as landmark_module
from typing import List

PoseLandmark = mp.solutions.pose.PoseLandmark


def posture_angle(x1, y1, x2, y2) -> np.float_:
    """
    Returns the angle (in degrees) between P2 and P3, where P1 = (x1, y1),
    P2 = (x2, y2), and P3 = (x1, 0).

    P3 is a point on the vertical axis of P1, and is the "ideal" location of P2.

    For a neck inclination calculation, take P2 to be the eye location and P1 to be the
    shoulder location and pivot point.

    For a torso inclination calculation, take P2 to be the hip location and P1 to be
    the hip location and pivot point.
    """
    theta = np.arccos(y1 * (y1 - y2) / (y1 * np.linalg.norm((x2 - x1, y2 - y1))))
    return (180 / np.pi) * theta


def classify(
    output_image: mp.Image,
    pose_landmark_result: mp.tasks.vision.PoseLandmarkerResult,
):
    landmarks: List[List[landmark_module.NormalizedLandmark]] = (
        pose_landmark_result.pose_landmarks
    )

    # TODO: investigate case when more than one pose is detected in image
    assert len(landmarks) == 1
    landmarks = landmarks[0]

    # Calculate landmark coordinates
    image_dims = np.array([output_image.width, output_image.height])

    # Left shoulder
    l_shoulder_x = landmarks[PoseLandmark.LEFT_SHOULDER].x
    l_shoulder_y = landmarks[PoseLandmark.LEFT_SHOULDER].y
    l_shoulder = np.array([l_shoulder_x, l_shoulder_y]) * image_dims
    # Right shoulder
    r_shoulder_x = landmarks[PoseLandmark.RIGHT_SHOULDER].x
    r_shoulder_y = landmarks[PoseLandmark.RIGHT_SHOULDER].y
    r_shoulder = np.array([r_shoulder_x, r_shoulder_y]) * image_dims
    # Left ear
    # l_ear_x = landmarks[PoseLandmark.LEFT_EAR].x
    # l_ear_y = landmarks[PoseLandmark.LEFT_EAR].y
    # l_ear = np.array(landmarks[PoseLandmark.LEFT_EAR]) * image_dims
    # Right ear
    # r_ear_x = landmarks[PoseLandmark.RIGHT_EAR].x
    # r_ear_y = landmarks[PoseLandmark.RIGHT_EAR].y
    # r_ear = np.array(landmarks[PoseLandmark.RIGHT_EAR]) * image_dims
    # Left hip
    l_hip_x = landmarks[PoseLandmark.LEFT_HIP].x
    l_hip_y = landmarks[PoseLandmark.LEFT_HIP].y
    l_hip = np.array([l_hip_x, l_hip_y]) * image_dims
    # Right hip
    # r_hip_x = landmarks[PoseLandmark.RIGHT_HIP].x
    # r_hip_y = landmarks[PoseLandmark.RIGHT_HIP].y
    # r_hip = np.array([r_hip_x, r_hip_y]) * image_dims

    # shoulder_distance = np.linalg.norm(l_shoulder - r_shoulder)
    neck_inclination = posture_angle(l_shoulder, r_shoulder)
    torso_inclination = posture_angle(l_hip, l_shoulder)

    if neck_inclination < 40 and torso_inclination < 10:
        print("Good")
    else:
        print("Bad")
