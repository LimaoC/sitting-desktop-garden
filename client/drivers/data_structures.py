"""
Brief:
    Data structures for use on the RPi Client.
File:
    sitting-desktop-garden/client/drivers/data_structures.py
Author:
    Gabriel Field (47484306)
"""

## SECTION: Imports

from PiicoDev_Switch import PiicoDev_Switch
from PiicoDev_SSD1306 import *

from datetime import datetime



## SECTION: Constants

""" Sentinel value for an invalid user. """
EMPTY_USER_ID = -1

EMPTY_POSTURE_DATA = None # TODO: Refine to a legal term, once the type is figured out



## SECTION: ControlledData

class ControlledData:
    """
    Data for passing around in client/drivers/main.do_everything().

    There should only ever be one object of this class at a time.

    Member fields:
        self._failed : bool                           
            True if this data is incomplete.
        self._user_id : int
            ID of current user.
        self._posture_data : (TODO: figure out this type)   
            Data updated through ML models, used for feedback.
        self._last_snapshot_time : datetime.datetime
            Time of the last successful pose estimation.
        self._last_cushion_time : datetime.datetime
            Time of the last successful cushion feedback event.
        self._last_plant_time : datetime.datetime
            Time of the last successful plant feedback event.
        self._last_sniff_time : datetime.datetime
            Time of the last successful scent feedback event.

    Class invariant:
        self._failed ==> (all other variables are default values)
    """

    # SECTION: Constructors

    def __init__(self):
        """
        DO NOT USE THIS CONSTRUCTOR! Call ControlledData.make_empty() or ControlledData.make_failed() instead.
        """
        self._failed             = True
        self._user_id            = EMPTY_USER_ID
        self._posture_data       = EMPTY_POSTURE_DATA
        self._last_snapshot_time = datetime.now()
        self._last_cushion_time  = datetime.now()
        self._last_plant_time    = datetime.now()
        self._last_sniff_time    = datetime.now()

    @classmethod
    def make_empty(cls, user_id : int) -> "ControlledData":
        """
        Construct a non-failed object of this class, with a provided user ID and empty posture data.
        
        Returns:
            (ControlledData): An object of this class that is not failed, with legal user ID and empty posture data.
        """
        return_me = ControlledData()
        return_me._failed             = False
        return_me._user_id            = user_id
        return_me._posture_data       = EMPTY_POSTURE_DATA
        return_me._last_snapshot_time = datetime.now()
        return_me._last_cushion_time  = datetime.now()
        return_me._last_plant_time    = datetime.now()
        return_me._last_sniff_time    = datetime.now()
        return return_me

    @classmethod
    def make_failed(cls) -> "ControlledData":
        """
        Construct a failed object of this class.
        
        Returns:
            (ControlledData): An object of this class that is failed.
        """
        return_me = ControlledData()
        return_me._failed             = True
        return_me._user_id            = EMPTY_USER_ID
        return_me._posture_data       = EMPTY_POSTURE_DATA
        return_me._last_snapshot_time = datetime.now()
        return_me._last_cushion_time  = datetime.now()
        return_me._last_plant_time    = datetime.now()
        return_me._last_sniff_time    = datetime.now()
        return return_me

    # SECTION: Getters/Setters

    def is_failed(self) -> bool:
        """
        Returns:
            (bool): True iff this ControlledData is failed.
        """
        return self._failed
    
    def get_user_id(self) -> int:
        """
        Returns:
            (int): The user id of this ControlledData.
        """
        return self._user_id

    def get_posture_data(self) -> "POSTURE_DATA": # TODO: Refine type signature
        """
        Returns:
            (POSTURE_DATA): The posture data stored in this ControlledData
        """
        return self._posture_data

    # SECTION: Posture data mapping
    
    def get_cushion_posture_data(self) -> "CUSHION_POSTURE_DATA": # TODO: Decide what this type looks like
        """
        Returns:
            (CUSHION_POSTURE_DATA): Posture data necessary for cushion feedback.
        TODO: Implement this.
        """
        # DEBUG:
        print("<!> WARNING: get_cushion_posture_data() not implemented!")
        # :DEBUG
        return None

    def get_plant_posture_data(self) -> "PLANT_POSTURE_DATA": # TODO: Decide what this type looks like
        """
        Returns:
            (PLANT_POSTURE_DATA) Posture data necessary for plant feedback.
        TODO: Implement this.
        """
        # DEBUG:
        print("<!> WARNING: get_plant_posture_data() not implemented!")
        # :DEBUG
        return None
    
    def get_sniff_posture_data(self) -> "SNIFF_POSTURE_DATA": # TODO: Decide what this type looks like
        """
        Returns:
            (SNIFF_POSTURE_DATA): Posture data necessary for scent feedback.
        TODO: Implement this.
        """
        # DEBUG:
        print("<!> WARNING: get_sniff_posture_data() not implemented!")
        # :DEBUG
        return None



