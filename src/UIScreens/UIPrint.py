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
        self.shoot = False

    def filtering(self, img):
        # camera = self.parent.camera
        # to_print = camera.apply_watermark(img, './data/assets/watermark.png')
        return Filtering().filter(img, self._parent.filter[self._parent.filter_id])

    def create_photo(self, name, img):
        cv2.imwrite(name, self.filtering(img))

    def print_photo(self, obj):
        os.system("lp %s" % self.TEMP_NAME)
        os.system("rm %s" % self.TEMP_NAME)
        self.parent.buttonClicked(obj)

    def initialize(self):
        cam_test = pygame.transform.smoothscale(pygame.image.load("./sprites/camtest.png"),
                                                (self._parent.w, self._parent.h))

        self.elements["camera"] = UISprite(self.surface,
                                           cam_test,
                                           0,
                                           0,
                                           self,
                                           0)

        # Back button
        def click_exit(btn):
           self.shoot = False
           self.parent.buttonClicked(btn)


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
                                                   'click': click_exit
                                                   #self.parent.buttonClicked
                                               },
                                               self,
                                               1)





        # Print button
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

        # Left backpanel
        self.elements["left_backpanel"] = UISprite(self.surface,
                                                   pygame.image.load("./sprites/left_bckg.png"),
                                                   0,
                                                   0,
                                                   self,
                                                   1)
        self.fill_left_panel(0, 0, 200, 200, [1, 2, 3, 4, 5], 10)


        UIScreen.initialize(self)

    def fill_left_panel(self, l, t, w, h, ids, v_offset):
        i = 0
        base_layer = 2
        self.max_layer = len(ids) + 2 + base_layer
        SCALE = 1.2
        DELAY = 0.2

        def insert_tween_in(btn):
            btn_idx = int(btn.name.split('_')[1])

            if btn_idx != self._parent.filter_id:
                btn.layer = self.max_layer
                btn.setTween(UIBumpEffect(SCALE, DELAY, True))
            return

        def insert_tween_out(btn):
            btn_idx = int(btn.name.split('_')[1])

            if btn_idx != self._parent.filter_id:
                btn.layer = btn_idx + base_layer
                btn.setTween(UIBumpEffect(SCALE, DELAY, False))

            return

        def on_icon_click(btn):
            if self._parent.filter_id > 0:
                self.elements["icon_%d" % self._parent.filter_id].setTween(UIBumpEffect(SCALE, DELAY, False))

            btn.layer = self.max_layer - 1
            self._parent.filter_id = int(btn.name.split('_')[1]) - 1

        for idx in ids:
            sc_a = pygame.transform.smoothscale(pygame.image.load("./sprites/filters/%d.png" % idx), (w, h))
            sc_d = pygame.transform.smoothscale(pygame.image.load("./sprites/filters/%d_d.png" % idx), (w, h))
            self.elements["icon_%d" % idx] = UISpriteButton("icon_%d" % idx,
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

    def transition(self, btn=None):
        is_in = btn == None
        from_left = ["left_backpanel", "icon_1", "icon_2", "icon_3", "icon_4", "icon_5"]
        DX = 300
        DY = 300
        DELAY = 0.2

        for elem in from_left:
            self.elements[elem].setTween(UITweenTranslate(-DX, 0, DELAY, not is_in))
            if is_in and elem.startswith("icon"):
                btn_idx = int(elem.split('_')[1])

                if btn_idx == self._parent.filter_id:
                    self.elements[elem].layer = self.max_layer - 1
                    self.elements[elem].insertTween(UIBumpEffect(1.2, DELAY, True))

        def delayedCallback():
            self.parent.buttonClicked(btn)

        if not is_in:
            t = Timer(DELAY, delayedCallback)
            t.start()

    def draw(self):
        self.create_photo(self.TEMP_NAME, self.img)
        self.frame = pygame.image.load(self.TEMP_NAME)
        self.elements["camera"].image = pygame.transform.smoothscale(self.frame, (self._parent.w, self._parent.h))
        UIScreen.draw(self)

    def setVisible(self, val, params=()):
        UIScreen.setVisible(self, val, params)
        if val:
            if (self.shoot == False):
                camera = self.parent.camera
                camera.shot()
                camera.release()
                swapper = self.parent.swapper
                self.img = swapper.apply_effect(camera.get_last_shot())
                self.shoot = True
            self.transition()
            self.create_photo(self.TEMP_NAME, self.img)
            self.frame = pygame.image.load(self.TEMP_NAME)
            self.elements["camera"].image = pygame.transform.smoothscale(self.frame, (self._parent.w, self._parent.h))