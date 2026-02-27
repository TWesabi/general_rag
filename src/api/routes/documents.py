"""Document management endpoints."""

import logging
import time
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.chunking import Chunker
from src.embeddings import Embedder
from src.models.document import Document, DocumentChunk
from src.parsers import DoclingParser
from src.storage import WeaviateClient

from ..dependencies import get_chunker, get_embedder, get_parser, get_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    parser: DoclingParser = Depends(get_parser),
    chunker: Chunker = Depends(get_chunker),
    embedder: Embedder = Depends(get_embedder),
    storage: WeaviateClient = Depends(get_storage),
):
    """
    Upload and process a document.

    Args:
        file: Uploaded file
        parser: Document parser
        chunker: Text chunker
        embedder: Embedding generator
        storage: Weaviate storage client

    Returns:
        Document ID and processing status
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    file_type = file.filename.split(".")[-1].lower()
    if file_type != "pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_type}. Only PDF is supported currently.",
        )

    try:
        start_time = time.time()
        logger.info(f"Starting document upload: {file.filename}")

        # Read file content
        file_bytes = await file.read()
        logger.info(f"File read: {len(file_bytes)} bytes")

        # Parse document
        parse_start = time.time()
        logger.info("Starting document parsing...")
        document = parser.parse_from_bytes(file_bytes, file.filename)
        document.id = str(uuid.uuid4())
        parse_time = time.time() - parse_start
        logger.info(
            f"Parsing completed in {parse_time:.2f}s - extracted {len(document.content)} characters"
        )

        # Chunk document
        chunk_start = time.time()
        logger.info("Starting document chunking...")
        chunks = chunker.chunk_document(document)
        chunk_time = time.time() - chunk_start
        logger.info(f"Chunking completed in {chunk_time:.2f}s - created {len(chunks)} chunks")

        # Generate embeddings
        embed_start = time.time()
        logger.info(f"Starting embedding generation for {len(chunks)} chunks...")
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = embedder.embed(chunk_texts)
        embed_time = time.time() - embed_start
        logger.info(f"Embedding generation completed in {embed_time:.2f}s")

        # Store document
        store_start = time.time()
        logger.info("Storing document in Weaviate...")
        doc_id = storage.store_document(document)
        logger.info(f"Document stored with ID: {doc_id}")

        # Store chunks with embeddings
        logger.info(f"Storing {len(chunks)} chunks with embeddings...")
        storage.store_chunks(chunks, doc_id, embeddings)
        store_time = time.time() - store_start
        logger.info(f"Storage completed in {store_time:.2f}s")

        total_time = time.time() - start_time
        logger.info(
            f"Document processing completed in {total_time:.2f}s total "
            f"(parse: {parse_time:.2f}s, chunk: {chunk_time:.2f}s, embed: {embed_time:.2f}s, store: {store_time:.2f}s)"
        )

        return JSONResponse(
            content={
                "document_id": doc_id,
                "filename": file.filename,
                "chunks_count": len(chunks),
                "status": "processed",
                "processing_time": f"{total_time:.2f}s",
                "timing": {
                    "parsing": f"{parse_time:.2f}s",
                    "chunking": f"{chunk_time:.2f}s",
                    "embedding": f"{embed_time:.2f}s",
                    "storage": f"{store_time:.2f}s",
                    "total": f"{total_time:.2f}s",
                },
            },
            status_code=201,
        )
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/parse_doc")
async def parse_document(filePath: Path) -> Document:
    pass


@router.post("/store_docs")
async def store_documents(documents: List[Document]) -> dict:
    pass


@router.post("/chunking")
async def chunk_document(Document: Document) -> List[DocumentChunk]:
    pass


@router.post("/store_chunks")
async def store_chunks(chunks: List[DocumentChunk]) -> dict:
    pass


@router.post("/embed_chunks")
async def embed_chunks(chunks: List[DocumentChunk]) -> dict:
    pass


@router.post("/store_embeddings")
async def store_embeddings(embeddings: List[float]) -> dict:
    pass


@router.get("")
async def list_documents(
    limit: int = 100,
    storage: WeaviateClient = Depends(get_storage),
):
    """
    List all documents.

    Args:
        limit: Maximum number of documents to return
        storage: Weaviate storage client

    Returns:
        List of documents
    """
    try:
        documents = storage.list_documents(limit=limit)
        return {"documents": documents, "count": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    storage: WeaviateClient = Depends(get_storage),
):
    """
    Get a document by ID.

    Args:
        document_id: Document ID
        storage: Weaviate storage client

    Returns:
        Document data
    """
    document = storage.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    storage: WeaviateClient = Depends(get_storage),
):
    """
    Delete a document and all its chunks.

    Args:
        document_id: Document ID
        storage: Weaviate storage client

    Returns:
        Deletion status
    """
    success = storage.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}


@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: str) -> List[DocumentChunk]:
    pass
