"""
Posture classification

REF: https://learnopencv.com/building-a-body-posture-analysis-system-using-mediapipe/
"""

import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.components.containers import landmark as landmark_module
from typing import List

PoseLandmark = mp.solutions.pose.PoseLandmark
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
NormalizedLandmark = landmark_module.NormalizedLandmark


def posture_angle(x1, y1, x2, y2) -> np.float_:
    """
    Returns the angle (in degrees) between P2 and P3, where P1 = (x1, y1),
    P2 = (x2, y2), and P3 = (x1, 0).

    P3 is a point on the vertical axis of P1, and is the "ideal" location of P2.

    For a neck inclination calculation, take P1 to be the shoulder location and pivot
    point, and P2 to be the eye location.

    For a torso inclination calculation, take P1 to be the hip location and pivot
    point, and P2 to be the hip location.
    """
    theta = np.arccos(y1 * (y1 - y2) / (y1 * np.linalg.norm((x2 - x1, y2 - y1))))
    return (180 / np.pi) * theta


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


def classify(
    output_image: mp.Image,
    pose_landmark_result: PoseLandmarkerResult,
):
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
    # Left ear
    l_ear_x = landmarks[PoseLandmark.LEFT_EAR].x * width
    l_ear_y = landmarks[PoseLandmark.LEFT_EAR].y * height
    # Right ear
    r_ear_x = landmarks[PoseLandmark.RIGHT_EAR].x * width
    r_ear_y = landmarks[PoseLandmark.RIGHT_EAR].y * height
    # Left hip
    l_hip_x = landmarks[PoseLandmark.LEFT_HIP].x * width
    l_hip_y = landmarks[PoseLandmark.LEFT_HIP].y * height
    # Right hip
    r_hip_x = landmarks[PoseLandmark.RIGHT_HIP].x * width
    r_hip_y = landmarks[PoseLandmark.RIGHT_HIP].y * height

    # Calculate neck & torso inclinations on left and right side and take their average
    l_neck_inclination = posture_angle(l_shoulder_x, l_shoulder_y, l_ear_x, l_ear_y)
    r_neck_inclination = posture_angle(r_shoulder_x, r_shoulder_y, r_ear_x, r_ear_y)
    l_torso_inclination = posture_angle(l_hip_x, l_hip_y, l_shoulder_x, l_shoulder_y)
    r_torso_inclination = posture_angle(r_hip_x, r_hip_y, r_shoulder_x, r_shoulder_y)

    neck_inclination = (l_neck_inclination + r_neck_inclination) / 2
    torso_inclination = (l_torso_inclination + r_torso_inclination) / 2

    if neck_inclination < 40 and torso_inclination < 10:
        print("Good")
    else:
        print("Bad")
