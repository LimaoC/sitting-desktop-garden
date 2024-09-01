## SECTION: Imports

from typing import Tuple
from PiicoDev_Switch import PiicoDev_Switch
from PiicoDev_SSD1306 import *
import threading

#from PiicoDev_Unified import sleep_ms

from data_structures import ControlledData, HardwareComponents, Picture, Face


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
    DEBUG_failed = True
    DEBUG_matched = False
    DEBUG_user_id = 0
    # :DEBUG
    if DEBUG_failed:
        return Face.make_failed()
    if not DEBUG_matched:
        return Face.make_unmatched()
    return Face.make_matched(DEBUG_user_id)

def ai_bros_posture_score(underlying_picture : "UNDERLYING_PICTURE") -> int:
    """
    Args:
        underlying_picture : UNDERLYING_PICTURE
            The picture of the person's posture
    Returns:
        int: score represtning how good the posture currently is???
    TODO: Convert this into an external API call. Currently returns debug data.
    NOTE: This will eventually be a database lookup. We're running the AI posture peeker
          asynchronously to the controller code.
    """
    return 1
