"""Batch indexing pipeline."""

from typing import List

from zenml import pipeline, step
from zenml.logger import get_logger

from .ingestion import (
    chunk_document_step,
    generate_embeddings_step,
    parse_document_step,
    store_document_step,
)

logger = get_logger(__name__)


@step
def get_file_paths_step(directory: str) -> List[str]:
    """
    Get list of file paths from directory.

    Args:
        directory: Directory path

    Returns:
        List of file paths
    """
    from pathlib import Path

    path = Path(directory)
    file_paths = [str(f) for f in path.glob("*.pdf")]
    logger.info(f"Found {len(file_paths)} PDF files in {directory}")
    return file_paths


@pipeline
def indexing_pipeline(directory: str) -> List[str]:
    """
    Batch indexing pipeline for multiple documents.

    Args:
        directory: Directory containing documents to index

    Returns:
        List of document IDs
    """
    # Get file paths
    file_paths = get_file_paths_step(directory)

    # Process each document
    doc_ids = []
    for file_path in file_paths:
        # Parse document
        document = parse_document_step(file_path)

        # Chunk document
        chunks = chunk_document_step(document)

        # Generate embeddings
        embeddings = generate_embeddings_step(chunks)

        # Store in Weaviate
        doc_id = store_document_step(document, chunks, embeddings)
        doc_ids.append(doc_id)

    logger.info(f"Indexed {len(doc_ids)} documents")
    return doc_ids
