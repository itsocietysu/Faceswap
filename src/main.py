from robotgui import *
from robotapp import *
import logging

if __name__ == "__main__":
  logger = logging.getLogger("FaceSwap")
  logger.setLevel(logging.INFO)

  fh = logging.FileHandler("FaceSwap.log")

  formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')

  fh.setFormatter(formatter)

  logger.addHandler(fh)

  try:
    app = RobotApp()
    app.initialize_app()
    logger.info("App initialize")
    app.run()
    logger.info("App closed")
  except Exception as e:
    logger.exception(e)
