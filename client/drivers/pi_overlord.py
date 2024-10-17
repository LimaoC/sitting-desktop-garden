"""
Entry point for the Sitting Desktop Garden Raspberry Pi Pot Client.

Author:
    Gabriel Field (47484306), Mitchell Clark
"""

import argparse
import logging
import time
from datetime import datetime, timedelta

import RPi.GPIO as GPIO
from data.routines import (
    init_database,
    destroy_database,
    reset_registered_face_embeddings,
    get_user_postures,
    Posture,
)
from drivers.data_structures import ControlledData, HardwareComponents
from drivers.login_system import RESET, handle_authentication
from models.pose_detection.frame_capturer import RaspCapturer
from PiicoDev_SSD1306 import *
from PiicoDev_Switch import *
from PiicoDev_Unified import sleep_ms

#: Pin to which the vibration motor is attached. This is D8 on the PiicoDev header.
CUSHION_GPIO_PIN = 8

#: Number of milliseconds between telling the user that login has succeeded and beginning real functionality.
LOGIN_SUCCESS_DELAY = 1000
#: Number of milliseconds between the user successfully logging out and returning to main().
LOGOUT_SUCCESS_DELAY = 1000

#: Proportion of the time the user must be in frame for any feedback to be given.
PROPORTION_IN_FRAME_THRESHOLD = 0.4

#: Minimum delay between reading posture data from the SQLite database, in run_user_session().
GET_POSTURE_DATA_TIMEOUT = timedelta(milliseconds=10000)
#: Width (in pixels) of each individual entry on the posture graph. (One pixel is hard to read.)
POSTURE_GRAPH_DATUM_WIDTH = 5
#: The number of data points to split the total data into, collected each time we read from the SQLite database.
NUM_DATA_POINTS_PER_TIMEOUT = 3

#: Minimum delay between consecutive uses of the vibration motor. Used in handle_feedback().
HANDLE_CUSHION_FEEDBACK_TIMEOUT = timedelta(milliseconds=30000)
#: Length of time for which the vibration motor should vibrate. Used in handle_cushion_feedback().
CUSHION_ACTIVE_INTERVAL = timedelta(milliseconds=3000)
#: Threshold for vibration cushion feedback. If the proportion of "good" sitting posture is below this, the cushion will vibrate.
CUSHION_PROPORTION_GOOD_THRESHOLD = 0.5

#: Minimum delay between consecutive uses of the plant-controlling servos. Used in handle_feedback().
HANDLE_PLANT_FEEDBACK_TIMEOUT = timedelta(milliseconds=15000)
#: Threshold for I. Jensen Plant Mover 10000 feedback. If the proportion of "good" sitting posture is below this,
#: the plant will move down.
PLANT_PROPORTION_GOOD_THRESHOLD = 0.5

#: Number of milliseconds between each loop iteration in run_user_session().
USER_SESSION_INTERVAL = 100

logger = logging.getLogger(__name__)


