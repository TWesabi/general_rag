"""Text chunking implementation."""

from enum import Enum
from typing import List

from src.config import settings
from src.models import Document, DocumentChunk


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""

    RECURSIVE = "recursive"
    FIXED = "fixed"


class Chunker:
    """Text chunker with configurable strategies."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
    ):
        """
        Initialize the chunker.

        Args:
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
            strategy: Chunking strategy to use
        """
        self.chunk_size = chunk_size or settings.chunking.size
        self.chunk_overlap = chunk_overlap or settings.chunking.overlap
        self.strategy = strategy

    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """
        Chunk a document into smaller pieces.

        Args:
            document: Document to chunk

        Returns:
            List of document chunks
        """
        if self.strategy == ChunkingStrategy.RECURSIVE:
            return self._recursive_chunk(document)
        elif self.strategy == ChunkingStrategy.FIXED:
            return self._fixed_chunk(document)
        else:
            raise ValueError(f"Unknown chunking strategy: {self.strategy}")

    def _recursive_chunk(self, document: Document) -> List[DocumentChunk]:
        """Recursive chunking strategy."""
        chunks = []
        text = document.content

        # Safety check
        if not text or len(text) == 0:
            return chunks

        start = 0
        chunk_index = 0
        max_iterations = (len(text) // max(1, self.chunk_size - self.chunk_overlap)) + 100
        iterations = 0

        while start < len(text):
            iterations += 1
            if iterations > max_iterations:
                raise ValueError(
                    f"Infinite loop detected in chunking. "
                    f"start={start}, text_len={len(text)}, "
                    f"chunk_size={self.chunk_size}, overlap={self.chunk_overlap}"
                )

            # Calculate end position
            end = min(start + self.chunk_size, len(text))

            # Extract chunk
            chunk_text = text[start:end]

            # Create chunk
            chunk = DocumentChunk(
                content=chunk_text,
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                metadata={
                    "document_id": document.id,
                    "source": document.metadata.source,
                    "file_type": document.metadata.file_type,
                },
            )
            chunks.append(chunk)

            # Move start position with overlap
            new_start = end - self.chunk_overlap

            # Prevent infinite loop - ensure we always make progress
            if new_start <= start:
                new_start = start + 1

            start = new_start
            chunk_index += 1

        return chunks

    def _fixed_chunk(self, document: Document) -> List[DocumentChunk]:
        """Fixed-size chunking strategy."""
        chunks = []
        text = document.content

        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i : i + self.chunk_size]
            if not chunk_text.strip():
                continue

            chunk = DocumentChunk(
                content=chunk_text,
                chunk_index=len(chunks),
                start_char=i,
                end_char=min(i + len(chunk_text), len(text)),
                metadata={
                    "document_id": document.id,
                    "source": document.metadata.source,
                    "file_type": document.metadata.file_type,
                },
            )
            chunks.append(chunk)

        return chunks
