import logging
import argparse

from models.face_recognition.recognition import get_face_match, register_faces
from models.pose_detection.frame_capturer import RaspCapturer, OpenCVCapturer

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pi", action="store_true")
    args = parser.parse_args()

    capturer = RaspCapturer() if args.pi else OpenCVCapturer()
    choice = input("(r)egister or (l)ogin: ")

    if choice == "r":
        faces = []
        user_id = int(input("Enter user id: "))
        for i in range(5):
            input(f"Enter to register a face ({i+1}): ")
            frame, _ = capturer.get_frame()
            faces.append(frame)

        logger.info("Registering face snapshots")
        status = register_faces(user_id, faces)
        logger.info("Registration status %d", status)

    elif choice == "l":
        input("Enter to login: ")
        frame, _ = capturer.get_frame()
        match = get_face_match(frame)
        logger.info("Matched to user id %d", match)


if __name__ == "__main__":
    main()
