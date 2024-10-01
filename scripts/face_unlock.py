import logging

import cv2
import numpy as np

from models.face_recognition.recognition import get_face_match, register_faces

logger = logging.getLogger(__name__)


def take_snapshot() -> np.ndarray:
    """Opens camera and takes one snapshot"""
    video = cv2.VideoCapture(0)
    _, frame = video.read()
    video.release()
    logger.debug("Frame shape %s", str(frame.shape))
    return frame


def main():
    logging.basicConfig(level=logging.DEBUG)
    choice = input("(r)egister or (l)ogin: ")

    if choice == "r":
        faces = []
        user_id = int(input("Enter user id: "))
        for i in range(5):
            input(f"Enter to register a face ({i+1}): ")
            frame = take_snapshot()
            faces.append(frame)

        logger.info("Registering face snapshots")
        status = register_faces(user_id, faces)
        logger.info("Registration status %d", status)

    elif choice == "l":
        input("Enter to login: ")
        frame = take_snapshot()
        match = get_face_match(frame)
        logger.info("Matched to user id %d", match)


if __name__ == "__main__":
    main()
