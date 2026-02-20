"""Query data models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """A retrieved chunk with relevance score."""

    chunk_id: str = Field(description="Chunk ID")
    content: str = Field(description="Chunk content")
    score: float = Field(description="Relevance score")
    metadata: dict = Field(default_factory=dict, description="Chunk metadata")
    document_id: Optional[str] = Field(default=None, description="Source document ID")


class QueryRequest(BaseModel):
    """Query request model."""

    query: str = Field(description="User query text")
    top_k: Optional[int] = Field(default=None, description="Number of results to return")
    score_threshold: Optional[float] = Field(
        default=None,
        description="Minimum score threshold",
    )
    include_metadata: bool = Field(default=True, description="Include metadata in response")
    filters: Optional[dict] = Field(default=None, description="Additional filters")


class QueryResponse(BaseModel):
    """Query response model."""

    query: str = Field(description="Original query")
    retrieved_chunks: List[RetrievedChunk] = Field(description="Retrieved chunks")
    answer: Optional[str] = Field(default=None, description="Generated answer")
    metadata: dict = Field(default_factory=dict, description="Response metadata")