def main():
    """
    Entry point for the control program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-posture-model",
        action="store_true",
        help="Whether to run the posture model. Useful for debugging.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    logger.debug("Running main")

    logger.debug("Initialising database")
    init_database()

    # Spin up the posture tracking process
    if not args.no_posture_model:
        from models.pose_detection.routines import PostureProcess

        logger.debug("Initialising posture tracking process")
        posture_process = PostureProcess(frame_capturer=RaspCapturer)

    # Handle user login/registration, posture tracking, and running the user session
    # Under normal circumstances, this loop shouldn't exit
    while True:
        # Attempt to login an existing user or register a new user
        user_id = handle_authentication(hardware)

        # Handle a "hard" reset, which resets the database, all registered faces,
        # and the hardware
        if user_id == RESET:
            _reset_garden()
            continue

        # Create user session data
        user = ControlledData.make_empty(user_id)

        # Let the posture tracking process know about the current user's id'
        if not args.no_posture_model:
            posture_process.track_user(user_id)

        logger.debug("Login successful")

        run_user_session(user)

        # Let the posture tracking process if the user has logged out
        if not args.no_posture_model:
            posture_process.untrack_user()


# SECTION: Hardware initialisation


def initialise_hardware() -> HardwareComponents:
    """
    Set up hardware for use throughout the project. We have:
        button0 with address switches [0, 0, 0, 0]
        button1 with address switches [0, 0, 0, 1]
        OLED display with address switch off
        Vibration motor attached to GPIO pin BUZZER_GPIO_PIN

    Returns:
        Object consisting of all hardware components connected to the Raspberry Pi.

    """
    logger.debug("<!> initialise_hardware()")
    return_me = HardwareComponents.make_fresh()
    # Clear button queues
    return_me.button0.was_pressed
    return_me.button1.was_pressed
    # Set up GPIO pins
    GPIO.setmode(GPIO.BCM)  # Same pin numbering convention as the PiicoDev header
    GPIO.setup(CUSHION_GPIO_PIN, GPIO.OUT)
    # Write low to stop buzzer from mistakenly buzzing, if necessary
    GPIO.output(CUSHION_GPIO_PIN, GPIO.LOW)

    logger.debug("<!> initialise_hardware() FINISHED")
    return return_me


# SECTION: Control for the logged-in user


def run_user_session(user: ControlledData) -> None:
    """
    Main control flow once a user is logged in.

    Args:
        user: data encapsulating the current state of the program.

    Requires:
        ! user.is_failed()
    """
    LOGIN_MESSAGE = "Logged in with user id: " + str(user.get_user_id())
    LOGOUT_MESSAGE = "Logged out user id " + str(user.get_user_id())

    # Initialise posture graph for the current session
    hardware.initialise_posture_graph(user.get_user_id())

    # Wind plant down all the way
    hardware.wind_plant_safe()

    # Display message to user
    hardware.display.fill(0)
    hardware.oled_display_text(LOGIN_MESSAGE, 0, 0, 1)
    hardware.display.show()
    sleep_ms(LOGIN_SUCCESS_DELAY)

    # Clear button queues
    hardware.button0.was_pressed
    hardware.button1.was_pressed
    # Set up initial display
    hardware.display.fill(0)
    hardware.oled_display_texts(
        hardware.get_control_messages(user.get_user_id()), 0, 0, 1
    )
    hardware.display.show()

    while True:
        # Check for user logout
        if hardware.button0.was_pressed:
            hardware.display.fill(0)
            hardware.oled_display_text(LOGOUT_MESSAGE, 0, 0, 1)
            hardware.display.show()
            sleep_ms(LOGOUT_SUCCESS_DELAY)
            logger.debug("<!> END run_user_session()")
            return

        # Run core functionality
        update_display_screen(user)
        handle_posture_graph(user)
        handle_feedback(user)

        sleep_ms(USER_SESSION_INTERVAL)


def update_display_screen(user: ControlledData) -> bool:
    """
    Update the display screen with whatever needs to be on there.

    We will display:
        As per HardwareComponents.get_control_messages(), and
        Current-session posture graph

    Args:
        user: data encapsulating the current state of the program.

    Returns:
        True, always. If you get a False return value, then something has gone VERY wrong.

    Requires:
        ! user.is_failed()

    Ensures:
        ! user.is_failed()
    """
    while (
        not user.get_posture_data().empty()
    ):  # NOTE: This is much more robust than getting a fixed number of things out of the queue
        hardware.display.fill(0)
        # Display user messages
        hardware.oled_display_texts(
            hardware.get_control_messages(user.get_user_id()), 0, 0, 1
        )
        # Display posture graph data
        hardware.display.updateGraph2D(
            hardware.posture_graph, user.get_posture_data().get_nowait()
        )
        hardware.display.show()

    return True


def handle_posture_graph(user: ControlledData) -> bool:
    """
    Get a snapshot of the user's posture data.
    Use this information to update the data for the posture graph.

    Args:
        (user : ControlledData): Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! user.is_failed()
    Ensures:
        ! user.is_failed()
    """
    now = datetime.now()

    if now > user.get_last_snapshot_time() + GET_POSTURE_DATA_TIMEOUT:
        # Get the most recent posture data for the user
        recent_posture_data = get_user_postures(
            user.get_user_id(),
            num=-1,
            period_start=now - GET_POSTURE_DATA_TIMEOUT,
            period_end=now,
        )

        # Exit if no data
        if len(recent_posture_data) == 0:
            logger.debug(
                "<!> Exiting handle_posture_monitoring_new() early: Not enough data"
            )
            return True

        # Exit if person not in frame enough
        average_prop_in_frame = sum(
            [posture.prop_in_frame for posture in recent_posture_data]
        ) / len(recent_posture_data)
        if average_prop_in_frame < PROPORTION_IN_FRAME_THRESHOLD:
            logger.debug(
                "<!> Exiting handle_posturing_monitoring_new() early: Not in frame for a high enough proportion of time."
            )
            user.set_last_snapshot_time(datetime.now())
            return True

        # Sort the list by period_start
        recent_posture_data = sorted(
            recent_posture_data, key=lambda posture: posture.period_start
        )

        # Calculate total time span
        start_time = recent_posture_data[0].period_start
        end_time = recent_posture_data[-1].period_end
        total_time = end_time - start_time

        # Calculate the interval length
        interval = total_time / NUM_DATA_POINTS_PER_TIMEOUT

        # Setup sublists, where each sublist is a portion of the overall data
        split_posture_lists: list[list[Posture]]
        split_posture_lists = [[] for _ in range(NUM_DATA_POINTS_PER_TIMEOUT)]

        # What is in each sublist is determined by period_start
        # We want an approximately equal amount of data in each sublist
        for posture in recent_posture_data:
            index = min(
                NUM_DATA_POINTS_PER_TIMEOUT - 1,
                int((posture.period_start - start_time) // interval),
            )
            split_posture_lists[index].append(posture)

        new_prop_good_data = []
        # Enqueue the average good posture for each data point for the graph to use
        for posture_list in split_posture_lists:
            if len(posture_list) == 0:
                continue
            logger.debug(f"<!> {posture_list=}")
            average_prop_good = sum(
                [posture.prop_good for posture in posture_list]
            ) / len(posture_list)
            new_prop_good_data += [average_prop_good] * POSTURE_GRAPH_DATUM_WIDTH
        user.accept_new_posture_data(new_prop_good_data)

        user.set_last_snapshot_time(now)

    return True


def handle_feedback(user: ControlledData) -> bool:
    """
    Provide feedback to the user if necessary.

    Args:
        user: Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.

    Requires:
        ! user.is_failed()

    Ensures:
        ! user.is_failed()
    """
    if datetime.now() > user.get_last_cushion_time() + HANDLE_CUSHION_FEEDBACK_TIMEOUT:
        if not handle_cushion_feedback(user):
            return False
    if datetime.now() > user.get_last_plant_time() + HANDLE_PLANT_FEEDBACK_TIMEOUT:
        if not handle_plant_feedback(user):
            return False

    return True


def handle_cushion_feedback(user: ControlledData) -> bool:
    """
    Vibrate cushion (if necessary), and update the timestamp of when cushion feedback was last given.

    Args:
        user: Data encapsulating the current state of the program.

    Returns:
        True, always. If you get a False return value, then something has gone VERY wrong.

    Requires:
        ! user.is_failed()

    Ensures:
        ! user.is_failed()
    """
    logger.debug("<!> handle_cushion_feedback()")

    # Load posture records within the last HANDLE_CUSHION_FEEDBACK_TIMEOUT
    now = datetime.now()
    recent_posture_data = get_user_postures(
        user.get_user_id(),
        num=-1,
        period_start=now - HANDLE_CUSHION_FEEDBACK_TIMEOUT,
        period_end=now,
    )

    # Exit if no data
    if len(recent_posture_data) == 0:
        logger.debug("<!> Exiting handle_cushion_feedback() early: No data")
        user.set_last_cushion_time(datetime.now())
        return True
    # Exit if person not in frame enough
    average_prop_in_frame = sum(
        [posture.prop_in_frame for posture in recent_posture_data]
    ) / len(recent_posture_data)
    if average_prop_in_frame < PROPORTION_IN_FRAME_THRESHOLD:
        logger.debug(
            "<!> Exiting handle_cushion_feedback() early: Not in frame for a high enough proportion of time."
        )
        user.set_last_cushion_time(datetime.now())
        return True

    # Get average proportion of good posture
    average_prop_good = sum(
        [posture.prop_good for posture in recent_posture_data]
    ) / len(recent_posture_data)
    if average_prop_good >= CUSHION_PROPORTION_GOOD_THRESHOLD:
        logger.debug("<!> Exiting handle_cushion_feedback() early: You sat well :)")
        user.set_last_cushion_time(datetime.now())
        return True

    # If posture not good enough, turn buzzer on
    buzzer_start_time = datetime.now()
    GPIO.output(CUSHION_GPIO_PIN, GPIO.HIGH)
    logger.debug("<!> buzzer on")
    while datetime.now() < buzzer_start_time + CUSHION_ACTIVE_INTERVAL:
        sleep_ms(100)
    # Turn buzzer off
    GPIO.output(CUSHION_GPIO_PIN, GPIO.LOW)
    logger.debug("<!> buzzer off")

    user.set_last_cushion_time(datetime.now())
    return True


def handle_plant_feedback(user: ControlledData) -> bool:
    """
    Set the plant height according to short-term current session data, and update the timestamp
    of when plant feedback was last given.

    Args:
        user: Data encapsulating the current state of the program.

    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.

    Requires:
        ! user.is_failed()
    Ensures:
        ! user.is_failed()
    """
    logger.debug("<!> handle_plant_feedback()")

    now = datetime.now()

    if now > user.get_last_plant_time() + HANDLE_PLANT_FEEDBACK_TIMEOUT:
        # Get the most recent posture data for the user
        recent_posture_data = get_user_postures(
            user.get_user_id(),
            num=-1,
            period_start=now - GET_POSTURE_DATA_TIMEOUT,
            period_end=now,
        )

        # Exit if no data
        if len(recent_posture_data) == 0:
            logger.debug("<!> Exiting handle_plant_feedback() early: No data")
            user.set_last_plant_time(datetime.now())
            return True

        # Exit if person not in frame enough
        average_prop_in_frame = sum(
            [posture.prop_in_frame for posture in recent_posture_data]
        ) / len(recent_posture_data)
        if average_prop_in_frame < PROPORTION_IN_FRAME_THRESHOLD:
            logger.debug(
                "<!> Exiting handle_plant_feedback() early: Not in frame for a high enough proportion of time."
            )
            user.set_last_plant_time(datetime.now())
            return True

        # Calculate average proportion of good posture
        average_prop_good = sum(
            [posture.prop_good for posture in recent_posture_data]
        ) / len(recent_posture_data)

        # Raise plant 1 'level' if posture is good, otherwise lower it 1.
        if average_prop_good >= PLANT_PROPORTION_GOOD_THRESHOLD:
            hardware.set_plant_height(hardware.plant_height + 1)
        else:
            hardware.set_plant_height(hardware.plant_height - 1)

        user.set_last_plant_time(datetime.now())

    return True


def _reset_garden() -> None:
    """Reset data, faces and hardware."""
    logger.debug("<!> Burning the garden to the ground...")

    global hardware

    destroy_database()
    logger.debug("\t<!> initialising database anew...")
    init_database()
    logger.debug("\t<!> resetting face embeddings...")
    reset_registered_face_embeddings()
    logger.debug("\t<!> initialising hardware...")
    hardware = initialise_hardware()
    logger.debug("\t<!> Like a phoenix, the Sitting Desktop Garden rises anew")


# LAUNCH

if __name__ == "__main__":
    hardware = initialise_hardware()
    main()
