"""
Brief:
    Data structures for use on the RPi Client.
File:
    sitting-desktop-garden/client/drivers/data_structures.py
Author:
    Gabriel Field (47484306)
"""

## SECTION: Imports

from typing import List
from PiicoDev_Switch import PiicoDev_Switch
from PiicoDev_SSD1306 import *

from datetime import datetime

# DEBUG:
from math import sin, pi
# :DEBUG


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
            Time of the last successful pull of posture data from the SQLite database
        self._last_cushion_time : datetime.datetime
            Time of the last successful cushion feedback event.
        self._last_plant_time : datetime.datetime
            Time of the last successful plant feedback event.
        self._last_sniff_time : datetime.datetime                TODO: Change this so it doesn't say "sniff". Change the getters and setters
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
        self._DEBUG_current_graph_list_index = 0
        self._DEBUG_current_graph_function = lambda x:  30 * (1 + sin(2 * pi * x / WIDTH))

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
        print("<!> Made a new empty ControlledData() with user_id", return_me._user_id)
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

    def DEBUG_get_next_posture_graph_value(self) -> int:
        """
        Get next thing to put on the DEBUG graph.

        Returns:
            (int): Next thing to put on the DEBUG graph.

        TODO: Remove this method
        """
        return_me = self._DEBUG_current_graph_function(self._DEBUG_current_graph_list_index)
        self._DEBUG_current_graph_list_index += 1
        return return_me

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
            (POSTURE_DATA): The posture data stored in this ControlledData.
        """
        return self._posture_data

    def get_last_snapshot_time(self) -> datetime:
        """
        Returns:
            (datetime): The last time that the internal posture data was updated.
        """
        return self._last_snapshot_time
    
    def set_last_snapshot_time(self, time : datetime) -> None:
        """
        Args:
            time : datetime
                The last time that the internal posture data was updated.
        """
        self._last_snapshot_time = time

    def get_last_cushion_time(self) -> datetime:
        """
        Returns:
            (datetime): The last time that the user was provided cushion feedback.
        """
        return self._last_cushion_time

    def set_last_cushion_time(self, time : datetime) -> None:
        """
        Args:
            time : datetime
                The last time that the user was provided cushion feedback.
        """
        self._last_cushion_time = time
    
    def get_last_plant_time(self) -> datetime:
        """
        Returns:
            (datetime): The last time that the user was provided plant feedback.
        """
        return self._last_plant_time

    def set_last_plant_time(self, time : datetime) -> None:
        """
        Args:
            time : datetime
                The last time that the user was provided plant feedback.
        """
        self._last_plant_time = time
    
    def get_last_sniff_time(self) -> datetime:
        """
        Returns:
            (datetime): The last time that the user was provided olfactory feedback.
        """
        return self._last_cushion_time

    def set_last_sniff_time(self, time : datetime) -> None:
        """
        Args:
            time : datetime
                The last time that the user was provided olfactory feedback.
        """
        self._last_sniff_time = time
    
    def accept_new_posture_data(self, posture_data : "POSTURE_DATA") -> None: # TODO: Refine type signature
        """
        Update the internal store of posture data.

        Args:
            posture_data : POSTURE_DATA
                New posture data to accept and merge with the current state of this object.
        
        TODO: Implement me!
        """
        # DEBUG:
        print("<!> accept_new_posture_data()")
        # :DEBUG


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
        self.display : PiicoDev_SSD1306
            OLED SSD1306 Display with default address
        self.posture_graph : PiicoDev_SSD1306.graph2D | None
            Graph object for rendering on self.display. NOT INITIALISED by default; i.e. None until initialised.
            Should get initialised ONCE THE USER IS LOGGED IN because the graph will look different for each user.
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
            PiicoDev_Switch(id = [0, 0, 0, 0], double_press_duration = DOUBLE_PRESS_DURATION), # WARNING: 2024-09-01 17:12 Gabe: I think this produces an "I2C is not enabled" warning. No idea why.
            PiicoDev_Switch(id = [0, 0, 0, 1], double_press_duration = DOUBLE_PRESS_DURATION), # WARNING: 2024-09-01 17:12 Gabe: I think this produces an "I2C is not enabled" warning. No idea why.
            create_PiicoDev_SSD1306() # This is the constructor; ignore the "is not defined" error message.
            
        )

    def __init__(self, button0, button1, display):
        self.button0: PiicoDev_Switch = button0 
        self.button1: PiicoDev_Switch = button1
        self.display: PiicoDev_SSD1306 = display
        self.posture_graph : PiicoDev_SSD1306.graph2D | None = None
    
    # SECTION: Setters

    # 2024-09-02 14-45 Gabe: TESTED.
    def get_control_messages(self, user_id : int) -> List[int]:
        """
        Get messages to display during usual application loop.
        TODO: Finalise these!

        Args:
            user_id : int
                ID of the currently logged-in user.
        """
        return ["b0: logout", "id: " + str(user_id)]

    def initialise_posture_graph(self, user_id : int) -> None:
        """
        Initialise self.posture_graph according to the provided user_id.

        Args:
            user_id : int
                ID of the currently logged-in user.

        WARNING: UNTESTED!
        """
        CONTROL_MESSAGES = self.get_control_messages(user_id)
        GRAPH_MIN_VALUE = 0
        GRAPH_MAX_VALUE = 60    # TODO: 2024-09-02 07-53 Gabe:
                                #       This needs to be a real value for the underlying data that we expect to be shown. 
                                #       From memory, this is probably `60` for "number of the last 60 seconds spent sitting well"
        LINE_HEIGHT = 15 # pixels
        LINE_WIDTH = 16 # characters
        
        # The posture graph will occupy space from the bottom (y = HEIGHT - 1) up to initialisation_y_value.
        initialisation_y_value = len([CONTROL_MESSAGES[i : i + LINE_WIDTH] for i in range(0, len(CONTROL_MESSAGES), LINE_WIDTH)]) * LINE_HEIGHT
        self.posture_graph = self.display.graph2D(
            originX = 0, originY = HEIGHT - 1, 
            width = WIDTH, height = HEIGHT - initialisation_y_value, 
            minValue = GRAPH_MIN_VALUE, maxValue = GRAPH_MAX_VALUE, 
            c = 1, bars = False
        )
    
    # SECTION: Using peripherals

    # 2024-09-01 16:57 Gabe: TESTED.
    def oled_display_text(self, text : str, x : int, y : int, colour : int = 1) -> int:
        """
        Display text on the oled display, wrapping lines if necessary.
        NOTE: Does not blank display. Call `.display.fill(0)` if needed.
        NOTE: Does not render. Call `.display.show()` if needed.
        

        Args:
            text : str
                String to write to the OLED display.
            x : int
                Horizontal coordinate from left side of screen.
            y : int
                Vertical coordinate from top side of screen.
            colour : int
                Defaults white.
                0: black
                1: white
        
        Returns:
            (int): The y-value at which any subsequent lines should start printing from.
        """
        LINE_HEIGHT = 15 # pixels
        LINE_WIDTH = 16 # characters
        chunks = [text[i : i + LINE_WIDTH] for i in range(0, len(text), LINE_WIDTH)]
        for (index, chunk) in enumerate(chunks):
            self.display.text(chunk, x, y + index * LINE_HEIGHT, colour)
        return y + len(chunks) * LINE_HEIGHT
    
    # 2024-09-01 17:12 Gabe: TESTED.
    def oled_display_texts(self, texts: List[str], x : int, y : int, colour : int) -> int:
        """
        Display many lines of text on the oled display, wrapping lines if necessary.
        NOTE: Does not blank display. Call `.display.fill(0)` if needed.
        NOTE: Does not render. Call `.display.show()` if needed.

        Args:
            texts : List[str]
                Strings to write to the OLED display. Each string begins on a new line.
            x : int
                Horizontal coordinate from left side of screen.
            y : int
                Vertical coordinate from top side of screen.
            colour : int
                0: black
                1: white
        
        Returns:
            (int): The y-value at which any subsequent lines should start printing from.
        """
        display_height_offset = 0
        for text in texts:
            display_height_offset = self.oled_display_text(text, x, y + display_height_offset, colour)
        return display_height_offset



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
            if not self.failed and self.matched, then this string will contain the user
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
