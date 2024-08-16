"""
Entry point for the Sitting Desktop Garden Raspberry Pi Pot Client.
@file sitting-desktop-garden/client/drivers/main.py
@author Gabriel Field (47484306)
"""

from data_structures import ControlledData

## SECTION: main()

def main():
    # DEBUG:
    print("<!> main()")
    # :DEBUG

    initialise_hardware()

    # Top level control flow
    while True:
        wait_for_login_attempt()
        main_data = attempt_login()
        if main_data.is_failed():
            continue
        do_everything(main_data)



## SECTION: Hardware initialisation

def initialise_hardware():
    """
    Set up hardware for use throughout the project.
    TODO: Actually write this function. Currently does nothing.
    """
    # DEBUG:
    print("<!> initialise_hardware()")
    # :DEBUG



## SECTION: Login handling

def wait_for_login_attempt() -> bool:
    """
    Waits until the user attempts to log in.
    @returns True when the user attempts to log in.
    TODO: Actually write this function. Currently prints a debug message and instantly returns.
    """
    # DEBUG:
    print("<!> wait_for_login_attempt()")
    # :DEBUG
    return True
    # See Control_flow.pdf for expected control flow

def attempt_login() -> ControlledData:
    """
    Attempts to log in.
    @returns ControlledData, which is:
        FAILED                 if the login is unsuccessful
        EMPTY (but not failed) if the login is successful
    TODO: Actually write this function. Currently prints a debug message.
    """
    # DEBUG:
    print("<!> attempt_login()")
    DEBUG_login_success = False
    DEBUG_default_user_id = "shitpost"
    # :DEBUG
    if DEBUG_login_success:
        return ControlledData.make_empty(DEBUG_default_user_id)
    else:
        return ControlledData.make_failed()
    # See Control_flow.pdf for expected control flow



## SECTION: Control for the logged-in user

def do_everything(uqcs : ControlledData) -> None:
    """
    Main control flow once a user is logged in.
    @param uqcs : ControlledData
        Data encapsulating the current state of the program.
    @requires ! uqcs.is_failed()
    @returns None
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
    @param uqcs : ControlledData
        Data encapsulating the current state of the program.
    @returns True, always. If you get a False return value, then something has gone VERY wrong.
    @requires ! uqcs.is_failed()
    @ensures  ! uqcs.is_failed()
    TODO: Implement this method. Currently prints a debug statement.
    """
    # DEBUG:
    print("<!> update_display_screen()")
    # :DEBUG
    return True

def handle_posture_monitoring(uqcs : ControlledData) -> bool:
    """
    Take a snapshot monitoring the user, and update the given ControlledData if necessary.
    @param uqcs : ControlledData
        Data encapsulating the current state of the program.
    @returns True, always. If you get a False return value, then something has gone VERY wrong.
    @requires ! uqcs.is_failed()
    @ensures  ! uqcs.is_failed()
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
    @param uqcs : ControlledData
        Data encapsulating the current state of the program.
    @returns True, always. If you get a False return value, then something has gone VERY wrong.
    @requires ! uqcs.is_failed()
    @ensures  ! uqcs.is_failed()
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
