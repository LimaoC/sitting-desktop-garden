import cv2
from models.pose_detection.routines import (
    DebugPostureTracker,
    create_debug_posture_tracker,
)


def run_posture_tracking_loop(posture_tracker: DebugPostureTracker):
    while True:
        # Other control flow code
        # ...

        posture_tracker.track_posture()

        # ...
        # Other control flow code

        # Quit when q is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


with create_debug_posture_tracker() as posture_tracker:
    run_posture_tracking_loop(posture_tracker)
