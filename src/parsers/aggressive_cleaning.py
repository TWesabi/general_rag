from parsers.basic_cleaning import BasicTextCleaner, TextCleaner
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class AggressiveCleaner(TextCleaner):
    def __call__(self, raw_text: str) -> str: ...

    def _basic_cleaning(self, text: str) -> str:
        cleaner = BasicTextCleaner()
        return cleaner(text)

    def _remove_tables(self, text: str) -> str: ...

    def _remove_punctuation(self, text: str) -> str: ...
