import logging
import logging.handlers

from app.config.settings import settings

logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)

formatter = logging.Formatter(
    "%(levelname)s: %(asctime)s, File %(filename)s (%(funcName)s), cause by:  %(message)s"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
