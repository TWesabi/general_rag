from abc import ABC, abstractmethod

from src.utils.logger import setup_logger

log = setup_logger(__name__)


class BaseChunker(ABC):
    @abstractmethod
    def __call__(self, text: str) -> list[str]: ...


class FixedSizeChunker(BaseChunker):

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.step_size = self.chunk_size - self.chunk_overlap

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Chunk overlap must be smaller than Chunk Size!")

    def __call__(self, text: str) -> list[str]:
        chunks: list[str] = []

        if text is None or text.strip() == "":
            raise ValueError("Text to be chunked is empty!")

        start = 0
        while start < len(text):
            chunk_text = text[start : start + self.chunk_size]
            chunks.append(chunk_text)
            start += self.step_size

        log.info("Chunking is compelted successfully! Number of chunks is %s", len(chunks))
        return chunks
