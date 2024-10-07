"""
Brief:
    Entry point for the Sitting Desktop Garden Raspberry Pi Pot Client.
File:
    sitting-desktop-garden/client/drivers/main.py
Author:
    Gabriel Field (47484306), Mitchell Clark
"""

## SECTION: Imports
import argparse
import logging
from datetime import datetime, timedelta

import RPi.GPIO as GPIO
from PiicoDev_SSD1306 import *
from PiicoDev_Switch import *
from PiicoDev_Unified import sleep_ms

from models.pose_detection.frame_capturer import RaspCapturer
from data.routines import (
    init_database,
    destroy_database,
    reset_registered_face_embeddings,
    get_user_postures,
    Posture,
)
from drivers.data_structures import ControlledData, HardwareComponents
from drivers.login_system import handle_authentication, RESET

## SECTION: Global constants

CUSHION_GPIO_PIN = 8
""" Pin to which the vibration motor is attached. This is D8 on the PiicoDev header. """

WAIT_FOR_LOGIN_POLLING_INTERVAL = 100
""" Number of milliseconds between each time the button is polled during wait_for_login_attempt(). """
LOGIN_TAKE_PICTURE_INTERVAL = 1000
""" Number of milliseconds between pictures taken for login attempts. """
START_LOGIN_ATTEMPTS_DELAY = 3000
""" Number of milliseconds between starting to attempt_login() and taking the first picture. """
ASK_CREATE_NEW_USER_POLLING_INTERVAL = 100
""" Number of milliseconds between each time the button is polled during ask_create_new_user(). """
FAIL_LOGIN_DELAY = 3000
""" Number of milliseconds between telling the user that login has completely failed and returning from attempt_login(). """
LOGIN_SUCCESS_DELAY = 3000
""" Number of milliseconds between telling the user that login has succeeded and beginning real functionality. """

POSTURE_GRAPH_DATUM_WIDTH = 5
""" Width (in pixels) of each individual entry on the posture graph. (One pixel is hard to read.) """

LOGOUT_SUCCESS_DELAY = 3000
""" Number of milliseconds between the user successfully logging out and returning to main(). """
GET_POSTURE_DATA_TIMEOUT = timedelta(milliseconds=10000)
""" Minimum delay between reading posture data from the SQLite database, in do_everything(). """
PROPORTION_IN_FRAME_THRESHOLD = 0.3
""" Proportion of the time the user must be in frame for any feedback to be given. FIXME: Fine-tune this value later. """

HANDLE_CUSHION_FEEDBACK_TIMEOUT = timedelta(milliseconds=5000)
""" Minimum delay between consecutive uses of the vibration motor. Used in handle_feedback(). """
CUSHION_ACTIVE_INTERVAL = timedelta(milliseconds=1000)
""" Length of time for which the vibration motor should vibrate. Used in handle_cushion_feedback(). """
CUSHION_PROPORTION_GOOD_THRESHOLD = 0.5
"""
Threshold for vibration cushion feedback. If the proportion of "good" sitting posture is below this, the cushion will vibrate. 
FIXME: Fine-tune this value later.
"""

HANDLE_PLANT_FEEDBACK_TIMEOUT = timedelta(milliseconds=10000)
""" Minimum delay between consecutive uses of the plant-controlling servos. Used in handle_feedback(). """

# KILLME:
HANDLE_SNIFF_FEEDBACK_TIMEOUT = timedelta(milliseconds=20000)
""" Minimum delay between consecutive uses of the scent bottle-controlling servos. Used in handle_feedback(). """

DEBUG_DO_EVERYTHING_INTERVAL = 1000
""" DEBUG Number of milliseconds between each loop iteration in do_everything(). """

logger = logging.getLogger(__name__)

## SECTION: main()


