import re
from abc import ABC, abstractmethod

from src.utils.logger import setup_logger

log = setup_logger(__name__)


class TextCleaner(ABC):
    @abstractmethod
    def __call__(self, raw_text: str) -> str: ...


class BasicTextCleaner(TextCleaner):
    def __call__(self, raw_text: str) -> str:

        if len(raw_text) == 0:
            log.warning("The raw text is empty")
            return ""

        lines = self._split_into_lines(raw_text)

        cleaned_lines = self._clean_lines_from_hashtags(lines=lines)

        joied_lines = self._join_lines(clean_lines=cleaned_lines)

        no_blanks = self._remove_extra_blank_lines(joied_lines)

        cleaned_text = self._remove_leading_trailing_spaces(no_blanks)

        return cleaned_text

    def _split_into_lines(self, text: str) -> list[str]:
        return text.split("\n")

    def _clean_lines_from_hashtags(self, lines: list[str]) -> list[str]:
        return [line.lstrip("#").strip() for line in lines]

    def _join_lines(self, clean_lines: list[str]) -> str:
        return "\n".join(clean_lines)

    def _remove_extra_blank_lines(self, text: str) -> str:
        return re.sub(r"\n{2,}", "\n\n", text)

    def _remove_leading_trailing_spaces(self, text: str) -> str:
        return text.strip()
