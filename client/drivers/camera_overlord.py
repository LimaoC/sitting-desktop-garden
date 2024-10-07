"""
This script periodically takes photos and saves them to a temporary file on ram. This
allows multiple programs to access the camera feed at once.

Exits gracefully with status INTERRUPTED and closes the camera if a sigint is received.
"""

import logging
import os
import signal
import time
from enum import Enum

from picamera2 import Picamera2


class ExitCode(Enum):
    INTERRUPTED = 1


logger = logging.getLogger(__name__)


def handle_quit(signo, frame):
    logger.info("Received SIGINT, quitting")
    picam2.close()
    quit(ExitCode.INTERRUPTED.value)


if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_still_configuration({"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    picam2.options["quality"] = 80

    signal.signal(signal.SIGINT, handle_quit)

    try:
        f = open("/tmp/snapshot.jpg", "x")
        f.close()
    except FileExistsError:
        print("Snapshot already exists")
    
    try:
        f = open("/tmp/big_brother.jpg", "x")
        f.close()
    except FileExistsError:
        print("Big Brother already exists")
    

    while True:
        for _ in range(2 * 3):
            picam2.capture_file("/tmp/snapshot2.jpg")
            os.replace("/tmp/snapshot2.jpg", "/tmp/snapshot.jpg")
            time.sleep(0.5)
        picam2.capture_file("/tmp/snapshot3.jpg")
        os.replace("/tmp/snapshot3.jpg", "/tmp/big_brother.jpg")
