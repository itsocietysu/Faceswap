import time
import logging

class TimerProfiler:
    def __init__(self, is_printable=True):
        self.time = None
        self.is_printable = is_printable
        pass

    def start(self):
        self.time = time.clock()
        pass

    def lap(self):
        if self.time:
            new_time = time.clock()
            res = (new_time - self.time)
            self.time = new_time
            return res
        pass

    def print_lap(self, dt, msg):
        if self.is_printable:
            print(msg, "dt = %s" % str(dt))
        pass

    def log_lap(self, dt, msg):
        logger = logging.getLogger("FaceSwap.TimerProfiler.log_lap")
        if self.is_printable:
            logger.info(msg + "dt = " + str(dt))

    def stop(self):
        if self.time:
            return (time.clock() - self.time)
        pass
