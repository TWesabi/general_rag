from src.utils.logger import setup_logger

log = setup_logger(__name__)

log.info("This is info")
log.debug("This is debug")
log.warning("This is a warning")
log.error("This is an error")
