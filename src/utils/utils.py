from pathlib import Path

from src.utils.logger import setup_logger

log = setup_logger(__name__)


def write_content_into_text(file: Path, content: str):

    try:
        with open(file, "w") as f:
            f.write(content)
            log.info("Written %s charachter into file: %s", len(content), file)
        return file

    except OSError as e:
        log.error("Failed to write into %s file:  %s", file, e)
        raise


def read_text_from_file(file: Path) -> str:
    with open(file, "r") as f:
        return f.read()
