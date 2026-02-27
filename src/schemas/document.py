"""Document data models."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


def _get_utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class DocumentMetadata(BaseModel):
    """Metadata for a document."""

    source: str = Field(description="Source file path or identifier")
    file_type: str = Field(description="File type (e.g., pdf, docx)")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    created_at: datetime = Field(default_factory=_get_utc_now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=_get_utc_now, description="Last update timestamp")
    custom_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom metadata fields",
    )


class DocumentChunk(BaseModel):
    """A chunk of a document."""

    id: Optional[str] = Field(default=None, description="Chunk ID")
    content: str = Field(description="Chunk text content")
    chunk_index: int = Field(description="Index of chunk in document")
    start_char: Optional[int] = Field(default=None, description="Start character position")
    end_char: Optional[int] = Field(default=None, description="End character position")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")


class Document(BaseModel):
    """A parsed document."""

    id: Optional[str] = Field(default=None, description="Document ID")
    content: str = Field(description="Full document text content")
    metadata: DocumentMetadata = Field(description="Document metadata")
    chunks: list[DocumentChunk] = Field(default_factory=list, description="Document chunks")
    raw_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw parsed data from parser",
    )
