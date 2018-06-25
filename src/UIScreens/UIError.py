import pygame
from pygame.locals import *
from robotgui import *

class UIError(UIScreen):
    def __init__(self, name, parent):
        UIScreen.__init__(self, name, parent)
        self._parent = parent

    def initialize(self):
        self.elements["background"] = UISprite(self.surface, pygame.image.load("./sprites/bckgempty.png"), 0, 0, self, 0)
        self.elements["err_text1"] = UIText(self.surface, self._parent.strings.get('error_info_message1'), self, 2)
        self.elements["err_text2"] = UIText(self.surface, self._parent.strings.get('error_info_message2'), self, 2)

        button = pygame.image.load("./sprites/waitspin.png")
        x = (self.surface.get_rect().center[0] - button.get_rect().center[0])
        y = (self.surface.get_rect().height - button.get_rect().height * 2)

        self.elements["waitspin"] = UISprite(self.surface, pygame.image.load("./sprites/waitspin.png"), x, y, self, 1)
        self.elements["waitspin"].insertTween(UIRotate(360))
        UIScreen.initialize(self)
