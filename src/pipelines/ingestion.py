"""Document ingestion pipeline."""

import uuid
from typing import List

from zenml import pipeline, step
from zenml.logger import get_logger

from ..chunking import Chunker
from ..embeddings import Embedder
from ..parsers import DoclingParser
from ..schemas.document import Document, DocumentChunk
from ..storage import WeaviateClient

logger = get_logger(__name__)


@step
def parse_document_step(file_path: str) -> Document:
    """
    Parse a document using Docling.

    Args:
        file_path: Path to the document file

    Returns:
        Parsed document
    """
    parser = DoclingParser()
    document = parser.parse(file_path)
    document.id = str(uuid.uuid4())
    logger.info(f"Parsed document: {document.id}")
    return document


@step
def chunk_document_step(document: Document) -> List[DocumentChunk]:
    """
    Chunk a document.

    Args:
        document: Document to chunk

    Returns:
        List of document chunks
    """
    chunker = Chunker()
    chunks = chunker.chunk_document(document)
    logger.info(f"Created {len(chunks)} chunks for document {document.id}")
    return chunks


@step
def generate_embeddings_step(chunks: List[DocumentChunk]) -> List[List[float]]:
    """
    Generate embeddings for chunks.

    Args:
        chunks: List of chunks to embed

    Returns:
        List of embedding vectors
    """
    embedder = Embedder()
    chunk_texts = [chunk.content for chunk in chunks]
    embeddings = embedder.embed(chunk_texts)
    logger.info(f"Generated embeddings for {len(chunks)} chunks")
    return embeddings


@step
def store_document_step(
    document: Document, chunks: List[DocumentChunk], embeddings: List[List[float]]
) -> str:
    """
    Store document and chunks in Weaviate.

    Args:
        document: Document to store
        chunks: Document chunks
        embeddings: Chunk embeddings

    Returns:
        Document ID
    """
    storage = WeaviateClient()
    doc_id = storage.store_document(document)
    storage.store_chunks(chunks, doc_id, embeddings)
    logger.info(f"Stored document {doc_id} with {len(chunks)} chunks")
    return doc_id


@pipeline
def ingestion_pipeline(file_path: str) -> str:
    """
    Complete document ingestion pipeline.

    Args:
        file_path: Path to the document file

    Returns:
        Document ID
    """
    # Parse document
    document = parse_document_step(file_path)

    # Chunk document
    chunks = chunk_document_step(document)

    # Generate embeddings
    embeddings = generate_embeddings_step(chunks)

    # Store in Weaviate
    doc_id = store_document_step(document, chunks, embeddings)

    return doc_id
