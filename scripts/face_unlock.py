import logging

import cv2
import numpy as np
from data.routines import register_faces
from models.face_recognition.recognition import get_face_match

logger = logging.getLogger(__name__)


def take_snapshot() -> np.ndarray:
    """Opens camera and takes one snapshot"""
    video = cv2.VideoCapture(0)
    _, frame = video.read()
    video.release()
    return frame


def main():
    choice = input("(r)egister or (l)ogin: ")

    if choice == "r":
        faces = []
        user_id = int(input("Enter user id: "))
        for i in range(5):
            input(f"Enter to register a face ({i+1}): ")
            frame = take_snapshot()
            faces.append(frame)

        register_faces(user_id, faces)

    elif choice == "l":
        input("Enter to login: ")
        frame = take_snapshot()
        match = get_face_match(frame)
        print(f"Matched to user id {match}")


if __name__ == "__main__":
    main()
