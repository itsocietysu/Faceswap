import pygame
from pygame.locals import *
from robotgui import *
import cv2
import os
from utils.Filtering import Filtering

class UIPrint(UIScreen):
    def __init__(self, name, parent):
        UIScreen.__init__(self, name, parent)
        self.TEMP_NAME = "./tmp_to_print.png"
        self._parent = parent
        self.fnumber = -1
        self.type = ""

    def create_photo(self, name, img):
        filtering = Filtering()
        camera = self.parent.camera
        img = filtering.filter(img, self._parent.filter_settings)
        to_print = camera.apply_watermark(img, './data/assets/watermark.png')


        cv2.imwrite(name, to_print)
        return to_print

    def print_photo(self, obj):
        os.system("lp %s" % self.TEMP_NAME)
        os.system("rm %s" % self.TEMP_NAME)
        self.parent.buttonClicked(obj)

    def initialize(self):
        cam_test = pygame.transform.smoothscale(pygame.image.load("./sprites/camtest.png"),
                                                (self._parent.w, self._parent.h))

        self.elements["camera"] = UISprite(self.surface, cam_test, 0, 0, self, 0)

        button = pygame.image.load("./sprites/back.png")
        buttonHov = pygame.image.load("./sprites/back_hov_b.png")
        self.elements["exit"] = UISpriteButton("exit",
                                               self.surface,
                                               button,
                                               buttonHov,
                                               self.surface.get_rect().center[0] - button.get_rect().center[0]
                                               + button.get_rect().width,
                                               self.surface.get_rect().bottom - button.get_rect().height,
                                               {
                                                   'click': self.parent.buttonClicked
                                               },
                                               self,
                                               1)

        button = pygame.image.load("./sprites/print.png")
        buttonHov = pygame.image.load("./sprites/print_hov_b.png")
        self.elements["print"] = UISpriteButton("print",
                                                self.surface,
                                                button,
                                                buttonHov,
                                                self.surface.get_rect().center[0] - button.get_rect().center[0]
                                                - button.get_rect().width,
                                                self.surface.get_rect().bottom - button.get_rect().height,
                                                {
                                                    'click': self.print_photo
                                                },
                                                self,
                                                1)

        UIScreen.initialize(self)

    def setVisible(self, val, params=()):
        UIScreen.setVisible(self, val, params)

        if val:
            camera = self.parent.camera
            camera.shot()
            camera.release()
            swapper = self.parent.swapper
            self.frame = swapper.apply_effect(camera.get_last_shot())
            self.create_photo(self.TEMP_NAME, self.frame)

            self.frame = pygame.image.load(self.TEMP_NAME)
            self.elements["camera"].image = pygame.transform.smoothscale(self.frame, (self._parent.w, self._parent.h))
