"""Document data models."""

import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentStatus(str, enum.Enum):
    PARSED = "parsed"
    CLEANED = "cleaned"
    CHUNKED = "chunked"
    EMBEDDED = "embedded"
    FAILED = "failed"
    SUCCESS = "Success"


class ChunkSchema(BaseModel):
    """A chunk of a document."""

    content: str = Field(description="Chunk text content")
    position: int = Field(description="Index of chunk in document")
    hints: str | None = Field(
        default=None, description="Info that suppliments the chunck in generation phase"
    )
    has_table: bool = Field(default=False, description="if the chunk has table content")
    has_image: bool = Field(default=False, description="if the chunck is acullay an image content")


class DocumentMetadata(BaseModel):
    """Metadata for a document."""

    local_path: Optional[str] = Field(description="Source file path")
    status: Optional[DocumentStatus] = Field(description="Status of the document in the pipeline")
    timestamp: Optional[datetime] = Field(description="Time of parsing")
    num_pages: Optional[int] = Field(description="Numger of pages in the docuemtn")
    table_count: Optional[int] = Field(description="How many table in the doc")
    has_tables: Optional[bool] = Field(default=False, description="Does it have tables")
    filename: Optional[str] = Field(description="the origina file name of the pdf ")
    mimetype: Optional[str] = Field(
        description="The media type of the docuemtn parsed",
    )


class DocumentSchema(BaseModel):
    """A parsed document."""

    doc_name: str = Field(description="Name of parsed docuemtn")
    raw_text: str = Field(description="Full document text content")
    metadata: Optional[DocumentMetadata] = Field(description="Document metadata")
    binary_hash: str = Field(description="a unique hash of the parsed document")
    chunks: Optional[list[ChunkSchema]] = Field(description="Document chunks")
    clean_text: Optional[str] = Field(
        default=None,
        description="Cleaned parsed text from cleaner",
    )
