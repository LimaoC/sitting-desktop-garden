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
from PiicoDev_Switch import PiicoDev_Switch
from PiicoDev_SSD1306 import *

from typing import Tuple
import threading

from data_structures import ControlledData, HardwareComponents, Picture, Face
from ai_bros import *



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

    # Top level control flow
    while True:
        wait_for_login_attempt()
        main_data = attempt_login()
        if main_data.is_failed():
            continue
        print("<!> would do_everything() here.")
        sleep_ms(5000) # DEBUG
        #do_everything(main_data)



## SECTION: Hardware initialisation

# 2024-09-01_15-29 Gabe: TESTED. for buttons and OLED display.
def initialise_hardware() -> HardwareComponents:
    """
    Set up hardware for use throughout the project.

    Returns:
        (HardwareComponents): Object consisting of all hardware components connected to the Raspberry Pi.

    TODO: Complete the function with all of the hardware peripherals (incrementally, as they get integrated).
    """
    print("<!> initialise_hardware()") # DEBUG
    return_me = HardwareComponents.make_fresh()
    # Clear button queues
    return_me.button0.was_pressed 
    return_me.button1.was_pressed
    print("<!> initialise_hardware() FINISHED") # DEBUG
    return return_me



## SECTION: Login handling

# 2024-09-01_15-52 Gabe: TESTED.
def wait_for_login_attempt() -> bool:
    """
    Waits until the user attempts to log in.

    Args:
        button0 : PiicoDev_Switch
            Button to wait for press on
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
            return ControlledData.make_empty(create_new_user(picture))
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

def ask_create_new_user() -> bool:
    """
    Ask the user whether they would like to create a new user profile based on the previous picture.

    Returns:
        (bool): True iff the user would like to create a new user profile
    TODO: Make this go out to hardware peripherals. It should have:
        Two buttons (yes / no)
        The LED display ("Unmatched face. Create new user?")
    
    WARNING: UNTESTED!
    """
    # # DEBUG:
    # DEBUG_user_response = False
    # # :DEBUG
    # return DEBUG_user_response
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

def create_new_user(underlying_picture : "UNDERLYING_PICTURE") -> int:
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
    # :DEBUG
    return DEBUG_new_user_id



## SECTION: Control for the logged-in user

def do_everything(uqcs : ControlledData) -> None:
    """
    Main control flow once a user is logged in.

    Args:
        (uqcs : ControlledData): Data encapsulating the current state of the program.
    Requires:
        ! uqcs.is_failed()
    
    TODO: Actually implement this
    """
    # DEBUG:
    DEBUG_user_wants_to_log_out = False
    # :DEBUG

    #logged_in_display()

    while True:
    # Loop invariant: ! uqcs.is_failed()
    # Currently just have Button 0 pressed logout the user
        if hardware.button0.was_pressed:
            return 
        
        # Probably should run individual threads for each of these
        posture_monitoring_thread = threading.Thread(handle_posture_monitoring, args=(uqcs))
        posture_monitoring_thread.start()
        update_display_screen(uqcs)
        handle_posture_monitoring(uqcs)
        handle_feedback(uqcs)

def logged_in_display(uqcs : ControlledData) -> bool:
    """
    Update the display screen with the things that are needed after the user immediately logs in
    TODO: Determine what needs to be on there.

    Args: 
        (uqcs : ControlledData):
            Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! uqcs.is_failed()
    Ensures:
        ! uqcs.is_failed()
    
    TODO: Implement this method. Currently prints a debug statement.
    """

    # draw_text
    # draw_logout_button

    return True

def update_display_screen(uqcs : ControlledData) -> bool:
    """
    Update the display screen with whatever needs to be on there.
    TODO: Determine what needs to be on there.

    Args: 
        (uqcs : ControlledData):
            Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! uqcs.is_failed()
    Ensures:
        ! uqcs.is_failed()
    
    TODO: Implement this method. Currently prints a debug statement.
    """
    # DEBUG:
    print("<!> update_display_screen()")
    # :DEBUG
    return True

def handle_posture_monitoring(uqcs : ControlledData) -> bool:
    """
    Take a snapshot monitoring the user, and update the given ControlledData if necessary.

    Args:
        (uqcs : ControlledData): Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! uqcs.is_failed()
    Ensures:
        ! uqcs.is_failed()
    
    TODO: Implement this method. Currently prints a debug statement.
    """
    # DEBUG:
    print("<!> handle_posture_monitoring()")
    # :DEBUG
    # See Control_flow.pdf for expected control flow
    while True:
        picture = take_picture()
        ai_bros_posture_score()
    return True

def handle_feedback(uqcs : ControlledData) -> bool:
    """
    Provide feedback to the user if necessary.
    
    Args:
        (uqcs : ControlledData): Data encapsulating the current state of the program.
    Returns:
        (bool): True, always. If you get a False return value, then something has gone VERY wrong.
    Requires:
        ! uqcs.is_failed()
    Ensures:
        ! uqcs.is_failed()
    
    TODO: Implement this method. Currently prints a debug statement.
    """
    # DEBUG:
    print("<!> handle_feedback()")
    # :DEBUG
    # See Control_flow.pdf for expected control flow
    return True



## LAUNCH

if __name__ == "__main__":
    main()
