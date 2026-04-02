from sqlalchemy.orm import Session

from src.chunking.fixed_size_chunker import BaseChunker, FixedSizeChunker
from src.chunking.recursive_chunker import RecursiveChunker
from src.config import settings
from src.db.chunck_repo import ChunkRepository
from src.db.document_repo import DocumentRepository
from src.embeddings.embedding import BaseEmbedder, OllamaEmbedder
from src.embeddings.transformer_embedding import TransformerEmbedder
from src.generation.generator import OllamaGenerator
from src.parsers.basic_cleaning import BasicTextCleaner
from src.parsers.parser_pdf import PdfParser
from src.pipelines.indexing import IndexingPipeline
from src.pipelines.ingestion import IngestionPipeline
from src.pipelines.rag import RAGPipeline
from src.retrieval.retriever import BaseRetriever, QdrantRetriever
from src.storage.vector_store import QdrantVectorStore, VectorStore


def create_embedder(provider: str = settings.EMBEDDING_PROVIDER) -> BaseEmbedder:
    if provider == "ollama":
        return OllamaEmbedder()
    elif provider == "transformer":
        return TransformerEmbedder()
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")


def create_chunker(
    chunker_type: str = settings.CHUNKER_TYPE,
    chunk_size: int = settings.CHUNKING__CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNKING__CHUNK_OVERLAP,
) -> BaseChunker:
    if chunker_type == "recursive":
        return RecursiveChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif chunker_type == "fixed":
        return FixedSizeChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    else:
        raise ValueError(f"Unknown chunker type provider: {chunker_type}")


def create_vector_store() -> VectorStore:
    embedder = create_embedder(provider=settings.EMBEDDING_PROVIDER)
    v_store = QdrantVectorStore(embedder=embedder)
    return v_store


def create_retriever(vector_store: VectorStore = None) -> BaseRetriever:
    store = vector_store or create_vector_store()
    return QdrantRetriever(vector_store=store)


def create_indexing_pipeline(
    session: Session, vector_store: VectorStore = None
) -> IndexingPipeline:
    chunk_repo = ChunkRepository(session=session)
    return IndexingPipeline(vector_store=vector_store, chunk_repo=chunk_repo)


def create_ingestion_pipeline(session: Session) -> IngestionPipeline:
    parser = PdfParser()
    cleaner = BasicTextCleaner()
    doc_repo = DocumentRepository(session=session)
    chunk_repo = ChunkRepository(session=session)
    chunker = create_chunker(chunker_type=settings.CHUNKER_TYPE)
    ingestion_pipeline = IngestionPipeline(
        pdf_parser=parser,
        basic_cleaner=cleaner,
        document_repo=doc_repo,
        chunk_repo=chunk_repo,
        chunker=chunker,
    )
    return ingestion_pipeline


def create_rag_pipeline() -> RAGPipeline:
    retriever = create_retriever()
    generator = OllamaGenerator()
    return RAGPipeline(retriever=retriever, generator=generator)