## SECTION: Hardware packaged together

class HardwareComponents:
    """
    Hardware components packaged together into a class.

    Member fields:
        self.button0 : PiicoDev_Switch
            A button with address switches set to [0, 0, 0, 0]
        self.button1 : PiicoDev_Switch
            A button with address switches set to [0, 0, 0, 1]
        self._display : [(PiicoDev_SSD1306_MicroBit | PiicoDev_SSD1306_Linux | PiicoDev_SSD1306_MicroPython)]
            OLED SSD1306 Display 
    """

    # SECTION: Constructors
    
    @classmethod
    def make_fresh(cls):
        """
        Create a new instance of HardwareComponents, set up according to the hardware that we expect
        to be plugged in.
        """
        DOUBLE_PRESS_DURATION = 400 # Milliseconds
        return HardwareComponents(
            PiicoDev_Switch(id = [0, 0, 0, 0], double_press_duration = DOUBLE_PRESS_DURATION),
            PiicoDev_Switch(id = [0, 0, 0, 1], double_press_duration = DOUBLE_PRESS_DURATION),
            create_PiicoDev_SSD1306() # This is the constructor; ignore the "is not defined" error message.
        )

    def __init__(self, button0, button1, display):
        self.button0: PiicoDev_Switch = button0 
        self.button1: PiicoDev_Switch = button1
        self.display: PiicoDev_SSD1306_MicroPython = display
    
    # SECTION: Using peripherals

    def oled_display_text(self, text : str, x : int, y : int, colour : int) -> None:
        """
        Display text on the oled display, wrapping lines if necessary.
        NOTE: Does not blank display. Call `.display.fill(0)` if needed.
        NOTE: Does not render. Call `.display.show()` if needed.

        Args:
            text : str
                String to write to the OLED display
            x : int
                Horizontal coordinate from left side of screen.
            y : int
                Vertical coordinate from top side of screen.
            colour : int
                0: black
                1: white
        """
        LINE_HEIGHT = 15 # pixels
        LINE_WIDTH = 16 # characters
        chunks = [text[i : i + LINE_WIDTH] for i in range(0, len(text), LINE_WIDTH)]
        for (index, chunk) in enumerate(chunks):
            self.display.text(chunk, x, y + index * LINE_HEIGHT, colour)



## SECTION: Picture

class Picture:
    """
    A picture, which may have failed.

    Member fields:
        self.failed : bool
            True iff this picture is incomplete.
        self.underlying_picture : (TODO: Figure out this type!)
            The picture encoded by this object.
    """

    def __init__(self) -> "Picture":
        self.failed : bool = True
        self.underlying_picture : "UNDERLYING_PICTURE" = None

    @classmethod
    def make_failed(cls) -> "Picture":
        """
        Make a failed Picture.
        """
        return_me = Picture()
        return_me.failed = True
        return_me.underlying_picture = None
        return return_me
    
    @classmethod
    def make_valid(cls, underlying_picture : "UNDERLYING_PICTURE") -> "Picture":
        """
        Make a valid Picture.
        """
        return_me = Picture()
        return_me.failed = False
        return_me.underlying_picture = underlying_picture
        return return_me



## SECTION: Face

class Face:
    """
    A potentially recognised face, which may have failed to match or failed to run.

    Member fields:
        self.failed : bool
            True iff the facial recognition model failed
        self.matched : bool
            True iff the facial recognition model matched a face
        self.user_id : int
            if not self._failed and self._matched, then this string will contain the user
            id of the matched user
    """
    
    def __init__(self) -> "Face":
        self.failed : bool = True
        self.matched : bool = False
        self.user_id : int = None
    
    @classmethod
    def make_failed(cls) -> "Face":
        """
        Make a failed Face.
        """
        return_me = Face()
        return_me.failed = True
        return_me.matched = False
        return_me.user_id = None
        return return_me
    
    @classmethod
    def make_unmatched(cls) -> "Face":
        """
        Make an unmatched Face.
        """
        return_me = Face()
        return_me.failed = False
        return_me.matched = False
        return_me.user_id = None
        return return_me

    @classmethod
    def make_matched(cls, user_id : int) -> "Face":
        """
        Make a matched face.

        Args:
            user_id : int
                The matched user id
        """
        return_me = Face()
        return_me.failed = False
        return_me.matched = True
        return_me.user_id = user_id
        return return_me
