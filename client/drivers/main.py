"""
Brief:
    Entry point for the Sitting Desktop Garden Raspberry Pi Pot Client.
File:
    sitting-desktop-garden/client/drivers/main.py
Author:
    Gabriel Field (47484306)
"""

## SECTION: Imports

from PiicoDev_Unified import sleep_ms
from PiicoDev_Switch import *
from PiicoDev_SSD1306 import *

import RPi.GPIO as GPIO

from typing import Tuple
import threading
from datetime import datetime, timedelta

from data_structures import ControlledData, HardwareComponents, Picture, Face
from ai_bros import *
from data.routines import *



## SECTION: Global constants

""" Number of milliseconds between each time the button is polled during wait_for_login_attempt(). """
WAIT_FOR_LOGIN_POLLING_INTERVAL = 100
""" Number of milliseconds between pictures taken for login attempts. """
LOGIN_TAKE_PICTURE_INTERVAL = 1000
""" Number of milliseconds between starting to attempt_login() and taking the first picture. """
START_LOGIN_ATTEMPTS_DELAY = 3000
""" Number of milliseconds between each time the button is polled during ask_create_new_user(). """
ASK_CREATE_NEW_USER_POLLING_INTERVAL = 100
""" Number of milliseconds between telling the user that login has completely failed and returning from attempt_login(). """
FAIL_LOGIN_DELAY = 3000
""" Number of milliseconds between telling the user that login has succeeded and beginning real functionality. """
LOGIN_SUCCESS_DELAY = 3000
""" Number of milliseconds between the user successfully logging out and returning to main(). """
LOGOUT_SUCCESS_DELAY = 3000
""" Minimum delay between reading posture data from the SQLite database, in do_everything(). """
GET_POSTURE_DATA_TIMEOUT = timedelta(milliseconds = 2000) # DEBUG: Change this value up to ~60000 later.
""" Minimum delay between consecutive uses of the vibration motor. Used in handle_feedback(). """
HANDLE_CUSHION_FEEDBACK_TIMEOUT = timedelta(milliseconds = 5000)
""" Length of time for which the vibration motor should vibrate. Used in handle_cushion_feedback(). """
CUSHION_ACTIVE_INTERVAL = timedelta(milliseconds=1000)
""" Minimum delay between consecutive uses of the plant-controlling servos. Used in handle_feedback(). """
HANDLE_PLANT_FEEDBACK_TIMEOUT = timedelta(milliseconds = 10000)
""" Minimum delay between consecutive uses of the scent bottle-controlling servos. Used in handle_feedback(). """
HANDLE_SNIFF_FEEDBACK_TIMEOUT = timedelta(milliseconds = 20000)
""" DEBUG Number of milliseconds between each loop iteration in do_everything(). """
DEBUG_DO_EVERYTHING_INTERVAL = 1000



## SECTION: main()

def main():
    """
    Entry point for the control program.
    """
    # DEBUG:
    print("<!> main()")
    # :DEBUG

    global hardware 
    hardware = initialise_hardware()

    init_database()

    # Top level control flow
    while True:
        wait_for_login_attempt()
        main_data = attempt_login()
        if main_data.is_failed():
            continue
        print("<!> main(): Successful login")
        do_everything(main_data)



## SECTION: Hardware initialisation

# 2024-09-01_15-29 Gabe: TESTED. for buttons and OLED display.
def initialise_hardware() -> HardwareComponents:
    """
    Set up hardware for use throughout the project. We have:
        button0 with address switches [0, 0, 0, 0]
        button1 with address switches [0, 0, 0, 1]
        OLED display with address switch off
        Vibration motor attached to GPIO pin 8 (which is D8 on the PiicoDev header)

    Returns:
        (HardwareComponents): Object consisting of all hardware components connected to the Raspberry Pi.

    TODO: Complete the function with all of the hardware peripherals (incrementally, as they get integrated).
    """
    print("<!> initialise_hardware()") # DEBUG
    return_me = HardwareComponents.make_fresh()
    # Clear button queues
    return_me.button0.was_pressed 
    return_me.button1.was_pressed
    # Set up GPIO pins
    GPIO.setmode(GPIO.BCM) # use pin numbering convention as per the PiicoDev header
    # Set data directions
    GPIO.setup(8, GPIO.OUT)

    print("<!> initialise_hardware() FINISHED") # DEBUG
    return return_me



## SECTION: Login handling

