import argparse
import logging

import cv2

from models.face_recognition.recognition import get_face_match

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    args = parser.parse_args()
    logger.debug("Reading image")
    face = cv2.imread(args.image_path)
    logger.debug("Checking for a match")
    matched_id = get_face_match(face)

    logger.debug("Matched user %d", matched_id)


if __name__ == "__main__":
    main()
