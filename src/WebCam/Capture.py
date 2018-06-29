from datetime import datetime as dt

import pygame
import cv2
import logging
import numpy as np


class Capture:
    def __init__(self):
        self._capture = None
        self._last_time = dt.now()
        self._last_frame = None
        self._frequency = 1.0 / 15.0  # frames per seconds
        self._shot = None
        self._is_active = True

        self._DESIRED_H = 720
        self._DESIRED_W = 1280
        self._ASPECT_W = int(self._DESIRED_H * 1.5)


        self.acquire()
        self.shape = self._last_frame.shape
        self.release()

    def _get_frame(self):
        tmp, self._last_frame = self._capture.read()
        clip_w = max((self._DESIRED_W - self._ASPECT_W) / 2, 0)
        if clip_w:
            self._last_frame = cv2.flip(self._last_frame, 1)[:, clip_w:-clip_w]
        else:
            self._last_frame = cv2.flip(self._last_frame, 1)

    def acquire(self):
        logger = logging.getLogger("FaceSwap.Capture.acquire")
        if self._capture is not None:
            if self._capture.isOpened():
                return

        self._capture = cv2.VideoCapture(0)

        if not self._capture.isOpened():
            logger.exception("Camera doesn't open!")
            raise IOError("Camera doesn't open!")

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._DESIRED_W)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._DESIRED_H)

        self._get_frame()

    def set_active(self, val):
        self._is_active = val

    def is_cam_active(self):
        return self._capture and self._capture.isOpened() and self._is_active

    def get_next_frame(self):
        logger = logging.getLogger("FaceSwap.get_next_frame.acquire")
        if self._capture is None:
            logger.exception("Camera doesn't exist!")
            raise IOError("Camera doesn't exist!")

        if not self._capture.isOpened():
            logger.exception("Camera doesn't exist!")
            raise IOError("Camera doesn't open!")

        now = dt.now()

        passed_time = (now - self._last_time).total_seconds()

        if passed_time - self._frequency >= 0:
            self._get_frame()
            self._last_time = now


        return self._last_frame

    def shot(self):
        self._shot = self._last_frame

    def get_last_shot(self):\
        return self._shot

    def get_pygame_image(self, img):
        if len(img):
            if img.shape[2] != 3:
                res[:, :, 0] = img[:, :, 0]
                res[:, :, 1] = img[:, :, 1]
                res[:, :, 2] = img[:, :, 2]
                img = res

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return pygame.image.frombuffer(img.tostring(), img.shape[1::-1], "RGB")
        return None

    def apply_watermark(self, img, water_path):
        L = 150
        R = 150
        T = 150
        D = 150
        water = cv2.imread(water_path, -1)
        shape = water.shape
        if len(water):
            img = cv2.resize(img, (shape[1] - L - R, shape[0] - T - D), interpolation=cv2.INTER_LINEAR)

            alpha = img.copy().astype(np.float32)
            alpha[:, :, 0] = water[T:shape[0] - D, L:shape[1] - R, 3] / 255.0
            alpha[:, :, 1] = water[T:shape[0] - D, L:shape[1] - R, 3] / 255.0
            alpha[:, :, 2] = water[T:shape[0] - D, L:shape[1] - R, 3] / 255.0

            res = water.copy()
            res[T:shape[0] - D, L:shape[1] - R, 3] = 255

            res[T:shape[0] - D, L:shape[1] - R, 0:3] = img[:, :] * (1 - alpha[:, :]) + water[T:shape[0] - D, L:shape[1] - R, 0:3] * (alpha[:, :])
            return res

        return None


    def release(self):
        if self._capture is not None:
            if self._capture.isOpened():
                self._capture.release()

    def __del__(self):
        self.release()