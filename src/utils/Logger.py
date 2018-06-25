import json
import datetime

class LOGGER :
    logs = []
    def __init__(self):
        return

    @staticmethod
    def log(type, kind, message) :
        LOGGER.logs.append({"type":type, "kind":kind, "msg" : message, "time" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    @staticmethod
    def popLogJSON() :
        res = json.dumps(LOGGER.logs)
        LOGGER.logs = []
        return res