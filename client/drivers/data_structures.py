"""
Brief:
    Data structures for use on the RPi Client.
File:
    sitting-desktop-garden/client/drivers/data_structures.py
Author:
    Gabriel Field (47484306)
"""

## SECTION: Imports

from datetime import datetime



## SECTION: Constants

EMPTY_USER_ID = ""
EMPTY_POSTURE_DATA = None # TODO: Refine to a legal term, once the type is figured out



## SECTION: ControlledData

class ControlledData:
    """
    Data for passing around in client/drivers/main.big_chungus()

    Member fields:
        self._failed : bool                           
            True if this data is incomplete.
        self._user_id : str
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
    def make_empty(cls, user_id : str) -> "ControlledData":
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
    
    def get_user_id(self) -> str:
        """
        Returns:
            (str): The user id of this ControlledData.
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
    