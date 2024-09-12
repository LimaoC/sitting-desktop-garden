## SECTION: Imports

from typing import Tuple
from PiicoDev_Switch import PiicoDev_Switch
from PiicoDev_SSD1306 import *
import threading
from datetime import datetime
from client.data.routines import *
from models.face_rec.routines import get_user_from_face

#from PiicoDev_Unified import sleep_ms

from data_structures import ControlledData, HardwareComponents, Picture, Face


def ai_bros_face_recogniser(underlying_picture : int) -> Face: # TODO: Refine type signature
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
    DEBUG_unmatched = None
    DEBUG_user_id = -42

    try:
        returned_user = get_user_from_face(underlying_picture)
    except NotImplementedError:
        returned_user = -1
    #returned_user = DEBUG_unmatched

    # :DEBUG
    if DEBUG_failed:
        return Face.make_failed()
    if returned_user is None:
        return Face.make_unmatched()
    #return Face.make_matched(DEBUG_user_id.id_)
    return Face.make_matched(returned_user.id_)

def ai_bros_posture_score(underlying_picture : "UNDERLYING_PICTURE") -> int: # TODO: Refine type signature
    """
    Args:
        underlying_picture : UNDERLYING_PICTURE
            The picture of the person's posture
    Returns:
        int: score representing how good the posture currently is???
    TODO: Convert this into an external API call. Currently returns debug data.
    NOTE: This will eventually be a database lookup. We're running the AI posture peeker
          asynchronously to the controller code.
    FIXME: This documentation is terrible
    """
    return 1

def ai_bros_get_posture_data(last_snapshot_time : datetime) -> "POSTURE_DATA": # TODO: Refine type signature
    """
    API call to get posture data from the SQLite database.
    Gets all data from after last_snapshot_time until the current time.
    
    Args:
        last_snapshot_time : datetime
            The last time we read the posture data.
    
    Returns:
        (POSTURE_DATA): Posture data returned from the API call.
    
    TODO: Actually implement this method. Currently prints a debug method and returns an empty list.
    """
    # DEBUG:
    print("<!> ai_bros_get_posture_data()")
    DEBUG_return_value = []
    # :DEBUG
    return DEBUG_return_value