def main():
    """
    Entry point for the control program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-posture-model", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    logger.debug("Running main")

    logger.debug("Initialising database")
    init_database()

    if not args.no_posture_model:
        from models.pose_detection.routines import PostureProcess

        logger.debug("Initialising posture tracking process")
        posture_process = PostureProcess(frame_capturer=RaspCapturer)

    while True:
        user_id = handle_authentication(hardware)

        # Handle reset
        if user_id == RESET:
            _reset_garden()
            continue

        # Create user session data
        user = ControlledData.make_empty(user_id)
        if not args.no_posture_model:
            posture_process.track_user(user_id)
        logger.debug("Login successful")

        # Run user session
        do_everything(user)

        if not args.no_posture_model:
            posture_process.untrack_user()


## SECTION: Hardware initialisation


# 2024-09-01_15-29 Gabe: TESTED. for buttons and OLED display.
def initialise_hardware() -> HardwareComponents:
    """
    Set up hardware for use throughout the project. We have:
        button0 with address switches [0, 0, 0, 0]
        button1 with address switches [0, 0, 0, 1]
        OLED display with address switch off
        Vibration motor attached to GPIO pin BUZZER_GPIO_PIN

    Returns:
        (HardwareComponents): Object consisting of all hardware components connected to the Raspberry Pi.

    TODO: Complete the function with all of the hardware peripherals (incrementally, as they get integrated).
    """
    print("<!> initialise_hardware()")  # DEBUG
    return_me = HardwareComponents.make_fresh()
    # Clear button queues
    return_me.button0.was_pressed
    return_me.button1.was_pressed
    # Set up GPIO pins
    GPIO.setmode(GPIO.BCM)  # Same pin numbering convention as the PiicoDev header
    GPIO.setup(CUSHION_GPIO_PIN, GPIO.OUT)
    # Write low to stop buzzer from mistakenly buzzing, if necessary
    GPIO.output(CUSHION_GPIO_PIN, GPIO.LOW)

    print("<!> initialise_hardware() FINISHED")  # DEBUG
    return return_me


## SECTION: Control for the logged-in user


# 2024-09-02 07-03 Gabe: Currently working the following here:
#   top-level control flow
#   interaction with buttons and display
def do_everything(auspost: ControlledData) -> None:
    """
    Main control flow once a user is logged in.

    Args:
        (auspost : ControlledData): Data encapsulating the current state of the program.
    Requires:
        ! auspost.is_failed()

    TODO: Actually implement this
    """
    print("<!> BEGIN do_everything()")

    LOGIN_MESSAGE = "Logged in with user id: " + str(auspost.get_user_id())
    LOGOUT_MESSAGE = "Logged out user id " + str(auspost.get_user_id())

    # Initialise posture graph for the current session
    hardware.initialise_posture_graph(auspost.get_user_id())

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
        hardware.get_control_messages(auspost.get_user_id()), 0, 0, 1
    )
    hardware.display.show()

    while True:
        # Loop invariant: ! auspost.is_failed()
        # Check for user logout
        if hardware.button0.was_pressed:
            hardware.display.fill(0)
            hardware.oled_display_text(LOGOUT_MESSAGE, 0, 0, 1)
            hardware.display.show()
            sleep_ms(LOGOUT_SUCCESS_DELAY)
            print("<!> END do_everything()")
            return

        update_display_screen(auspost)
        # handle_posture_monitoring(auspost)
        handle_posture_monitoring_new(auspost)
        handle_feedback(auspost)

        sleep_ms(DEBUG_DO_EVERYTHING_INTERVAL)


# 2024-09-13 11-32 Gabe: TESTED.
def update_display_screen(auspost: ControlledData) -> bool:
    """
    Update the display screen with whatever needs to be on there.
    We will display:
        As per HardwareComponents.get_control_messages(), and
        Current-session posture graph

    Args:
        (auspost : ControlledData):
            Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! auspost.is_failed()
    Ensures:
        ! auspost.is_failed()
    """
    print("<!> BEGIN update_display_screen()")

    while (
        not auspost.get_posture_data().empty()
    ):  # NOTE: This is much more robust than getting a fixed number of things out of the queue
        hardware.display.fill(0)
        hardware.oled_display_texts(
            hardware.get_control_messages(auspost.get_user_id()), 0, 0, 1
        )
        hardware.display.updateGraph2D(
            hardware.posture_graph, auspost.get_posture_data().get_nowait()
        )
        hardware.display.show()

    print("<!> END update_display_screen()")
    return True


def handle_posture_monitoring_new(auspost: ControlledData) -> bool:

    # DEBUG:
    print("<!> handle_posture_monitoring_new()")
    # :DEBUG

    now = datetime.now()

    if now > auspost.get_last_snapshot_time() + GET_POSTURE_DATA_TIMEOUT:
        # Get the most recent posture data for the user
        recent_posture_data = get_user_postures(
            auspost.get_user_id(),
            num=-1,
            period_start=now - GET_POSTURE_DATA_TIMEOUT,
            period_end=now,
        )

        # Exit if not enough data
        if len(recent_posture_data) <= POSTURE_GRAPH_DATUM_WIDTH:
            print("<!> Exiting handle_posture_monitoring_new() early: Not enough data")
            # auspost.set_last_snapshot_time(datetime.now())
            return True

        # Exit if not in frame enough
        average_prop_in_frame = sum(
            [posture.prop_in_frame for posture in recent_posture_data]
        ) / len(recent_posture_data)
        if average_prop_in_frame < PROPORTION_IN_FRAME_THRESHOLD:
            print(
                "<!> Exiting handle_posturing_monitoring_new() early: Not in frame for a high enough proportion of time."
            )
            auspost.set_last_snapshot_time(datetime.now())
            return True

        # Sort the list by period_start
        recent_posture_data = sorted(
            recent_posture_data, key=lambda posture: posture.period_start
        )

        # Calculate total time span
        start_time = recent_posture_data[0].period_start
        end_time = recent_posture_data[-1].period_start
        total_time = end_time - start_time

        # Calculate the interval length
        interval = total_time / POSTURE_GRAPH_DATUM_WIDTH

        # Setup a sublist each representing 1 pixel on the graph
        split_posture_lists: list[list[Posture]]
        split_posture_lists = [[] for _ in range(POSTURE_GRAPH_DATUM_WIDTH)]

        # Sublists will be split by period_start
        for posture in recent_posture_data:
            index = min(
                POSTURE_GRAPH_DATUM_WIDTH - 1,
                int((posture.period_start - start_time) // interval),
            )
            split_posture_lists[index].append(posture)

        new_prop_good_data = []
        # Enqueue the average good posture for the graph to use
        for posture_list in split_posture_lists:
            print(f"<!> {posture_list=}")
            average_prop_good = sum(
                [posture.prop_good for posture in posture_list]
            ) / len(posture_list)
            # KILLME:
            # print(f"<!> {average_prop_good=}")
            # auspost.accept_new_posture_data([average_prop_good] * DEBUG_MULTIPLIER_CONSTANT) # DEBUG: 2024-10-06_20-16 Gabe: Fixed the typing by wrapping into a singleton list
            # print(f"<!> Avg prop_good is {average_prop_good}")
            new_prop_good_data += [average_prop_good] * POSTURE_GRAPH_DATUM_WIDTH
        auspost.accept_new_posture_data(new_prop_good_data)

        auspost.set_last_snapshot_time(now)

    return True


# KILLME:
def handle_posture_monitoring(auspost: ControlledData) -> bool:
    """
    Take a snapshot monitoring the user, and update the given ControlledData if necessary.

    Args:
        (auspost : ControlledData): Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! auspost.is_failed()
    Ensures:
        ! auspost.is_failed()

    TODO: Implement error handling
    WARNING: UNTESTED!
    """
    # DEBUG:
    print("<!> handle_posture_monitoring()")
    # :DEBUG
    now = datetime.now()
    if now > auspost.get_last_snapshot_time() + GET_POSTURE_DATA_TIMEOUT:
        # TODO: The ai_bros_get_posture_data() call might fail once it's implemented properly.
        #       If it does, we need to handle it properly.
        auspost.accept_new_posture_data([])
        # DEBUG:
        auspost.accept_new_posture_data([auspost.DEBUG_get_next_posture_graph_value()])
        # :DEBUG
        auspost.set_last_snapshot_time(now)
    return True


def handle_feedback(auspost: ControlledData) -> bool:
    """
    Provide feedback to the user if necessary.

    Args:
        (auspost : ControlledData): Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! auspost.is_failed()
    Ensures:
        ! auspost.is_failed()
    """
    if (
        datetime.now()
        > auspost.get_last_cushion_time() + HANDLE_CUSHION_FEEDBACK_TIMEOUT
    ):
        if not handle_cushion_feedback(auspost):
            return False
    if datetime.now() > auspost.get_last_plant_time() + HANDLE_PLANT_FEEDBACK_TIMEOUT:
        if not handle_plant_feedback(auspost):
            return False
    if datetime.now() > auspost.get_last_sniff_time() + HANDLE_SNIFF_FEEDBACK_TIMEOUT:
        if not handle_sniff_feedback(auspost):
            return False

    return True


## SECTION: Feedback handling


# 2024-09-15_20-18 Gabe: TESTED.
def handle_cushion_feedback(auspost: ControlledData) -> bool:
    """
    Vibrate cushion (if necessary), and update the timestamp of when cushion feedback was last given.

    Args:
        (auspost : ControlledData): Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! auspost.is_failed()
    Ensures:
        ! auspost.is_failed()

    TODO: Implement this method. Currently prints a debug statement and updates the time.
    """
    # DEBUG:
    print("<!> handle_cushion_feedback()")
    # :DEBUG

    # Load posture records within the last HANDLE_CUSHION_FEEDBACK_TIMEOUT
    now = datetime.now()
    recent_posture_data = get_user_postures(
        auspost.get_user_id(),
        num=-1,
        period_start=now - HANDLE_CUSHION_FEEDBACK_TIMEOUT,
        period_end=now,
    )

    # Conditions for exiting early
    # 2024-09-15_19-47 Gabe: TESTED.
    if len(recent_posture_data) == 0:
        print("<!> Exiting handle_cushion_feedback() early: No data")
        auspost.set_last_cushion_time(datetime.now())
        return True
    # 2024-09-15_20-18 Gabe: TESTED.
    average_prop_in_frame = sum(
        [posture.prop_in_frame for posture in recent_posture_data]
    ) / len(recent_posture_data)
    if average_prop_in_frame < PROPORTION_IN_FRAME_THRESHOLD:
        print(
            "<!> Exiting handle_cushion_feedback() early: Not in frame for a high enough proportion of time."
        )
        auspost.set_last_cushion_time(datetime.now())
        return True
    # 2024-09-15_20-18 Gabe: TESTED.
    average_prop_good = sum(
        [posture.prop_good for posture in recent_posture_data]
    ) / len(recent_posture_data)
    if average_prop_good >= CUSHION_PROPORTION_GOOD_THRESHOLD:
        print("<!> Exiting handle_cushion_feedback() early: You sat well :)")
        auspost.set_last_cushion_time(datetime.now())
        return True

    # 2024-09-15_19-40 Gabe: TESTED.
    buzzer_start_time = datetime.now()
    GPIO.output(CUSHION_GPIO_PIN, GPIO.HIGH)
    print("<!> buzzer on")
    while datetime.now() < buzzer_start_time + CUSHION_ACTIVE_INTERVAL:
        # Can add extra code here if necessary. This WILL halt execution of this thread.
        sleep_ms(100)
    GPIO.output(CUSHION_GPIO_PIN, GPIO.LOW)
    print("<!> buzzer off")

    auspost.set_last_cushion_time(datetime.now())
    return True


def handle_plant_feedback(auspost: ControlledData) -> bool:
    """
    Set the plant height according to short-term current session data, and update the timestamp
    of when plant feedback was last given.

    Args:
        (auspost : ControlledData): Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! auspost.is_failed()
    Ensures:
        ! auspost.is_failed()

    TODO: Implement this method. Currently prints a debug statement and updates the time.
    """
    # DEBUG:
    print("<!> handle_plant_feedback()")
    # :DEBUG
    auspost.set_last_plant_time(datetime.now())
    return True


def handle_sniff_feedback(auspost: ControlledData) -> bool:
    """
    Dispense olfactory reward (if necessary), and update the timestamp of when olfactory feedback
    was last given.

    Args:
        (auspost : ControlledData): Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! auspost.is_failed()
    Ensures:
        ! auspost.is_failed()

    TODO: Implement this method. Currently prints a debug statement and updates the time.
    """
    # DEBUG:
    print("<!> handle_sniff_feedback()")
    # :DEBUG
    auspost.set_last_sniff_time(datetime.now())
    return True


def _reset_garden() -> None:
    """Reset data, faces and hardware."""
    print("<!> Burning the garden to the ground...")

    global hardware

    destroy_database()
    print("\t<!> initialising database anew...")
    init_database()
    print("\t<!> resetting face embeddings...")
    reset_registered_face_embeddings()
    print("\t<!> initialising hardware...")
    hardware = initialise_hardware()
    print("\t<!> Like a phoenex, the Sitting Desktop Garden rises anew")


## LAUNCH

if __name__ == "__main__":
    hardware = initialise_hardware()
    main()