# 2024-09-01_15-52 Gabe: TESTED.
def wait_for_login_attempt() -> bool:
    """
    Waits until the user attempts to log in.

    Returns:
        (bool): True when the user attempts to log in.    
    """
    print("<!> BEGIN wait_for_login_attempt()")

    WAIT_FOR_LOGIN_OLED_MESSAGE = "Press button0 to log in!"
    # Display to screen
    hardware.display.fill(0)
    hardware.oled_display_text(WAIT_FOR_LOGIN_OLED_MESSAGE, 0, 0, 1)
    hardware.display.show()
    # Clear button queue
    hardware.button0.was_pressed

    while True:
        if hardware.button0.was_pressed:
            # Clear the display
            hardware.display.fill(0)
            hardware.display.show()
            print("<!> END wait_for_login_attempt()") # DEBUG
            return True
        sleep_ms(WAIT_FOR_LOGIN_POLLING_INTERVAL)

# 2024-09-01 17:06 Gabe: TESTED., assuming ai_bros_face_recogniser() does what it should do.
def attempt_login() -> ControlledData:
    """
    Attempts to log in.

    Returns:
        (ControlledData): which is:
            FAILED                 if the login is unsuccessful
            EMPTY (but not failed) if the login is successful
    """

    # TODO: Finalise these messages
    SMILE_FOR_CAMERA_MESSAGE = "LIS: Smile for the camera!"
    PICTURE_FAILED_MESSAGE = "LIS: Picture failed T-T"
    AI_FAILED_MESSAGE = "LIS: Failed to determine user T-T"
    LOGIN_TOTALLY_FAILED_MESSAGE = "LIS: Failed to log in T-T"

    hardware.display.fill(0)
    hardware.oled_display_text(SMILE_FOR_CAMERA_MESSAGE, 0, 0, 1)
    hardware.display.show()
    sleep_ms(START_LOGIN_ATTEMPTS_DELAY)

    while True:
        hardware.display.fill(0)
        hardware.oled_display_text(SMILE_FOR_CAMERA_MESSAGE, 0, 0, 1)
        hardware.display.show()
        picture = take_picture()
        if picture.failed:
            print('<!> Picture Failed') # DEBUG
            hardware.display.fill(0)
            hardware.oled_display_text(PICTURE_FAILED_MESSAGE, 0, 0, 1)
            hardware.display.show()
            sleep_ms(LOGIN_TAKE_PICTURE_INTERVAL)
            continue
        face = ai_bros_face_recogniser(picture.underlying_picture) # TODO: This should be an external API call.
        if face.failed:
            print("<!> AI has failed us") # DEBUG
            hardware.display.fill(0)
            hardware.oled_display_text(AI_FAILED_MESSAGE, 0, 0, 1)
            hardware.display.show()
            sleep_ms(LOGIN_TAKE_PICTURE_INTERVAL)
            continue
        if face.matched:
            print("<!> Mega W for AI") # DEBUG
            return ControlledData.make_empty(face.user_id)
        elif ask_create_new_user():
            return ControlledData.make_empty(create_new_user(picture.underlying_picture))
        # Tell the user the login failed
        print("<!> attempt_login(): Totally failed lol") # DEBUG
        hardware.display.fill(0)
        hardware.oled_display_text(LOGIN_TOTALLY_FAILED_MESSAGE, 0, 0, 1)
        hardware.display.show()
        sleep_ms(FAIL_LOGIN_DELAY)
        return ControlledData.make_failed()  

def take_picture() -> Picture:
    """
    Takes a picture from the camera, and returns a (failable) picture object.

    TODO: Actually write this function. Currently prints a debug message and returns a failed picture.
    """
    # DEBUG:
    print("<!> take_picture()")
    DEBUG_return_value = Picture.make_valid("DEBUG_picture_goes_here")
    # :DEBUG
    return DEBUG_return_value

# 2024-09-01 17:06 Gabe: TESTED.
def ask_create_new_user() -> bool:
    """
    Ask the user whether they would like to create a new user profile based on the previous picture.

    Returns:
        (bool): True iff the user would like to create a new user profile
    TODO: Make this go out to hardware peripherals. It should have:
        Two buttons (yes / no)
        The LED display ("Unmatched face. Create new user?")
    """
    print("<!> BEGIN ask_create_new_user()")

    CREATE_NEW_USER_MESSAGES = ["No face matched.", "Create new user?", "button0: no", "button1: yes"]
    # Display to screen
    hardware.display.fill(0)
    hardware.oled_display_texts(CREATE_NEW_USER_MESSAGES, 0, 0, 1)
    hardware.display.show()
    # Clear button queue
    hardware.button0.was_pressed
    hardware.button1.was_pressed

    while True:
        if hardware.button0.was_pressed:
            # Clear the display
            hardware.display.fill(0)
            hardware.display.show()
            print("<!> END ask_create_new_user(): do NOT create new user") # DEBUG
            return False
        if hardware.button1.was_pressed:
            # Clear the display
            hardware.display.fill(0)
            hardware.display.show()
            print("<!> END ask_create_new_user(): DO create new user") # DEBUG
            return True
        sleep_ms(ASK_CREATE_NEW_USER_POLLING_INTERVAL)

