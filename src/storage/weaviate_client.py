"""Weaviate client wrapper for document and chunk storage."""

import uuid
from typing import Any, Dict, List, Optional

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.init import Auth

from ..config import settings
from ..models.document import Document, DocumentChunk


class WeaviateClient:
    """Weaviate client wrapper for RAG system."""

    DOCUMENT_CLASS = "Document"
    CHUNK_CLASS = "Chunk"

    def __init__(self):
        """Initialize Weaviate client using v v4 API."""
        # Parse URL to get host and port
        from urllib.parse import urlparse

        parsed_url = urlparse(settings.weaviate.url)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or 8080
        is_secure = parsed_url.scheme == "https"

        # Set up authentication if needed
        auth_credentials = None
        if settings.weaviate.api_key:
            auth_credentials = Auth.api_key(api_key=settings.weaviate.api_key)

        # Connect using v4 API
        try:
            if host in ("localhost", "127.0.0.1", "0.0.0.0") and port == 8080:
                # For local connections on default port, use connect_to_local
                # Only pass grpc_port if use_grpc is True (don't pass None)
                if settings.weaviate.use_grpc:
                    self.client = weaviate.connect_to_local(
                        grpc_port=50051,
                        auth_credentials=auth_credentials,
                    )
                else:
                    # Don't pass grpc_port when not using gRPC
                    self.client = weaviate.connect_to_local(
                        auth_credentials=auth_credentials,
                    )
            else:
                # Use custom connection for non-standard port or remote hosts
                # Only pass grpc_port if use_grpc is True
                if settings.weaviate.use_grpc:
                    self.client = weaviate.connect_to_custom(
                        http_host=host,
                        http_port=port,
                        http_secure=is_secure,
                        grpc_host=host,
                        grpc_port=50051,
                        grpc_secure=False,
                        auth_credentials=auth_credentials,
                    )
                else:
                    # Don't pass grpc_port when not using gRPC
                    self.client = weaviate.connect_to_custom(
                        http_host=host,
                        http_port=port,
                        http_secure=is_secure,
                        auth_credentials=auth_credentials,
                    )

            # Initialize schema
            self._initialize_schema()
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to Weaviate at {settings.weaviate.url}. "
                f"Make sure Weaviate is running. Error: {e}"
            )

    def _initialize_schema(self):
        """Initialize Weaviate schema for documents and chunks using v4 API."""
        # Check if collections already exist
        if self.client.collections.exists(self.DOCUMENT_CLASS):
            return

        # Single-node: replication factor 1 avoids "leader not found" / consistency errors
        replication = Configure.replication(factor=1)

        # Create Document collection
        try:
            self.client.collections.create(
                name=self.DOCUMENT_CLASS,
                description="Document metadata",
                replication_config=replication,
                properties=[
                    Property(
                        name="content", data_type=DataType.TEXT, description="Full document content"
                    ),
                    Property(
                        name="source", data_type=DataType.TEXT, description="Source file path"
                    ),
                    Property(name="file_type", data_type=DataType.TEXT, description="File type"),
                    Property(
                        name="file_size", data_type=DataType.INT, description="File size in bytes"
                    ),
                    Property(
                        name="created_at", data_type=DataType.DATE, description="Creation timestamp"
                    ),
                ],
            )
        except Exception:
            # Collection might already exist
            pass

        # Create Chunk collection (with vector support)
        # Default embedding dimension (all-MiniLM-L6-v2 is 384)
        # This will be set when first vector is inserted if needed
        try:
            self.client.collections.create(
                name=self.CHUNK_CLASS,
                description="Document chunks with embeddings",
                replication_config=replication,
                vector_config=Configure.VectorConfig.none(
                    vector_index_config=Configure.VectorIndex.hnsw()  # Use HNSW index
                ),  # We provide vectors ourselves
                properties=[
                    Property(
                        name="content", data_type=DataType.TEXT, description="Chunk text content"
                    ),
                    Property(
                        name="chunk_index",
                        data_type=DataType.INT,
                        description="Index of chunk in document",
                    ),
                    Property(
                        name="document_id",
                        data_type=DataType.TEXT,
                        description="ID of parent document",
                    ),
                    Property(
                        name="source", data_type=DataType.TEXT, description="Source file path"
                    ),
                    Property(name="file_type", data_type=DataType.TEXT, description="File type"),
                    Property(
                        name="start_char",
                        data_type=DataType.INT,
                        description="Start character position",
                    ),
                    Property(
                        name="end_char",
                        data_type=DataType.INT,
                        description="End character position",
                    ),
                ],
            )
        except Exception:
            # Collection might already exist
            pass

    def store_document(self, document: Document) -> str:
        """
        Store a document in Weaviate.

        Args:
            document: Document to store

        Returns:
            Document ID
        """
        doc_id = document.id or str(uuid.uuid4())

        # Format date as RFC3339 (required by Weaviate)
        # RFC3339 requires timezone - use UTC if naive datetime
        created_at = document.metadata.created_at
        if created_at.tzinfo is None:
            from datetime import timezone

            created_at = created_at.replace(tzinfo=timezone.utc)
        rfc3339_date = created_at.isoformat()

        properties = {
            "content": document.content,
            "source": document.metadata.source,
            "file_type": document.metadata.file_type,
            "file_size": document.metadata.file_size,
            "created_at": rfc3339_date,
        }

        collection = self.client.collections.get(self.DOCUMENT_CLASS)
        collection.data.insert(
            uuid=doc_id,
            properties=properties,
        )

        return doc_id

    def store_chunks(
        self, chunks: List[DocumentChunk], document_id: str, vectors: List[List[float]]
    ) -> List[str]:
        """
        Store document chunks with their embeddings.

        Args:
            chunks: List of chunks to store
            document_id: ID of parent document
            vectors: Embedding vectors for each chunk

        Returns:
            List of chunk IDs
        """
        chunk_ids = []
        collection = self.client.collections.get(self.CHUNK_CLASS)

        for chunk, vector in zip(chunks, vectors):
            chunk_id = chunk.id or str(uuid.uuid4())

            properties = {
                "content": chunk.content,
                "chunk_index": chunk.chunk_index,
                "document_id": document_id,
                "source": chunk.metadata.get("source", ""),
                "file_type": chunk.metadata.get("file_type", ""),
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
            }

            collection.data.insert(
                uuid=chunk_id,
                properties=properties,
                vector=vector,
            )

            chunk_ids.append(chunk_id)

        return chunk_ids

    def search_chunks(
        self,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filters: Additional filters

        Returns:
            List of matching chunks with metadata
        """
        collection = self.client.collections.get(self.CHUNK_CLASS)

        # Build filter if provided (Weaviate v4 uses "filters" not "where")
        filter_obj = None
        if filters:
            filter_obj = self._build_where_filter(filters)

        # Perform vector search
        kwargs = dict(
            near_vector=query_vector,
            limit=top_k,
            return_metadata=["distance"],
        )
        if filter_obj is not None:
            kwargs["filters"] = filter_obj
        response = collection.query.near_vector(**kwargs)

        chunks = []
        for obj in response.objects:
            # Convert distance to similarity score
            distance = obj.metadata.distance if obj.metadata and obj.metadata.distance else 1.0
            score = max(0.0, 1.0 - distance)  # Simple conversion

            if score >= score_threshold:
                doc_id = obj.properties.get("document_id")
                chunks.append(
                    {
                        "chunk_id": str(obj.uuid),
                        "content": obj.properties.get("content", ""),
                        "score": score,
                        "metadata": {
                            "chunk_index": obj.properties.get("chunk_index"),
                            "document_id": str(doc_id) if doc_id is not None else None,
                            "source": obj.properties.get("source"),
                            "file_type": obj.properties.get("file_type"),
                        },
                    }
                )

        return chunks

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document data or None if not found
        """
        try:
            collection = self.client.collections.get(self.DOCUMENT_CLASS)
            obj = collection.data.fetch_by_id(uuid=document_id)
            if obj:
                return {
                    "id": str(obj.uuid),
                    "content": obj.properties.get("content"),
                    "source": obj.properties.get("source"),
                    "file_type": obj.properties.get("file_type"),
                    "file_size": obj.properties.get("file_size"),
                    "created_at": obj.properties.get("created_at"),
                }
            return None
        except Exception:
            return None

    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all documents.

        Args:
            limit: Maximum number of documents to return

        Returns:
            List of documents
        """
        collection = self.client.collections.get(self.DOCUMENT_CLASS)
        response = collection.query.fetch_objects(limit=limit)

        documents = []
        for obj in response.objects:
            documents.append(
                {
                    "id": str(obj.uuid),
                    "source": obj.properties.get("source"),
                    "file_type": obj.properties.get("file_type"),
                    "file_size": obj.properties.get("file_size"),
                    "created_at": obj.properties.get("created_at"),
                }
            )

        return documents

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks.

        Args:
            document_id: Document ID

        Returns:
            True if successful, False otherwise
        """
        try:
            chunk_collection = self.client.collections.get(self.CHUNK_CLASS)
            doc_collection = self.client.collections.get(self.DOCUMENT_CLASS)

            # First, delete all chunks for this document
            chunks_response = chunk_collection.query.fetch_objects(
                where={
                    "path": ["document_id"],
                    "operator": "Equal",
                    "valueText": document_id,
                },
                limit=1000,  # Adjust if you have more chunks per document
            )

            for chunk_obj in chunks_response.objects:
                chunk_collection.data.delete_by_id(uuid=chunk_obj.uuid)

            # Delete the document
            doc_collection.data.delete_by_id(uuid=document_id)
            return True
        except Exception:
            return False

    def _build_where_filter(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build Weaviate where filter from dictionary.

        Args:
            filters: Filter dictionary

        Returns:
            Weaviate where filter or None
        """
        if not filters:
            return None

        # Simple implementation - can be extended
        conditions = []
        for key, value in filters.items():
            conditions.append({"path": [key], "operator": "Equal", "valueText": str(value)})

        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return {"operator": "And", "operands": conditions}

        return None

    def __del__(self):
        """Close connection when client is destroyed."""
        if hasattr(self, "client"):
            try:
                self.client.close()
            except Exception:
                pass
