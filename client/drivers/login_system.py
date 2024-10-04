"""
Login system
"""

import numpy as np

from data.routines import next_user_id, create_user
from models.pose_detection.frame_capturer import RaspCapturer
from models.face_recognition.recognition import register_faces, get_face_match, Status
from drivers.data_structures import HardwareComponents, LEFT_BUTTON, RIGHT_BUTTON

NUM_FACES = 5
QUIT = -4
BAD_STATUS_MESSAGES = {
    Status.NO_FACES.value: "No face detected please try again",
    Status.TOO_MANY_FACES.value: "Too many faces detected please try again",
}
QUIT_INSTRUCTIONS = "Right button to quit"


def handle_authentication(hardware: HardwareComponents) -> int:
    """Run authentication loop until user either registers or logs in.

    Args:
        hardware: connected RPI hardware

    Returns:
        id of logged in user.
    """
    while True:
        hardware.send_message("Left button to login\nRight button to register")
        button = hardware.wait_for_button_press()

        if button == RIGHT_BUTTON:
            status = handle_register(hardware)

        if button == LEFT_BUTTON:
            status = handle_login(hardware)

        if _is_status_id(status):
            return status

        if status != QUIT:
            error = ValueError(f"Did not expect status: {status}")
            hardware.send_message(str(error))
            raise error


def handle_register(hardware: HardwareComponents) -> int:
    """Tries to register a new user until successful.

    Args:
        hardware: Connected RPI hardware

    Returns:
        User id of new registered user or -4 if the user quits
    """
    while True:
        status = _attempt_register(hardware)

        if status == QUIT:
            return QUIT

        if _is_status_id(status):
            return status


def handle_login(hardware: HardwareComponents) -> int:
    """Tries to login a new user until successful.

    Args:
        hardware: Connected RPI hardware

    Returns:
        User id of logged in user, -4 if the user quits.
    """
    while True:
        status = _attempt_login(hardware)

        if status == QUIT:
            return QUIT

        if _is_status_id(status):
            return status


def _attempt_login(hardware: HardwareComponents) -> int:
    capturer = RaspCapturer()
    hardware.send_message(f"Press left button to take photo\n{QUIT_INSTRUCTIONS}")

    button_pressed = hardware.wait_for_button_press()
    if button_pressed == LEFT_BUTTON:
        face, _ = capturer.get_frame()
    if button_pressed == RIGHT_BUTTON:
        return QUIT

    status = get_face_match(face)
    _send_bad_status(hardware, status)

    return status


def _attempt_register(hardware: HardwareComponents) -> int:
    capturer = RaspCapturer()
    faces: list[np.ndarray] = []
    for i in range(NUM_FACES):
        hardware.send_message(
            f"Press left button to take photo {i + 1}/{NUM_FACES}\n{QUIT_INSTRUCTIONS}"
        )

        button_pressed = hardware.wait_for_button_press()
        if button_pressed == RIGHT_BUTTON:
            return QUIT
        if button_pressed == LEFT_BUTTON:
            frame, _ = capturer.get_frame()
            faces.append(frame)

    hardware.send_message("Attempting register...")
    user_id = next_user_id()
    status = register_faces(user_id, faces)

    if status == Status.OK.value:
        create_user()
        hardware.send_message("Registration successful!")
        return user_id

    _send_bad_status(hardware, status)

    return status


def _is_status_id(status: int) -> bool:
    return status > 0


def _send_bad_status(hardware: HardwareComponents, status: int) -> None:
    if status in BAD_STATUS_MESSAGES:
        hardware.send_message(BAD_STATUS_MESSAGES[status])