def create_new_user(underlying_picture : int) -> int:
    """
    Create a new user based on the given picture, and return their user id.

    Args:
        underlying_picture : UNDERLYING_PICTURE
            Picture to associate with the new user profile
    Returns:
        (int): The new user's user id
    TODO: Actually write to the local SQLite database, and properly determine the new user id.
    """
    # DEBUG:
    DEBUG_new_user_id = 0
    # new_user_id = create_user()
    # try:
    #     register_faces(new_user_id, [underlying_picture])
    # except NotImplementedError:
    #     pass
    # :DEBUG
    return DEBUG_new_user_id
    # return new_user_id # DEBUG



## SECTION: Control for the logged-in user

# 2024-09-02 07-03 Gabe: Currently working the following here:
#   top-level control flow
#   interaction with buttons and display
def do_everything(auspost : ControlledData) -> None:
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
    # Clear display
    hardware.display.fill(0)
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
        
        # Probably should run individual threads for each of these
        # TODO: Move the threading to a more reasonable location. main() is probably best.
        # posture_monitoring_thread = threading.Thread(handle_posture_monitoring, args=(auspost))
        # posture_monitoring_thread.start()

        update_display_screen(auspost)
        handle_posture_monitoring(auspost)
        handle_feedback(auspost)

        sleep_ms(DEBUG_DO_EVERYTHING_INTERVAL)

# 2024-09-13 11-32 Gabe: TESTED.
def update_display_screen(auspost : ControlledData) -> bool:
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

    hardware.display.fill(0)
    hardware.oled_display_texts(hardware.get_control_messages(auspost.get_user_id()), 0, 0, 1)
    if not auspost.get_posture_data().empty():
        hardware.display.updateGraph2D(hardware.posture_graph, auspost.get_posture_data().get_nowait())
    # Render
    hardware.display.show()

    print("<!> END update_display_screen()")
    return True

def handle_posture_monitoring(auspost : ControlledData) -> bool:
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
    if (now > auspost.get_last_snapshot_time() + GET_POSTURE_DATA_TIMEOUT):
        # TODO: The ai_bros_get_posture_data() call might fail once it's implemented properly.
        #       If it does, we need to handle it properly.
        auspost.accept_new_posture_data(ai_bros_get_posture_data(auspost.get_last_snapshot_time()))
        # DEBUG:
        auspost.accept_new_posture_data([auspost.DEBUG_get_next_posture_graph_value()])
        # :DEBUG
        auspost.set_last_snapshot_time(now)
    return True

def handle_feedback(auspost : ControlledData) -> bool:
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
    if (datetime.now() > auspost.get_last_cushion_time() + HANDLE_CUSHION_FEEDBACK_TIMEOUT):
        if not handle_cushion_feedback(auspost):
            return False
    if (datetime.now() > auspost.get_last_plant_time() + HANDLE_PLANT_FEEDBACK_TIMEOUT):
        if not handle_plant_feedback(auspost):
            return False
    if (datetime.now() > auspost.get_last_sniff_time() + HANDLE_SNIFF_FEEDBACK_TIMEOUT):
        if not handle_sniff_feedback(auspost):
            return False
    
    return True



## SECTION: Feedback handling

def handle_cushion_feedback(auspost : ControlledData) -> bool:
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
    DEBUG_should_vibrate = True
    # :DEBUG

    # Control flow:
    #   Load posture records within the last HANDLE_CUSHION_FEEDBACK_TIMEOUT.
    #   If we don't have any data to go off, return True* immediately
    #   If the data we have to go off sees an average prop_in_frame < PROPORTION_IN_FRAME_THRESHOLD,
    #       return True immediately
    #   If the data we have to go off sees an average prop_good < PROPORTION_GOOD_POSTURE_THRESHOLD,
    #       Vibrate the buzzer for CUSHION_ACTIVE_INTERVAL time
    #       return True
    #   return True
    # *all of these `return True`s should `auspost.set_last_cushion_time(datetime.now())` first.
    # For now, just:
    #   Vibrate the buzzer for CUSHION_ACTIVE_INTERVAL time
    #   return True
    
    # TESTING::
    if DEBUG_should_vibrate:
        buzzer_start_time = datetime.now()
        GPIO.output(8, GPIO.HIGH)
        print("<!> buzzer on")
        while datetime.now() < buzzer_start_time + CUSHION_ACTIVE_INTERVAL:
            # Can add extra code here if necessary. This WILL halt execution of this thread.
            sleep_ms(100)
        GPIO.output(8, GPIO.LOW)
        print("<!> buzzer off")
    # ::TESTING

    auspost.set_last_cushion_time(datetime.now())
    return True

def handle_plant_feedback(auspost : ControlledData) -> bool:
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

def handle_sniff_feedback(auspost : ControlledData) -> bool:
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



## LAUNCH

if __name__ == "__main__":
    main()
