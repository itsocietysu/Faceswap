import pygame
from pygame.locals import *
from robotgui import *
from threading import Timer
from utils.TimerProfiler import *

import cv2




class UIMain(UIScreen):
    def __init__(self, name, parent):
        self.lastActionTime = 0
        self._parent = parent
        self.margin = 25
        self.max_layer = -1
        UIScreen.__init__(self, name, parent)

    def fill_left_panel(self, l, t, w, h, ids, v_offset):
        i = 0
        base_layer = 2
        self.max_layer = len(ids) + 2 + base_layer

        SCALE = 1.2
        DELAY = 0.2

        def insert_tween_in(btn):
            btn_idx = int(btn.name.split("_")[1])

            if btn_idx != self._parent.storage.current_scientist_id:
                btn.layer = self.max_layer
                btn.setTween(UIBumpEffect(SCALE, DELAY, True))
            return

        def insert_tween_out(btn):
            btn_idx = int(btn.name.split('_')[1])

            if btn_idx != self._parent.storage.current_scientist_id:
                btn.layer = btn_idx + base_layer
                btn.setTween(UIBumpEffect(SCALE, DELAY, False))

            return

        def on_icon_click(btn):
            if self._parent.storage.current_scientist_id > 0 and\
                    self._parent.storage.current_scientist_id != int(btn.name.split("_")[1]):
                self.elements["icon_%d" % self._parent.storage.current_scientist_id].setTween(UIBumpEffect(SCALE,
                                                                                                           DELAY,
                                                                                                           False))

            btn.layer = self.max_layer - 1
            self._parent.storage.current_scientist_id = int(btn.name.split('_')[1])

        for idx in ids:
            sc_a = pygame.transform.smoothscale(pygame.image.load("./sprites/avatars/%d.png" % idx),
                                                (w, h))
            sc_d = pygame.transform.smoothscale(pygame.image.load("./sprites/avatars/%d_d.png" % idx),
                                                (w, h))

            self.elements["icon_%d" % idx] = \
                UISpriteButton("icon_%d" % idx,
                               self.surface,
                               sc_d,
                               sc_a,
                               l,
                               t + (h + v_offset) * i,
                               {
                                   'click': on_icon_click,
                                   'hoverin': insert_tween_in,
                                   'hoverout': insert_tween_out,
                               },
                               self,
                               base_layer + idx)

            i += 1

    def initialize(self):
        # Camera frame placeholder
        cam_test = cv2.resize(cv2.imread("./sprites/camtest.png"), (self._parent.w, self._parent.h))

        self.elements["camera"] = UIProxySprite(self.surface, cam_test, self, 0)

        # Left backpanel
        self.elements["left_backpanel"] = UISprite(self.surface, pygame.image.load("./sprites/left_bckg1.png"), 0, 0, self, 1)
        self.fill_left_panel(0, 0, 188, 188, [1, 2, 3, 4, 5], 10)

        # Photo button
        button = pygame.image.load("./sprites/shot.png")
        buttonHov = pygame.image.load("./sprites/shot_hov.png")
        self.elements["photo"] = UISpriteButton("photo",
                                                self.surface,
                                                button,
                                                buttonHov,
                                                self.surface.get_rect().center[0] - button.get_rect().width / 2 + self.margin,
                                                self.surface.get_rect().bottom - button.get_rect().height,
                                                {
                                                    'click': self.transition
                                                },
                                                self,
                                                2)


        # Info button
        #button = pygame.image.load("./sprites/buttonInfo.png")
        #buttonHov = pygame.image.load("./sprites/buttonInfoHov.png")
        #self.elements["info"] = UISpriteButton("info",
        #                                       self.surface,
        #                                       button,
        #                                       buttonHov,
        #                                       self.surface.get_rect().width - button.get_rect().width - self.margin,
        #                                       self.surface.get_rect().top + self.margin,
        #                                       {
        #                                           'click': self.transition
        #                                       },
        #                                       self,
        #                                       2)

        UIScreen.initialize(self)

    def transition(self, btn=None):

        is_in = btn == None

        from_left = ["left_backpanel", "icon_1", "icon_2", "icon_3", "icon_4", "icon_5"]
        #from_right = ["info"]
        from_down = ["photo"]

        DX = 300
        DY = 300
        DELAY = 0.2

        for elem in from_left:
            self.elements[elem].setTween(UITweenTranslate(-DX, 0, DELAY, not is_in))
            if is_in and elem.startswith("icon"):
                btn_idx = int(elem.split('_')[1])

                if btn_idx == self._parent.storage.current_scientist_id:
                    self.elements[elem].layer = self.max_layer - 1
                    self.elements[elem].insertTween(UIBumpEffect(1.2, DELAY, True))

        #info button
        #for elem in from_right:
        #    self.elements[elem].setTween(UITweenTranslate(DX, 0, DELAY, not is_in))

        for elem in from_down:
            self.elements[elem].setTween(UITweenTranslate(0, DY, DELAY, not is_in))

        def delayedCallback():
            self.parent.buttonClicked(btn)

        if not is_in:
            t = Timer(DELAY, delayedCallback)
            t.start()

    def setVisible(self, val, params=()):
        UIScreen.setVisible(self, val, params)
        if val:
            self.transition()

        self.parent.camera.set_active(val)

    def draw(self):
        timer = TimerProfiler(False)
        timer.start()
        if self._parent.camera.is_cam_active():
            camera = self.parent.camera
            swapper = self.parent.swapper

            cam_frame = camera.get_next_frame()
            timer.print_lap(timer.lap(), "get frame")
            effect = swapper.apply_effect(cam_frame)
            timer.print_lap(timer.lap(), "apply effect")
            frame = effect#camera.get_pygame_image(effect)
            timer.print_lap(timer.lap(), "redo image")
            self.elements["camera"].image = cv2.resize(frame, (self._parent.w, self._parent.h))
            timer.print_lap(timer.lap(), "image assign")

        UIScreen.draw(self)
        timer.print_lap(timer.lap(), "parent draw")

