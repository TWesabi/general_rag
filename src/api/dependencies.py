"""FastAPI dependencies."""

from src.chunking import Chunker
from src.embeddings import Embedder
from src.generation import Generator
from src.parsers import DoclingParser
from src.retrieval import Retriever
from src.storage import WeaviateClient


def get_parser() -> DoclingParser:
    """Get Docling parser instance."""
    return DoclingParser()


def get_chunker() -> Chunker:
    """Get chunker instance."""
    return Chunker()


def get_embedder() -> Embedder:
    """Get embedder instance."""
    return Embedder()


def get_storage() -> WeaviateClient:
    """Get Weaviate storage client."""
    return WeaviateClient()


def get_retriever() -> Retriever:
    """Get retriever instance."""
    return Retriever()


def get_generator() -> Generator:
    """Get LLM generator instance."""
    return Generator()
