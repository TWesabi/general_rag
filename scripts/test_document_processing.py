"""Test script to debug document processing pipeline."""

import logging
import sys
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_system.chunking import Chunker  # noqa: E402
from rag_system.embeddings import Embedder  # noqa: E402
from rag_system.parsers import DoclingParser  # noqa: E402
from rag_system.storage import WeaviateClient  # noqa: E402


def test_parser(file_path: str):
    """Test document parsing."""
    logger.info("=" * 60)
    logger.info("TEST 1: Document Parsing")
    logger.info("=" * 60)

    start = time.time()
    try:
        logger.info("Initializing parser...")
        parser = DoclingParser()
        init_time = time.time() - start
        logger.info(f"Parser initialized in {init_time:.2f}s")

        logger.info(f"Parsing file: {file_path}")
        parse_start = time.time()
        document = parser.parse(file_path)
        parse_time = time.time() - parse_start

        logger.info(f"✓ Parsing completed in {parse_time:.2f}s")
        logger.info(f"  - Extracted {len(document.content)} characters")
        logger.info(f"  - File type: {document.metadata.file_type}")
        logger.info(f"  - File size: {document.metadata.file_size} bytes")

        # Check if content is suspiciously large
        if len(document.content) > 1000000:  # 1MB of text
            logger.warning(
                f"⚠ WARNING: Very large document content: {len(document.content)} characters"
            )
            logger.warning("  This might cause slow chunking. Checking first 1000 chars...")
            logger.info(f"  First 1000 chars: {document.content[:1000]}")
        elif len(document.content) == 0:
            logger.warning("⚠ WARNING: Document content is empty!")

        return document
    except Exception as e:
        logger.error(f"✗ Parsing failed: {e}", exc_info=True)
        return None


def test_chunking(document):
    """Test document chunking."""
    logger.info("=" * 60)
    logger.info("TEST 2: Document Chunking")
    logger.info("=" * 60)

    start = time.time()
    try:
        logger.info("Initializing chunker...")
        chunker = Chunker()
        init_time = time.time() - start
        logger.info(f"Chunker initialized in {init_time:.2f}s")
        logger.info(f"  - Chunk size: {chunker.chunk_size}")
        logger.info(f"  - Chunk overlap: {chunker.chunk_overlap}")
        logger.info(f"  - Strategy: {chunker.strategy}")

        logger.info(f"Document content length: {len(document.content)} characters")
        logger.info("Starting chunking...")
        chunk_start = time.time()

        # Add progress logging for long operations
        import threading

        def log_progress():
            elapsed = 0
            while True:
                time.sleep(5)
                elapsed += 5
                logger.info(f"  ... still chunking (elapsed: {elapsed}s)")

        progress_thread = threading.Thread(target=log_progress, daemon=True)
        progress_thread.start()

        chunks = chunker.chunk_document(document)
        chunk_time = time.time() - chunk_start

        logger.info(f"✓ Chunking completed in {chunk_time:.2f}s")
        logger.info(f"  - Created {len(chunks)} chunks")
        if chunks:
            logger.info(f"  - First chunk length: {len(chunks[0].content)} chars")
            logger.info(f"  - Last chunk length: {len(chunks[-1].content)} chars")

        return chunks
    except Exception as e:
        logger.error(f"✗ Chunking failed: {e}", exc_info=True)
        return None


def test_embeddings(chunks):
    """Test embedding generation."""
    logger.info("=" * 60)
    logger.info("TEST 3: Embedding Generation")
    logger.info("=" * 60)

    start = time.time()
    try:
        logger.info("Initializing embedder (this may download models on first run)...")
        embedder = Embedder()
        init_time = time.time() - start
        logger.info(f"Embedder initialized in {init_time:.2f}s")

        if not chunks:
            logger.warning("No chunks to embed")
            return None

        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embed_start = time.time()
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = embedder.embed(chunk_texts)
        embed_time = time.time() - embed_start

        logger.info(f"✓ Embedding generation completed in {embed_time:.2f}s")
        logger.info(f"  - Generated {len(embeddings)} embeddings")
        if embeddings:
            logger.info(f"  - Embedding dimension: {len(embeddings[0])}")
            logger.info(f"  - Average time per chunk: {embed_time/len(chunks):.3f}s")

        return embeddings
    except Exception as e:
        logger.error(f"✗ Embedding generation failed: {e}", exc_info=True)
        return None


def test_storage(document, chunks, embeddings):
    """Test Weaviate storage."""
    logger.info("=" * 60)
    logger.info("TEST 4: Weaviate Storage")
    logger.info("=" * 60)

    start = time.time()
    try:
        logger.info("Connecting to Weaviate...")
        storage = WeaviateClient()
        connect_time = time.time() - start
        logger.info(f"✓ Connected to Weaviate in {connect_time:.2f}s")

        if not chunks or not embeddings:
            logger.warning("Skipping storage test - no chunks/embeddings")
            return None

        import uuid

        document.id = str(uuid.uuid4())

        logger.info("Storing document...")
        store_doc_start = time.time()
        doc_id = storage.store_document(document)
        store_doc_time = time.time() - store_doc_start
        logger.info(f"✓ Document stored in {store_doc_time:.2f}s")
        logger.info(f"  - Document ID: {doc_id}")

        logger.info(f"Storing {len(chunks)} chunks...")
        store_chunks_start = time.time()
        chunk_ids = storage.store_chunks(chunks, doc_id, embeddings)
        store_chunks_time = time.time() - store_chunks_start
        logger.info(f"✓ Chunks stored in {store_chunks_time:.2f}s")
        logger.info(f"  - Stored {len(chunk_ids)} chunks")

        return doc_id
    except Exception as e:
        logger.error(f"✗ Storage failed: {e}", exc_info=True)
        return None


def main():
    """Main test function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_document_processing.py <path_to_pdf>")
        print("\nExample:")
        print("  python scripts/test_document_processing.py test.pdf")
        sys.exit(1)

    file_path = sys.argv[1]

    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Document Processing Pipeline Test")
    logger.info("=" * 60)
    logger.info(f"File: {file_path}")
    logger.info("")

    total_start = time.time()

    # Test each step
    document = test_parser(file_path)
    if not document:
        logger.error("Parsing failed, stopping tests")
        sys.exit(1)

    logger.info("")
    chunks = test_chunking(document)
    if not chunks:
        logger.error("Chunking failed, stopping tests")
        sys.exit(1)

    logger.info("")
    embeddings = test_embeddings(chunks)
    if not embeddings:
        logger.error("Embedding generation failed, stopping tests")
        sys.exit(1)

    logger.info("")
    doc_id = test_storage(document, chunks, embeddings)

    total_time = time.time() - total_start

    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total processing time: {total_time:.2f}s")
    if doc_id:
        logger.info("✓ Document successfully processed and stored!")
        logger.info(f"  Document ID: {doc_id}")
    else:
        logger.warning("⚠ Document processed but not stored (storage test skipped/failed)")


if __name__ == "__main__":
    main()
