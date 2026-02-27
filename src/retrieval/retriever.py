"""Retrieval system for RAG."""

from typing import List, Optional

from ..config import settings
from ..embeddings import Embedder
from ..models.query import RetrievedChunk
from ..storage import WeaviateClient


class Retriever:
    """Retrieval system with vector search."""

    def __init__(
        self,
        storage_client: Optional[WeaviateClient] = None,
        embedder: Optional[Embedder] = None,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ):
        """
        Initialize the retriever.

        Args:
            storage_client: Weaviate client instance
            embedder: Embedder instance
            top_k: Number of results to retrieve
            score_threshold: Minimum score threshold
        """
        self.storage = storage_client or WeaviateClient()
        self.embedder = embedder or Embedder()
        self.top_k = top_k or settings.retrieval.top_k
        self.score_threshold = score_threshold or settings.retrieval.score_threshold

    def retrieve(
        self, query: str, top_k: Optional[int] = None, filters: Optional[dict] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Query text
            top_k: Number of results to return
            filters: Additional filters

        Returns:
            List of retrieved chunks
        """
        # Generate query embedding
        query_vector = self.embedder.embed_single(query)

        # Search in Weaviate
        top_k = top_k or self.top_k
        results = self.storage.search_chunks(
            query_vector=query_vector,
            top_k=top_k,
            score_threshold=self.score_threshold,
            filters=filters,
        )

        # Convert to RetrievedChunk objects
        retrieved_chunks = []
        for result in results:
            chunk = RetrievedChunk(
                chunk_id=result["chunk_id"],
                content=result["content"],
                score=result["score"],
                metadata=result["metadata"],
                document_id=result["metadata"].get("document_id"),
            )
            retrieved_chunks.append(chunk)

        return retrieved_chunks
