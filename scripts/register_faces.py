import logging

import cv2

from data.routines import destroy_database, init_database, register_faces

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.debug("Destroying db")
    destroy_database()
    logger.debug("Init db")
    init_database()

    video = cv2.VideoCapture(0)
    faces = []
    for _ in range(5):
        _, frame = video.read()
        faces.append(frame)
        input("Enter to continue: ")

    video.release()
    logger.debug("Registering faces")
    register_faces(1, faces)


if __name__ == "__main__":
    main()
