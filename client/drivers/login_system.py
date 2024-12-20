"""
Login system
"""

import logging
from typing import Callable

import numpy as np
from data.routines import create_user, next_user_id
from drivers.data_structures import (
    HardwareComponents,
    LEFT_BUTTON,
    RIGHT_BUTTON,
    DOUBLE_RIGHT_BUTTON,
)
from models.face_recognition.recognition import Status, get_face_match, register_faces
from models.pose_detection.frame_capturer import RaspCapturer

NUM_FACES = 5
QUIT = -6
RESET = -5
BAD_STATUS_MESSAGES = {
    Status.NO_FACES.value: "No face detected please",
    Status.TOO_MANY_FACES.value: "Too many faces detected",
    Status.NO_MATCH.value: "Could not match face",
    Status.ALREADY_REGISTERED.value: "Face already registered",
}
QUIT_INSTRUCTIONS = "Right: quit"

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
        _log_and_send(
            hardware,
            ["Left: login",
            "Right: register",
            "Double press right: reset data"]
        )
        button = hardware.wait_for_button_press()

        if button == RIGHT_BUTTON:
            status = _loop_action(hardware, _attempt_register)

        if button == LEFT_BUTTON:
            status = _loop_action(hardware, _attempt_login)

        if button == DOUBLE_RIGHT_BUTTON:
            return RESET

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
    messages = ["Left: take photo", f"{QUIT_INSTRUCTIONS}"]
    _log_and_send(hardware, messages, message_time=0)

    button_pressed = hardware.wait_for_button_press()
    if button_pressed == LEFT_BUTTON:
        face, _ = capturer.get_frame()

    if button_pressed == RIGHT_BUTTON:
        return QUIT

    _log_and_send(hardware, ["Trying login..."], message_time=0)
    status = get_face_match(face)
    _handle_status_message(hardware, status)

    return status


def _attempt_register(hardware: HardwareComponents) -> int:
    capturer = RaspCapturer()

    # Capture NUM_FACES faces
    faces: list[np.ndarray] = []
    for i in range(NUM_FACES):
        messages = [
            f"Left: take photo {i + 1}/{NUM_FACES}",
            f"{QUIT_INSTRUCTIONS}"
        ]
        _log_and_send(hardware, messages, message_time=0)

        button_pressed = hardware.wait_for_button_press()
        if button_pressed == RIGHT_BUTTON:
            return QUIT

        if button_pressed == LEFT_BUTTON:
            frame, _ = capturer.get_frame()
            faces.append(frame)

    # Try register faces
    _log_and_send(hardware, ["Registering..."])
    user_id = next_user_id()
    status = register_faces(user_id, faces)

    if status == Status.OK.value:
        create_user()
        _log_and_send(hardware, ["Registration successful!"])
        return user_id

    _handle_status_message(hardware, status)

    return status


def _is_status_id(status: int) -> bool:
    return status > 0


def _handle_status_message(hardware: HardwareComponents, status: int) -> None:
    if status in BAD_STATUS_MESSAGES:
        _log_and_send(hardware, BAD_STATUS_MESSAGES[status])


def _log_and_send(
    hardware: HardwareComponents, messages: list[str], message_time: int = 1
) -> None:
    logger.debug(messages)
    hardware.send_message(messages, message_time=message_time)
