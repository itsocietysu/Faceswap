#import syslog
import pygame
from distutils.util import strtobool
import os

from collections import deque

from pygame.locals import *
from robotgui import *
from UIScreens.UIMain import *
from UIScreens.UIInfo import *
from UIScreens.UIError import *
from UIScreens.UICapture import *
from UIScreens.UIPrint import *

from utils.Settings import *
from WebCam.Capture import *
from WebCam.FaceSwapEffect import *
from StateMachine.Storage import storage

# TODO: move logger from utils
from utils.TimerProfiler import *

import logging

logger = logging.getLogger("FaceSwap")

class RobotApp:
    def __init__(self):
        logger = logging.getLogger("FaceSwap.RobotApp.__init__")
        try:
            self.upload_initial_data()
            self.storage = storage
            if strtobool(self.settings.PRINT_FONTS):
                fonts = pygame.font.get_fonts()
                logger.info("Fonts " + str(fonts))
            self.w = int(self.settings.WIDTH)
            self.h = int(self.settings.HEIGHT)
            pygame.init()
            pygame.display.set_mode((self.w, self.h),
                                    FULLSCREEN if not strtobool(self.settings.FRAME) else 0)

            if not strtobool(self.settings.CURSOR):
                pygame.mouse.set_cursor((8, 8),
                                        (0, 0),
                                        (0, 0, 0, 0, 0, 0, 0, 0),
                                        (0, 0, 0, 0, 0, 0, 0, 0))

            self.surface = pygame.display.get_surface()
            self.gui = RobotGUI()
            logger.info("RobotGUI initialize")
            self.events = []
            self.camera = Capture()
            logger.info("Capture initialize")
            self.swapper = FaseSwapEffect(self.camera)
            logger.info("FaseSwapEffect initialize")
            #self.swapper.set_active(True)
            self.sleeper_thread = deque()
            self.sleeper_time = int(self.settings.TIME_SLEEP)
            self.filter = []
            for i in xrange(0, 5):
                self.filter.append({
                    'name':       self.filters["FILTER%s_NAME" % str(i)],
                    'contrast':   self.filters["FILTER%s_CONTRAST" % str(i)],
                    'brighness':  self.filters["FILTER%s_BRIGHNESS" % str(i)],
                    'warm':       self.filters["FILTER%s_WARM" % str(i)],
                    'saturation': self.filters["FILTER%s_SATURATION" % str(i)],
                    'sharpen':    self.filters["FILTER%s_SHARPEN" % str(i)]
                })
            self.filter_id = 0
        except Exception as e:
            logger.exception("RobotApp doesn't initialize")
            raise Exception("RobotApp doesn't initialize")


    def upload_initial_data(self):
        logger = logging.getLogger("FaceSwap.RobotApp.upload_initial_data")
        try:
            self.settings = Settings("data/settings.txt")
            logger.info("upload data/settings.txt")

            self.strings = Strings("data/strings.txt")
            logger.info("upload data/strings.txt")

            self.filters = Settings("data/filters.txt")
            logger.info("upload data/filters.txt")
        except Exception as e:
            logger.exception(e)
            raise Exception(e)

    def initialize_app(self):
        logger = logging.getLogger("FaceSwap.RobotApp.initialize_app")
        try:
            self.gui.init()
            # guiscreens
            # TODO: Need to remove hardcoded sleeper
            self.sleep_timeout = self.settings.SLEEP_TIME
            self.lastActionTime = 0
            screens = [UIMain("main", self), UICapture("capture", self), UIPrint("print", self), UIInfo("info", self), UIError("error", self)]
            for elem in screens:
                elem.initialize()
                self.gui.regScreen(elem)
            self.gui.showUiScreen("main", 0)
        except Exception as e:
            logger.exception(e)
            raise Exception(e)

    def run(self):
        logger = logging.getLogger("FaceSwap.RobotApp.run")

        timer = TimerProfiler(False)
        timer.start()
        revfps = 1.0 / 30.0
        cur_time = time.clock()
        done = False

        while not done:
            try:
                updated_gui = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        break
                    elif event.type == pygame.KEYDOWN:
                        pressed = pygame.key.get_pressed()
                        if pressed[pygame.K_w] and pressed[pygame.K_e] and pressed[pygame.K_d]:
                            self.getLastLogs()
                            done = True
                            break
                    else:
                        self.lastActionTime = time.clock()
                        updated_gui = True
                        self.update(event)

                if not updated_gui:
                    self.update(0)

                # TODO: Need to implement normal render requester
                newtime = time.clock()
                if newtime - cur_time > revfps:
                    cur_time = newtime
                    self.draw()
                timer.log_lap(timer.lap(), "cycle")
            except Exception as e:
                logger.exception(e)
                raise Exception(e)

    def update(self, event):
        try:
            self.gui.updateGUI(event)
            self.handleEvents()
        except Exception as e:
            logger = logging.getLogger("FaceSwap.RobotApp.run")
            logger.exception(e)

            raise Exception(e)

    def draw(self):
        try:
            timer = TimerProfiler(False)
            timer.start()
            self.surface.fill((255, 255, 255))
            timer.log_lap(timer.lap(), "Clear screen")
            self.gui.renderGUI()
            timer.log_lap(timer.lap(), "Render gui")
            pygame.display.flip()
            timer.log_lap(timer.lap(), "Flip")
        except Exception as e:
            logger = logging.getLogger("FaceSwap.RobotApp.draw")
            logger.exception(e)

            raise Exception(e)

    def postEvent(self, event):
        self.events.append(event)

    def startSleeper(self):
        logger = logging.getLogger("FaceSwap.RobotApp.startSleeper")
        temp = threading.Timer(self.sleeper_time, self.EventSleeper)
        self.sleeper_thread.append(temp)

        temp.start()
        logger.info("Thread Start")

    def EventSleeper(self):
        print len(self.sleeper_thread)
        self.sleeper_thread.popleft()
        print len(self.sleeper_thread)
        if len(self.sleeper_thread) != 0:
            return

        logger = logging.getLogger("FaceSwap.RobotApp.EventSleeper")
        self.storage.current_scientist_id = -1
        self.postEvent(UIEvent("show", "main", 0))
        logger.info("Thread finish")

    def handleButtonEvent(self, event):
        logger = logging.getLogger("FaceSwap.RobotApp.handleButtonEvent")
        try:
            def capture(params):
                self.gui.showUiScreen("capture", 0)

            def info(params):
                self.gui.showUiScreen("info", 0)

            def back_to_main(params):
                self.gui.showUiScreen("main", 0)


            dispatchers = {
                "main": {
                    "photo": capture,
                    "info":  info,
                },
                "info": {
                    "exit": back_to_main,
                },
                "print": {
                    "exit": back_to_main,
                    "print": back_to_main,
                },
            }

            path = event.value.split('.')
            parent = path[0]
            obj = path[1]

            if parent in dispatchers and obj in dispatchers[parent]:
                dispatchers[parent][obj](event.params)
            else:
                logger.warning("No dispatcher for button with name: " + str(event.value))
        except Exception as e:
            logger.exception(e)

            raise Exception(e)

    def handleErrorEvent(self, event):
        return

    def handleShowScreen(self, event):
        self.gui.showUiScreen(event.value, 0)

    def handleEvents(self):
        logger = logging.getLogger("FaceSwap.RobotApp.handleEvents")
        type_event_handlers = {
            "button": self.handleButtonEvent,
            "error":  self.handleErrorEvent,
            "show": self.handleShowScreen,
        }
        while len(self.events):
            event = self.events.pop()
            logger.info(event)

            if event.type in type_event_handlers:
                type_event_handlers[event.type](event)
            else:
                logger.exception("No dispatcher for event type: " + str(event.type))
                raise Exception("No dispatcher for event type: %s", event.type)

    # TODO: Make an normal click events
    def buttonClicked(self, button):
        logger = logging.getLogger("FaceSwap.RobotApp.buttonClicked")
        self.postEvent(UIEvent("button", button.parent.name + '.' + button.name, ()))
        self.startSleeper()

        logger.info("Button with name = " + button.name + " was clicked")

    def getLastLogs(self):
        return ""

