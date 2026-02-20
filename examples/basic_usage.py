"""Basic usage example for the RAG system."""

import asyncio
from pathlib import Path

from rag_system.chunking import Chunker
from rag_system.embeddings import Embedder
from rag_system.generation import Generator
from rag_system.parsers import DoclingParser
from rag_system.retrieval import Retriever
from rag_system.storage import WeaviateClient


async def main():
    """Basic usage example."""
    print("RAG System - Basic Usage Example")
    print("=" * 50)

    # Initialize components
    print("\n1. Initializing components...")
    parser = DoclingParser()
    chunker = Chunker()
    embedder = Embedder()
    storage = WeaviateClient()
    retriever = Retriever()
    generator = Generator()

    # Example: Process a document
    print("\n2. Processing document...")
    # Replace with actual PDF path
    # pdf_path = "path/to/your/document.pdf"
    # document = parser.parse(pdf_path)
    # chunks = chunker.chunk_document(document)
    # embeddings = embedder.embed([chunk.content for chunk in chunks])
    # doc_id = storage.store_document(document)
    # storage.store_chunks(chunks, doc_id, embeddings)
    # print(f"Document stored with ID: {doc_id}")

    # Example: Query the system
    print("\n3. Querying the system...")
    query = "What is the main topic of the document?"
    retrieved_chunks = retriever.retrieve(query, top_k=3)
    print(f"Retrieved {len(retrieved_chunks)} chunks")

    # Generate answer
    print("\n4. Generating answer...")
    context = "\n\n".join([chunk.content for chunk in retrieved_chunks])
    answer = await generator.generate(query, context=context)
    print(f"Answer: {answer}")

    print("\nExample completed!")


if __name__ == "__main__":
    asyncio.run(main())
