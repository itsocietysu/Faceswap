import pygame
from utils.Strings import *
from pygame.locals import *
import time
import logging
import cv2

class RobotGUI:
    def showUiScreen(self, name, params):
        logger = logging.getLogger("FaceSwap.RobotGUI.showUiScreen")
        self.prev_screen = self.getCurentScreen()

        if not self.screens.has_key(name):
            logger.warning("No screen named " + name)
            raise Exception("No screen named " + name)

        cur_name = self.getCurentScreen()
        if cur_name is not None:
            if name == cur_name:
                return True

        for var in self.screens:
            self.screens[var].setVisible(False, ())

        self.screens[name].setVisible(True, params)

        logger.info("Screen " + name + " become visible")
        return True

    def regScreen(self, screen):
        self.screens[screen.name] = screen
        return True

    def getPrevScreen(self):
        return self.prev_screen

    def getCurentScreen(self):
        for var in self.screens:
            if (self.screens[var].visible):
                return self.screens[var].name
        return ""

    def init(self):
        self.screens = {}
        return True

    def updateGUI(self, event):
        for var in self.screens:
            if self.screens[var].visible:
                self.screens[var].update(event)
        return True

    def renderGUI(self):
        for var in self.screens:
            if self.screens[var].visible:
                self.screens[var].draw()

class UIScreen:
    def __init__(self, name, parent):
        self.name = name
        self.visible = False
        self.elements = {}
        self.sounds = {}
        self.render_objects = []
        self.surface = parent.surface
        self.parent = parent

    def initialize(self):
        for var in self.elements:
            self.render_objects.append(self.elements[var])

    def update(self, event):
            for var in self.elements:
                self.elements[var].update(event)

    def draw(self):
        if (self.visible):
            self.render_objects = sorted(self.render_objects, key=lambda element: element.layer)
            for var in self.render_objects:
                var.draw()

    def setVisible(self, val, params=()):
        for var in self.elements:
                self.elements[var].interact()
        self.visible = val

class UIWidget:
    def __init__(self, parent, layer):
        self.layer = layer
        self.visible = True
        self.parent = parent
        self.tweens = []

    def draw(self):
        raise NotImplementedError("pure virtual call")

    def update(self, event):
        return

    def interact(self):
        return

    def insertTween(self, uitween):
        self.tweens.append(uitween)

    def setTween(self, uitween):
        self.tweens = []
        self.tweens.append(uitween)

class UIProxySprite(UIWidget):
    def __init__(self, surface, image, parent, layer):
        UIWidget.__init__(self, parent, layer)
        self.surface = surface
        self.image = image

    def draw(self):
        if (self.visible) :
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2BGRA)
            self.surface.get_buffer().write(img.tostring())

class UISprite(UIWidget):
    def __init__(self, surface, image, x, y, parent, layer):
        UIWidget.__init__(self, parent, layer)
        self.surface = surface
        self.image = image
        self.x = x
        self.y = y

        imgrect = pygame.Surface.get_rect(image)
        w = imgrect.right - imgrect.left
        h = imgrect.bottom - imgrect.top

        self.rect = pygame.Rect(x, y, w, h)

    def update(self, event):
        for tween in self.tweens:
            tween.update()

    def draw(self):
        if (self.visible) :

            sprite = self.image
            owncenter = sprite.get_rect().center

            _dx, _dy = 0, 0
            for tween in self.tweens:
                sprite, _dx, _dy = tween.doFrame(sprite, _dx, _dy)

            center = sprite.get_rect().center

            dx = center[0] - owncenter[0] - _dx
            dy = center[1] - owncenter[1] - _dy

            self.surface.blit(sprite, (self.x - dx, self.y - dy))

def truncline(text, font, maxwidth):
        real=len(text)
        stext=text
        l=font.size(text)[0]
        cut=0
        a=0
        done=1
        old = None
        while l > maxwidth:
            a=a+1
            n=text.rsplit(None, a)[0]
            if stext == n:
                cut += 1
                stext= n[:-cut]
            else:
                stext = n
            l=font.size(stext)[0]
            real=len(stext)
            done=0
        return real, done, stext

def wrapline(text, font, maxwidth):
    done=0
    wrapped=[]

    while not done:
        nl, done, stext=truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text=text[nl:]
    return wrapped

def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)

class UIText(UIWidget):
    def __init__(self, surface, pr_string, parent, layer):
        UIWidget.__init__(self, parent, layer)
        self.tweens = []
        self.surface = surface

        pygame.font.init()
        myfont = pygame.font.SysFont(pr_string.font, pr_string.font_size, bold=pr_string.bold, italic=pr_string.italic)

        self.x = pr_string.x
        self.y = pr_string.y
        self.max_width = pr_string.line_width
        self.line_dist = pr_string.line_space

        self.lines = wrapline(pr_string.text, myfont, self.max_width)
        self.image = []
        for line in self.lines:
            self.image.append(myfont.render(line, 1, pr_string.color))

    def update(self, event):
        for tween in self.tweens :
            tween.update()

    def draw(self):
        if (self.visible) :
            i = 0
            for line in self.image:
                sprite = line
                owncenter = sprite.get_rect().center

                _dx, _dy = 0, 0
                for tween in self.tweens :
                    sprite, _dx, _dy = tween.doFrame(sprite, _dx, _dy)

                center = sprite.get_rect().center

                dx = center[0] - owncenter[0] - _dx
                dy = center[1] - owncenter[1] - _dy

                imgrect = sprite.get_rect()
                w = imgrect.right - imgrect.left
                h = imgrect.bottom - imgrect.top

                self.surface.blit(sprite, (self.x - dx, self.y - dy + i * (h + self.line_dist)))
                i += 1

    def insertTween(self, uitween):
        self.tweens.append(uitween)

