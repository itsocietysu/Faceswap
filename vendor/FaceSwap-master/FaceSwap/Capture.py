from datetime import datetime as dt

import numpy as np
import cv2


class Capture:
    def __init__(self):
        self._capture = None
        self._last_time = dt.now()
        self._last_frame = None
        self._frequency = 1.0 / 30.0  # frames per seconds

    def _get_frame(self):
        tmp, self._last_frame = self._capture.read()
        self._last_frame = cv2.flip(self._last_frame, 1)

    def acquire(self):
        if self._capture is not None:
            if self._capture.isOpened():
                return

        self._capture = cv2.VideoCapture(0)

        if not self._capture.isOpened():
            raise IOError("Camera doesn't open!")

        self._get_frame()

    def get_next_frame(self):
        if self._capture is None:
            raise IOError("Camera doesn't exist!")

        if not self._capture.isOpened():
            raise IOError("Camera doesn't open!")

        now = dt.now()

        passed_time = (now - self._last_time).total_seconds()

        if passed_time - self._frequency >= 0:
            self._get_frame()
            self._last_time = now


        return self._last_frame

    def release(self):
        if self._capture is not None:
            if self._capture.isOpened():
                self._capture.release()

    def __del__(self):
        self.release()