import logging
from logging import Logger


def setup_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(
        logging.INFO
    )  # this should not be hardcoded but set as variable so in dev we set it to DEBUG
    frmt = "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
    formatter = logging.Formatter(fmt=frmt)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
