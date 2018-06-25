import pygame
from pygame.locals import *
from robotgui import *
from threading import Timer

class UIInfo(UIScreen):
    def __init__(self, name, parent):
        self._parent = parent
        UIScreen.__init__(self, name, parent)

    def initialize(self):
        self.elements["logo"] = UISprite(self.surface, pygame.image.load("./sprites/polylogo.png"), 0, 0, self, 1)

        tut1 = pygame.image.load("./sprites/tut_1.png")
        self.elements["tut1"] = UISprite(self.surface,
                                         tut1,
                                         self.surface.get_rect().width - tut1.get_rect().width - 100,
                                         350,
                                         self,
                                         1)

        tut2 = pygame.image.load("./sprites/shot.png")
        self.elements["tut2"] = UISprite(self.surface,
                                         tut2,
                                         82,
                                         450,
                                         self,
                                         1)

        tut3 = pygame.image.load("./sprites/print.png")
        self.elements["tut3"] = UISprite(self.surface,
                                         tut3,
                                         self.surface.get_rect().width - tut1.get_rect().width - 100,
                                         650,
                                         self,
                                         1)

        button = pygame.image.load("./sprites/back.png")
        buttonHov = pygame.image.load("./sprites/back_hov_b.png")
        self.elements["exit"] = UISpriteButton("exit",
                                               self.surface,
                                               button,
                                               buttonHov,
                                               self.surface.get_rect().width - button.get_rect().width - 20,
                                               self.surface.get_rect().top,
                                               {
                                                   'click': self.parent.buttonClicked
                                               },
                                               self,
                                               1)

        self.elements["text1"] = UIText(self.surface, self._parent.strings.get('info_first_info_message'), self, 2)
        self.elements["text2"] = UIText(self.surface, self._parent.strings.get('info_second_info_message'), self, 2)
        self.elements["text3"] = UIText(self.surface, self._parent.strings.get('info_third_info_message'), self, 2)
        UIScreen.initialize(self)

    def setVisible(self, val, params=()):
        UIScreen.setVisible(self, val, params)
        if val:
            self.transition()

    def transition(self, btn=None):
        is_in = btn == None

        from_left = ["logo", "tut2", "text1", "text3"]
        from_right = ["tut1", "tut3", "exit", "text2"]

        DX = 1000
        DY = 0
        DELAY = 0.3

        for elem in from_left:
            self.elements[elem].setTween(UITweenTranslate(-DX, 0, DELAY, not is_in))

        for elem in from_right:
            self.elements[elem].setTween(UITweenTranslate(DX, 0, DELAY, not is_in))

        def delayedCallback():
            self.parent.buttonClicked(btn)

        if not is_in:
            t = Timer(DELAY, delayedCallback)
            t.start()