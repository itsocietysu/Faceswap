import pygame
from pygame.locals import *
from robotgui import UIScreen, UISprite, UIEvent, UIBumpEffect, UIProxySprite
from threading import Timer
import cv2

class UICapture(UIScreen):
    def __init__(self, name, parent):
        UIScreen.__init__(self, name, parent)
        self._parent = parent
        self.is_thread_buisy = False

    def prepare_counters(self, _from, _to, cx, cy):
        for idx in range(_from, _to + 1):
            c = pygame.image.load("./sprites/count/%d.png" % idx)

            self.elements["%d" % idx] = \
                UISprite(self.surface,
                         c,
                         cx - c.get_rect().center[0],
                         cy - c.get_rect().center[1],
                         self,
                         3)

            self.elements["%d" % idx].visible = False

    def initialize(self):
        cam_test = cv2.resize(cv2.imread("./sprites/camtest.png"), (self._parent.w, self._parent.h))

        self.elements["camera"] = UIProxySprite(self.surface, cam_test, self, 0)

        self.prepare_counters(1, 3, self.surface.get_rect().center[0], self.surface.get_rect().center[1])

        UIScreen.initialize(self)

    def setVisible(self, val, params=()):
        SCALE = 0.05
        DELAY = 5.0
        STEP_DELAY = DELAY / 3.0
        COUNT_DOWNS = 3
        POW_NUM = 0.5
        UIScreen.setVisible(self, val, params)

        def step(curr_step):
            if curr_step > 0:
                if curr_step < COUNT_DOWNS:
                    self.elements["%d" % (curr_step + 1)].visible = False
                self.elements["%d" % curr_step].visible = True
                self.elements["%d" % curr_step].setTween(UIBumpEffect(SCALE, STEP_DELAY, False, POW_NUM))
                t = Timer(STEP_DELAY, step, args=[curr_step - 1])
                t.start()
            else:
                self.elements["%d" % (curr_step + 1)].visible = False
                self.parent.postEvent(UIEvent("show", "print", ()))

        self.parent.camera.acquire()
        if val:
            self.parent.camera.set_active(val)
            step(COUNT_DOWNS)

    def draw(self):
        if self._parent.camera.is_cam_active():
            camera = self.parent.camera
            swapper = self.parent.swapper
            frame = swapper.apply_effect(camera.get_next_frame())
            self.elements["camera"].image = cv2.resize(frame, (self._parent.w, self._parent.h))

        UIScreen.draw(self)