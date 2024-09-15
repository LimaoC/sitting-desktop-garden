"""
File:
    sitting-desktop-garden/client/proof_of_concept/flood_database_with_data.py

Purpose:
    Providing debug test data

Author:
    Gabriel Field (47484306)

Source:
    Largely based on https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0
"""

## SECTION: Imports

from datetime import datetime, timedelta
import random

import data.routines as db



## SECTION: Moses

NUMBER_OF_SECONDS_IN_AN_HOUR = 3600
"""title"""

def DEBUG_flood() -> None:
    """
    Flood the database with debug test data, for user with ID 1, set up for THE NEXT HOUR.
    The debug test data includes a random posture record for each SECOND of the hour.
    """
    print("<!> Killing database")
    db.destroy_database()
    print("<!> Initialising database")
    db.init_database()
    print("<!> Making user")
    user_id = db.create_user()
    print(f"<!> {user_id=}")
    print("<!> Flooding with posture records...")
    now = datetime.now()
    for second in range(NUMBER_OF_SECONDS_IN_AN_HOUR):
        db.save_posture(posture = db.Posture(
            id_ = None,
            user_id = user_id,
            prop_good = random.random(),
            prop_in_frame = random.random(),
            period_start = now + timedelta(seconds = second),
            period_end = now + timedelta(seconds = second + 1)
        ))
    print("<!> Database flooded. Exiting.")
    return


## LAUNCH

if __name__ == "__main__":
    DEBUG_flood()
