from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.chunking.fixed_size_chunker import BaseChunker
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class RecursiveChunker(BaseChunker):

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be less than Chunk size!")

    def __call__(self, text: str) -> list[str]:

        if text is None or text.strip() == "":
            raise ValueError("Text to be chunked is empty!")

        chunker = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

        chunks = chunker.split_text(text=text)
        log.info("Chunking completed Successfully!")

        return chunks
