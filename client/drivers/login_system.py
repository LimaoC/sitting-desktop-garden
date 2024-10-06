"""
Login system
"""

import logging
from typing import Callable

import numpy as np

from data.routines import next_user_id, create_user
from models.pose_detection.frame_capturer import RaspCapturer
from models.face_recognition.recognition import register_faces, get_face_match, Status
from drivers.data_structures import HardwareComponents, LEFT_BUTTON, RIGHT_BUTTON

NUM_FACES = 5
QUIT = -4
BAD_STATUS_MESSAGES = {
    Status.NO_FACES.value: "No face detected please",
    Status.TOO_MANY_FACES.value: "Too many faces detected",
    Status.NO_MATCH.value: "Could not match face",
}
QUIT_INSTRUCTIONS = "Right button to quit"

Action = Callable[[HardwareComponents], int]

logger = logging.getLogger(__name__)


def handle_authentication(hardware: HardwareComponents) -> int:
    """Run authentication loop until user either registers or logs in.

    Args:
        hardware: connected RPI hardware

    Returns:
        id of logged in user.
    """
    while True:
        _log_and_send(hardware, "Left button to login\nRight button to register")
        button = hardware.wait_for_button_press()

        if button == RIGHT_BUTTON:
            status = _loop_action(hardware, _attempt_register)

        if button == LEFT_BUTTON:
            status = _loop_action(hardware, _attempt_login)

        if _is_status_id(status):
            return status

        if status != QUIT:
            error = ValueError(f"Did not expect status: {status}")
            hardware.send_message(str(error))
            raise error


def _loop_action(hardware: HardwareComponents, action: Action) -> int:
    """Loop action until appropriate status is returned"""
    while True:
        status = action(hardware)

        if status == QUIT:
            return QUIT

        if _is_status_id(status):
            return status


def _attempt_login(hardware: HardwareComponents) -> int:
    capturer = RaspCapturer()
    message = f"Press left button to take photo\n{QUIT_INSTRUCTIONS}"
    _log_and_send(hardware, message, message_time=0)

    button_pressed = hardware.wait_for_button_press()
    if button_pressed == LEFT_BUTTON:
        face, _ = capturer.get_frame()

    if button_pressed == RIGHT_BUTTON:
        return QUIT

    status = get_face_match(face)
    _handle_status_message(hardware, status)

    return status


def _attempt_register(hardware: HardwareComponents) -> int:
    capturer = RaspCapturer()

    # Capture NUM_FACES faces
    faces: list[np.ndarray] = []
    for i in range(NUM_FACES):
        message = (
            f"Press left button to take photo {i + 1}/{NUM_FACES}\n"
            f"{QUIT_INSTRUCTIONS}"
        )
        _log_and_send(hardware, message, message_time=0)

        button_pressed = hardware.wait_for_button_press()
        if button_pressed == RIGHT_BUTTON:
            return QUIT

        if button_pressed == LEFT_BUTTON:
            frame, _ = capturer.get_frame()
            faces.append(frame)

    # Try register faces
    _log_and_send(hardware, "Registering...")
    user_id = next_user_id()
    status = register_faces(user_id, faces)

    if status == Status.OK.value:
        create_user()
        _log_and_send(hardware, "Registration successful!")
        return user_id

    _handle_status_message(hardware, status)

    return status


def _is_status_id(status: int) -> bool:
    return status > 0


def _handle_status_message(hardware: HardwareComponents, status: int) -> None:
    if status in BAD_STATUS_MESSAGES:
        _log_and_send(hardware, BAD_STATUS_MESSAGES[status])


def _log_and_send(
    hardware: HardwareComponents, message: str, message_time: int = 1
) -> None:
    logger.debug(message)
    hardware.send_message(message, message_time=message_time)
