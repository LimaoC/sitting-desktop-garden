import logging
import pprint
import argparse

from models.pose_detection.routines import PostureProcess
from models.pose_detection.frame_capturer import RaspCapturer, OpenCVCapturer
from data.routines import destroy_database, init_database, create_user, get_postures

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pi", action="store_true")
    args = parser.parse_args()
    logger.debug(args)

    logger.debug("Testing PostureProces")
    logger.debug("Destroying database")
    destroy_database()
    logger.debug("Creating new database")
    init_database()
    logger.debug("Inserting user")
    user_id = create_user()
    logger.debug("starting postures %s", get_postures())
    process = PostureProcess(frame_capturer=RaspCapturer if args.pi else OpenCVCapturer)
    for i in range(200):
        logger.debug("Parent process running")

        if i == 5:
            logger.debug("Giving child a user to track")
            process.track_user(user_id)

        if input("q to quit: ") == "q":
            process.stop()
            break

    logger.debug("Postures after async tracking \n%s", pprint.pformat(get_postures()))


if __name__ == "__main__":
    main()
