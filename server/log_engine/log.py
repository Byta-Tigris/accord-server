import logging
from .handler import DatabaseLogHandler


logger = logging.Logger("database_logger")
_handler = DatabaseLogHandler()
formatter = logging.Formatter('%(module)s -%(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
_handler.setFormatter(formatter)

logger.addHandler(_handler)