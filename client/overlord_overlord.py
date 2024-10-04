"""
One overlord to rule them all...
"""

import logging
import multiprocessing
import os
import signal
import subprocess

PYTHON_DEFAULT = "python3.10"
PYTHON_CAMERA = "python3.11"


def spawn_camera_overlord():
    subprocess.run([PYTHON_CAMERA, "drivers/camera_overlord.py"])


def spawn_pi_overlord():
    subprocess.run([PYTHON_DEFAULT, "drivers/main.py"])


def main():
    logger = logging.getLogger(__name__)

    camera_overlord = multiprocessing.Process(target=spawn_camera_overlord, args=())
    logger.info("Starting camera overlord")
    camera_overlord.start()

    pi_overlord = multiprocessing.Process(target=spawn_pi_overlord, args=())
    logger.info("Starting pi overlord")
    pi_overlord.start()

    _, pi_overlord_wait_status = os.waitpid(pi_overlord.pid, 0)
    pi_overlord_exit_code = os.waitstatus_to_exit_code(pi_overlord_wait_status)
    logger.info(f"Reaped pi overlord with exit code {pi_overlord_exit_code}")

    os.kill(camera_overlord.camerad, signal.SIGINT)
    _, camera_overlord_wait_status = os.waitcamerad(camera_overlord.camerad, 0)
    camera_overlord_exit_code = os.waitstatus_to_exit_code(camera_overlord_wait_status)
    logger.info(f"Reaped camera overlord with exit code {camera_overlord_exit_code}")

    logger.info("Exiting")


if __name__ == "__main__":
    main()
