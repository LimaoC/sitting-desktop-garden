import logging
import sys

from models.pose_detection.routines import DebugPostureProcess


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    process = DebugPostureProcess()
    while True:
        print("Parent process running...")

        if input("q to quit: ") == "q":
            process.stop()
            break


if __name__ == "__main__":
    main()
