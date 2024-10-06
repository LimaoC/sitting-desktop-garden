"""
One overlord to rule them all...
"""

import argparse
import logging
import multiprocessing
import os
import signal
import subprocess

PYTHON_DEFAULT = "python3.10"
PYTHON_CAMERA = "python3.11"


def spawn_camera_overlord():
    subprocess.run([PYTHON_CAMERA, "drivers/camera_overlord.py"])


def spawn_pi_overlord(no_posture_model):
    cmd = [PYTHON_DEFAULT, "drivers/main.py"]
    if no_posture_model:
        cmd.append("--no-posture-model")
    subprocess.run(cmd)


def main():
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-posture-model", action="store_true")
    args = parser.parse_args()

    # Spawn a new process to run the camera indefinitely
    camera_overlord = multiprocessing.Process(target=spawn_camera_overlord, args=())
    logger.info("Starting camera overlord")
    camera_overlord.start()

    # Spawn a new process to run the Raspberry Pi code
    pi_overlord = multiprocessing.Process(
        target=spawn_pi_overlord, args=(args.no_posture_model,)
    )
    logger.info("Starting pi overlord")
    pi_overlord.start()

    # If the Pi process ever terminates, gracefully terminate the camera process
    _, pi_overlord_wait_status = os.waitpid(pi_overlord.pid, 0)
    pi_overlord_exit_code = os.waitstatus_to_exitcode(pi_overlord_wait_status)
    logger.info(f"Reaped pi overlord with exit code {pi_overlord_exit_code}")

    os.kill(camera_overlord.pid, signal.SIGINT)
    _, camera_overlord_wait_status = os.waitpid(camera_overlord.pid, 0)
    camera_overlord_exit_code = os.waitstatus_to_exitcode(camera_overlord_wait_status)
    logger.info(f"Reaped camera overlord with exit code {camera_overlord_exit_code}")

    logger.info("Exiting")


if __name__ == "__main__":
    main()
