import pygame
from pygame.locals import *
from robotgui import *
import cv2
import os
from utils.Filtering import Filtering
import numpy as np

class UIPrint(UIScreen):
    def __init__(self, name, parent):
        UIScreen.__init__(self, name, parent)
        self.TEMP_NAME = "./tmp_to_print.png"
        self._parent = parent
        self.fnumber = -1
        self.type = ""
        self.shoot = False
        self.max_layer = -1
        self.s = (188, 188)#(int(200), int(720 / (1080 / 200))) #(1080, 720)

    def filtering(self, img, filter):
        img = Filtering().filter(img, filter)
        return img

    def apply_watermark(self, img, water_path, params={}):
        def_params = {'L': 0, 'R': 0, 'T': 0, 'D': 0}
        def_params.update(params)
        params = def_params
        L = params['L']
        R = params['R']
        T = params['T']
        D = params['D']
        water = cv2.imread(water_path, -1)

        water = cv2.resize(water, (img.shape[1] - (L + R), img.shape[0] - (T + D)))
        shape = img.shape
        if len(water):
            alpha = img.copy().astype(np.float32)
            alpha[T:shape[0] - D, L:shape[1] - R, 0] = water[:, :, 3] / 255.0
            alpha[T:shape[0] - D, L:shape[1] - R, 1] = water[:, :, 3] / 255.0
            alpha[T:shape[0] - D, L:shape[1] - R, 2] = water[:, :, 3] / 255.0

            res = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            res[T:shape[0] - D, L:shape[1] - R, 3] = 255

            res[T:shape[0] - D, L:shape[1] - R, 0:3] = img[T:shape[0] - D, L:shape[1] - R] \
                                                       * (1 - alpha[T:shape[0] - D, L:shape[1] - R]) \
                                                       + water[:, :, 0:3] * (alpha[T:shape[0] - D, L:shape[1] - R])
            return res

        return None

    def create_photo(self, name, img):
        img = self.filtering(img, self._parent.filter[self._parent.filter_id])
        img = self.apply_watermark(img, "./data/assets/watermark_new.png")
        cv2.imwrite(name, img)

    def print_photo(self, obj):
        os.system("lp %s" % self.TEMP_NAME)
        os.system("rm %s" % self.TEMP_NAME)
        self.shoot = False
        self.parent.buttonClicked(obj)

    def update_filter_prints(self):
        self.filter_prints = self.get_filter_prints(self.img)


    def initialize(self):
        self.max_layer = -1
        self._parent.filter_id = 0


        cam_test = pygame.transform.smoothscale(pygame.image.load("./sprites/camtest.png"),
                                                (self._parent.w, self._parent.h))
        self.img = cv2.imread("./sprites/camtest.png")

        self.update_filter_prints()

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
                                                   pygame.image.load("./sprites/left_bckg1.png"),
                                                   0,
                                                   0,
                                                   self,
                                                   1)
        self.fill_left_panel(0, 0, self.s[0], self.s[1], [1, 2, 3, 4, 5], 10)
        UIScreen.initialize(self)

    def fill_left_panel(self, l, t, w, h, ids, v_offset):
        i = 0
        base_layer = 2
        self.max_layer = len(ids) + 2 + base_layer
        SCALE = 1.2
        DELAY = 0.2

        def insert_tween_in(btn):
            btn_idx = int(btn.name.split('_')[1])

            if btn_idx != self._parent.filter_id + 1:
                btn.layer = self.max_layer
                btn.setTween(UIBumpEffect(SCALE, DELAY, True))
            return

        def insert_tween_out(btn):
            btn_idx = int(btn.name.split('_')[1])

            if btn_idx != self._parent.filter_id + 1:
                btn.layer = btn_idx + base_layer
                btn.setTween(UIBumpEffect(SCALE, DELAY, False))
            return

        def on_icon_click(btn):
            if self._parent.filter_id + 1 != int(btn.name.split("_")[1]):
                self.elements["icon_%d" % (self._parent.filter_id + 1)].setTween(UIBumpEffect(SCALE, DELAY, False))
            btn.layer = self.max_layer - 1
            self._parent.filter_id = int(btn.name.split('_')[1]) - 1
            self.create_photo(self.TEMP_NAME, self.img)


        for idx in ids:
            cnv_img = cv2.cvtColor(self.filter_prints[idx - 1], cv2.COLOR_BGR2RGB)
            sc_a = pygame.transform.smoothscale(pygame.image.frombuffer(cnv_img.tostring(),
                                                                        cnv_img.shape[1::-1],
                                                                        "RGB"),
                                                (w, h))

            self.elements["icon_%d" % idx] = UISpriteButton("icon_%d" % idx,
                                                            self.surface,
                                                            sc_a,
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
        DELAY = 0.2

        for elem in from_left:
            self.elements[elem].setTween(UITweenTranslate(-DX, 0, DELAY, not is_in))
            if is_in and elem.startswith("icon"):
                btn_idx = int(elem.split('_')[1])
                if btn_idx == self._parent.filter_id + 1:
                    self.elements[elem].layer = self.max_layer - 1
                    self.elements[elem].insertTween(UIBumpEffect(1.2, DELAY, True))

        def delayedCallback():
            self.parent.buttonClicked(btn)

        if not is_in:
            t = Timer(DELAY, delayedCallback)
            t.start()


    def get_filter_prints(self, img):
        size = 500 # TODO MOVE TO SETTIGS

        w = self.img.shape[1]
        h = self.img.shape[0]

        s = (int((h - size) / 2), int((w - size) / 2))
        e = (int((h + size) / 2), int((w + size) / 2))

        img = img[s[0]:e[0], s[1]:e[1]]

        img = cv2.resize(img, self.s)

        filter_prints = []
        for i in range(5):
            new_img = self.filtering(img, self._parent.filter[i])
            new_img = self.apply_watermark(new_img, "./sprites/filter/%i_name.png" % (i + 1))
            filter_prints.append(new_img)

        return filter_prints


    def redraw_filter_prints(self):
        for idx in xrange(5):
            cnv_img = cv2.cvtColor(self.filter_prints[idx], cv2.COLOR_BGR2RGB)
            self.elements["icon_%d" % (idx + 1)].image_hover = self.elements["icon_%d" % (idx + 1)].image = \
                pygame.transform.smoothscale(pygame.image.frombuffer(cnv_img.tostring(),
                                                                     cnv_img.shape[1::-1],
                                                                     "RGB"),
                                                (self.s[0], self.s[1]))

    def draw(self):
        self.frame = pygame.image.load(self.TEMP_NAME)
        self.elements["camera"].image = pygame.transform.smoothscale(self.frame, (self._parent.w, self._parent.h))
        self.redraw_filter_prints()
        UIScreen.draw(self)

    def setVisible(self, val, params=()):
        if val:
            if (self.shoot == False):
                self.shoot = True
                camera = self.parent.camera
                camera.shot()
                camera.release()
                swapper = self.parent.swapper
                self.img = swapper.apply_effect(camera.get_last_shot())
                self.create_photo(self.TEMP_NAME, self.img)
                self.update_filter_prints()
            self.transition()
        UIScreen.setVisible(self, val, params)