import cv2
import threading
from FaceSwap.FaceOfScientistsSwap import FaceOfScientistsSwap
from StateMachine.Storage import storage

import logging

class FaseSwapEffect:
    def __init__(self, camera):
        logger = logging.getLogger("FaceSwap.FaseSwapEffect.__init__")

        self.skins = [
            'Elon.jpg',
            'Stiv.jpg',
            'einstein.jpg',
            'mendel.jpg',
            'ciol.jpg',
        ]

        self.skins_dir = './data/skins/'

        images = map(cv2.imread, [self.skins_dir + x for x in self.skins])

        for img in images:
            if img is None:
                logger.exception("Error loading from path: " + self.skins_dir)
                raise ImportError("Error loading from path: " + self.skins_dir)

        try:
            self.swapper = FaceOfScientistsSwap(camera.shape, images)
        except:
            logger.exception("FaceOfScientistsSwap doesn't initialize")
            raise Exception("FaceOfScientistsSwap doesn't initialize")
        self.camera = camera

    def apply_effect(self, img):
        curr_idx = max(min(storage.current_scientist_id - 1, len(self.skins) - 1), -1)

        if curr_idx >= 0:
            return self.swapper.get_replacement_image(img, curr_idx)

        return img

