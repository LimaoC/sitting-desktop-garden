"""
Brief:
    Entry point for the Sitting Desktop Garden Raspberry Pi Pot Client.
File:
    sitting-desktop-garden/client/drivers/main.py
Author:
    Gabriel Field (47484306)
"""

## SECTION: Imports

from PiicoDev_Switch import PiicoDev_Switch
#from PiicoDev_Unified import sleep_ms

from drivers.data_structures import ControlledData, HardwareComponents, Picture, Face



## SECTION: main()

def main():
    """
    Entry point for the control program.
    """
    # DEBUG:
    print("<!> main()")
    # :DEBUG

    hardware = initialise_hardware()

    # Top level control flow
    while True:
        wait_for_login_attempt(hardware.get_button(0))
        main_data = attempt_login()
        if main_data.is_failed():
            continue
        do_everything(main_data)



## SECTION: Hardware initialisation

def initialise_hardware():
    """
    Set up hardware for use throughout the project.

    Returns:
        (HardwareComponents): Object consisting of all hardware components connected to the Raspberry Pi.

    TODO: Complete the function with all of the hardware peripherals (incrementally, as they get integrated).
    WARNING: UNTESTED!
    """
    # DEBUG:
    print("<!> initialise_hardware()")
    # :DEBUG
    return HardwareComponents.make_fresh()



## SECTION: Login handling

def wait_for_login_attempt(button0 : PiicoDev_Switch) -> bool:
    """
    Waits until the user attempts to log in.

    Args:
        button0 : PiicoDev_Switch
            Button to wait for press on
    Returns:
        (bool): True when the user attempts to log in.
    
    WARNING: UNTESTED!
    """
    # DEBUG:
    print("<!> BEGIN wait_for_login_attempt()")
    # :DEBUG

    while True:
        if button0.was_pressed:
            print("<!> END wait_for_login_attempt()") # DEBUG
            return True

def attempt_login() -> ControlledData:
    """
    Attempts to log in.

    Returns:
        (ControlledData): which is:
            FAILED                 if the login is unsuccessful
            EMPTY (but not failed) if the login is successful

    TODO: Actually write this function. Currently prints a debug message.
    """
    # # DEBUG:
    # print("<!> attempt_login()")
    # DEBUG_login_success = True
    # DEBUG_default_user_id = "play-user"
    # # :DEBUG
    # if DEBUG_login_success:
    #     return ControlledData.make_empty(DEBUG_default_user_id)
    # else:
    #     return ControlledData.make_failed()
    
    while True:
        picture = take_picture()
        if picture.is_failed():
            continue
        face = ai_bros_face_recogniser(picture.underlying_picture) # TODO: This should be an external API call.
        if face.is_failed():
            continue
        if face.is_matched():
            return ControlledData.make_empty(face.get_user_id())
        if not ask_create_new_user():
            continue
        new_user_id = create_new_user(picture.underlying_picture)
        return ControlledData.make_empty(new_user_id)
        

def take_picture() -> Picture:
    """
    Takes a picture from the camera, and returns a (failable) picture object.

    TODO: Actually write this function. Currently prints a debug message and returns a failed picture.
    """
    # DEBUG:
    print("<!> take_picture()")
    DEBUG_return_value = Picture.make_failed()
    # :DEBUG
    return DEBUG_return_value

def ai_bros_face_recogniser(underlying_picture : "UNDERLYING_PICTURE") -> Face:
    """
    Recognise a face, powered by AI.

    Args:
        underlying_picture : UNDERLYING_PICTURE
            The picture to pass to the face recogniser. This data passing may be handled differently
            in the final version.
    Returns:
        (Face): Failed, matched or unmatched Face
    TODO: Convert this into an external API call. Currently returns debug data.
    """
    # DEBUG:
    print("<!> ai_bros_face_recogniser()")
    DEBUG_failed = False
    DEBUG_matched = True
    DEBUG_user_id = 0
    # :DEBUG
    if DEBUG_failed:
        return Face.make_failed()
    if not DEBUG_matched:
        return Face.make_unmatched()
    return Face.make_matched(DEBUG_user_id)

def ask_create_new_user() -> bool:
    """
    Ask the user whether they would like to create a new user profile based on the previous picture.

    Returns:
        (bool): True iff the user would like to create a new user profile
    TODO: Make this go out to hardware peripherals. It should have:
        Two buttons (yes / no)
        The LED display ("Unmatched face. Create new user?")
    """
    # DEBUG:
    DEBUG_user_response = False
    # :DEBUG
    return DEBUG_user_response

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
    while True:
    # Loop invariant: ! uqcs.is_failed()
        if DEBUG_user_wants_to_log_out:
            return
        update_display_screen(uqcs)
        handle_posture_monitoring(uqcs)
        handle_feedback(uqcs)

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
