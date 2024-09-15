from abc import ABC, abstractmethod

import numpy as np
import time
import cv2
import os


class FrameCapturer(ABC):
    """Provides an interface to video frames for a PostureTracker."""

    @abstractmethod
    def get_frame(self) -> tuple[np.ndarray, int]:
        """
        Returns:
            (frame, timestamp), image is an image frame in the format HxWxC. Where the channels are
                in RGB format. Timestamp is in milliseconds.
        """


class OpenCVCapturer(FrameCapturer):
    """FrameCapturer using OpenCV to read from camera."""

    def __init__(self) -> None:
        self._cam = cv2.VideoCapture(0)

    def get_frame(self) -> tuple[np.ndarray, int]:
        _, frame = self._cam.read()
        timestamp = self._cam.get(cv2.CAP_PROP_POS_MSEC)
        return frame, timestamp

    def release(self) -> None:
        """Release the camera."""
        self._cam.release()


class RaspCapturer(FrameCapturer):
    """FrameCapturer using a temp file to read from the camera.
    File is created using client/drivers/camera_overlord.py"""
    def get_frame(self) -> tuple[np.ndarray, int]:
        tries = 0
        while True:
            array = cv2.imread('/tmp/snapshot.jpg')
            if array is None:
                tries += 1
                if tries > 5: raise FileNotFoundError('No snapshot found')
                time.sleep(0.05) 
            else:
                tries = 0
                finfo = os.stat('/tmp/snapshot.jpg')
                return (array, finfo.st_mtime)