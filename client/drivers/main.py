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
""" Number of milliseconds between telling the user that login has succeeded and beginning real functionality. """
LOGIN_SUCCESS_DELAY = 3000
""" Number of milliseconds between the user successfully logging out and returning to main(). """
LOGOUT_SUCCESS_DELAY = 3000
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

# 2024-09-02 07-03 Gabe: Currently working the following here:
#   top-level control flow
#   interaction with buttons and display
def do_everything(uqcs : ControlledData) -> None:
    """
    Main control flow once a user is logged in.

    Args:
        (uqcs : ControlledData): Data encapsulating the current state of the program.
    Requires:
        ! uqcs.is_failed()
    
    TODO: Actually implement this
    """
    print("<!> BEGIN do_everything()")

    LOGIN_MESSAGE = "Logged in with user id: " + str(uqcs.get_user_id())
    LOGOUT_MESSAGE = "Logged out user id " + str(uqcs.get_user_id())

    # Display message to user
    hardware.display.fill(0)
    hardware.oled_display_text(LOGIN_MESSAGE, 0, 0, 1)
    hardware.display.show()
    sleep_ms(LOGIN_SUCCESS_DELAY)
    
    # Clear button queues
    hardware.button0.was_pressed
    hardware.button1.was_pressed

    while True:
    # Loop invariant: ! uqcs.is_failed()
        # Check for user actions
        if hardware.button0.was_pressed:
            hardware.display.fill(0)
            hardware.oled_display_text(LOGOUT_MESSAGE, 0, 0, 1)
            hardware.display.show()
            sleep_ms(LOGOUT_SUCCESS_DELAY)
            print("<!> END do_everything()")
            return 
        
        # Probably should run individual threads for each of these
        # TODO: Move the threading to a more reasonable location. main() is probably best.
        # posture_monitoring_thread = threading.Thread(handle_posture_monitoring, args=(uqcs))
        # posture_monitoring_thread.start()

        # DEBUG:
        update_display_screen(uqcs)
        # handle_posture_monitoring(uqcs)
        # handle_feedback(uqcs)
        # :DEBUG

        sleep_ms(DEBUG_DO_EVERYTHING_INTERVAL)

# 2024-09-02 07:21 Gabe: Don't think we need this method anymore
# def logged_in_display(uqcs : ControlledData) -> bool:
#     """
#     Update the display screen with the things that are needed after the user immediately logs in
#     TODO: Determine what needs to be on there.

#     Args: 
#         (uqcs : ControlledData):
#             Data encapsulating the current state of the program.
#     Returns:
#         (bool): True, always. If you get a False return value, then something has gone VERY wrong.
#     Requires:
#         ! uqcs.is_failed()
#     Ensures:
#         ! uqcs.is_failed()
    
#     TODO: Implement this method. Currently prints a debug statement.
#     """

#     # draw_text
#     # draw_logout_button

#     return True

def update_display_screen(uqcs : ControlledData) -> bool:
    """
    Update the display screen with whatever needs to be on there.
    We will display:
        User id (top row)
        Current-session posture graph
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
    print("<!> BEGIN update_display_screen()")

    CONTROL_MESSAGES = ["b0: logout", "id: " + str(uqcs.get_user_id())]
    GRAPH_MIN_VALUE = 0
    GRAPH_MAX_VALUE = 60    # TODO: 2024-09-02 07-53 Gabe:
                            #       This needs to be a real value for the underlying data that we expect to be shown. 
                            #       From memory, this is probably `60` for "number of the last 60 seconds spent sitting well"
    
    from math import sin, pi
    DEBUG_DISPLAY_THIS_GRAPH = [30 * (1 + sin(2 * pi * x / WIDTH)) for x in range(WIDTH)]

    hardware.display.fill(0)
    next_line_y = hardware.oled_display_texts(CONTROL_MESSAGES, 0, 0, 1)
    posture_graph = hardware.display.graph2D(
        originX = 0, originY = HEIGHT - 1, 
        width = WIDTH, height = HEIGHT - next_line_y, 
        minValue = GRAPH_MIN_VALUE, maxValue = GRAPH_MAX_VALUE, 
        c = 1, bars = False
    )
    # FIXME: 2024-09-02 07-58 Gabe: 
    #   This is shit and terrible!!
    #   It also doesn't work!
    #   We should be holding a PiicoDev_SSD1306.graph2D in uqcs,
    #    and simply updating that member field here.
    #   We shouldn't be creating a whole new graph2D object every time
    #    we want to draw to the same graph!!!
    for y in DEBUG_DISPLAY_THIS_GRAPH:
        hardware.display.updateGraph2D(posture_graph, y)
    hardware.display.show()
    print("<!> END update_display_screen()")
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