class UISpriteButton(UIWidget):
    def __init__(self, name, surface, image, image_hover, x, y, button_callbacks, parent, layer, pr_string=""):
        UIWidget.__init__(self, parent, layer)
        self.sound = pygame.mixer.Sound("Sounds/chimes.wav")
        self.name = name
        self.surface = surface
        self.image = image
        self.image_hover = image_hover

        self.x = x
        self.y = y
        self.callback_dict = button_callbacks

        self.hover = False

        imgrect = pygame.Surface.get_rect(image)
        w = imgrect.right - imgrect.left
        h = imgrect.bottom - imgrect.top

        self.rect = pygame.Rect(x, y, w, h)

        self.timage = []
        if (pr_string != ""):
            pygame.font.init()
            myfont = pygame.font.SysFont(pr_string.font, pr_string.font_size, bold=pr_string.bold, italic=pr_string.italic)

            self.tx = pr_string.x
            self.ty = pr_string.y
            self.max_width = pr_string.line_width
            self.line_dist = pr_string.line_space

            self.lines = wrapline(pr_string.text, myfont, self.max_width)
            for line in self.lines:
                self.timage.append(myfont.render(line, 1, pr_string.color))

    def draw(self):
        if (self.visible) :
            if (self.hover and self.image_hover != 0) :
                sprite = self.image_hover
            else :
                sprite = self.image

            _dx, _dy = 0, 0
            for tween in self.tweens:
                sprite, _dx, _dy = tween.doFrame(sprite, _dx, _dy)

            self.surface.blit(sprite, (self.x + _dx, self.y + _dy))

            i = 0
            for line in self.timage:
                sprite = line
                owncenter = sprite.get_rect().center

                center = sprite.get_rect().center

                _dx, _dy = 0, 0
                for tween in self.tweens:
                    sprite, _dx, _dy = tween.doFrame(sprite, _dx, _dy)

                dx = center[0] - owncenter[0] + _dx
                dy = center[1] - owncenter[1] + _dy

                imgrect = sprite.get_rect()
                w = imgrect.right - imgrect.left
                h = imgrect.bottom - imgrect.top

                self.surface.blit(sprite, (self.x + self.tx - dx, self.y + self.ty - dy + i * (h + self.line_dist)))
                i += 1

    def mouse_in_rect(self, mouse):
        mx = mouse[0]
        my = mouse[1]
                 
        if mx > self.rect.topleft[0]:
            if my > self.rect.topleft[1]:
                if mx < self.rect.bottomright[0]:
                    if my < self.rect.bottomright[1]:
                        return True
        return False

    def update(self, event):
        for tween in self.tweens:
            tween.update()

        if (event == 0):
            return

        mouse = pygame.mouse.get_pos()
        if event.type == MOUSEBUTTONUP:
            if self.mouse_in_rect(mouse):
                self.sound.play()
                #time.sleep(0.3)

                if 'click' in self.callback_dict:
                    self.callback_dict['click'](self)

        elif event.type == MOUSEMOTION:
            if self.mouse_in_rect(mouse):
                hover_new = True
            else:
                hover_new = False

            if hover_new and self.hover != hover_new and 'hoverin' in self.callback_dict:
                self.callback_dict['hoverin'](self)
            if not hover_new and self.hover != hover_new and 'hoverout' in self.callback_dict:
                self.callback_dict['hoverout'](self)

            self.hover = hover_new


    def interact(self):
        self.hover = False

class UITween:
    def __init__(self):
        self.time = time.clock()
        self.dt = -1
        return

    def doFrame(self, widget, _dx, _dy):
        return widget, _dx, _dy

    def update(self):
        newtime = time.clock()
        self.dt = newtime - self.time

class UIRotate(UITween):
    def __init__(self, sec_deg):
        UITween.__init__(self)
        self.sec_deg = sec_deg

    def doFrame(self, widget, _dx, _dy):
        if (self.dt > 0) :
            angle = int(self.dt * self.sec_deg)
            return pygame.transform.rotozoom(widget, angle, 1)
        return  widget, _dx, _dy

class UIBumpEffect(UITween):
    def __init__(self, scale, delay, is_in, pow_num=0.8):
        UITween.__init__(self)
        self.scale = scale
        self.delay = delay
        self.is_in = is_in
        self.pow_num = pow_num

    def doFrame(self, widget, _dx, _dy):
        progress = max(0.0, min((self.delay - self.dt) / self.delay, 1.0))

        if self.is_in:
            progress = 1 - progress

        progress = pow(progress, self.pow_num)

        res_scale = (1 - progress) + progress * self.scale

        return pygame.transform.rotozoom(widget, 0.0, res_scale), _dx, _dy

class UITweenTranslate(UITween):
    def __init__(self, dx, dy, delay, is_in):
        UITween.__init__(self)
        self.dx = dx
        self.dy = dy
        self.delay = delay
        self.is_in = is_in

    def doFrame(self, widget, _dx, _dy):
        progress = max(0.0, min((self.delay - self.dt) / self.delay, 1.0))

        if self.is_in:
            progress = 1 - progress

        progress = pow(progress, 0.8)

        res_dx = progress * self.dx
        res_dy = progress * self.dy

        return widget, _dx + res_dx, _dy + res_dy


class UIEvent:
    def __init__(self, type, value, params):
        self.type = type
        self.value = value
        self.params = params
