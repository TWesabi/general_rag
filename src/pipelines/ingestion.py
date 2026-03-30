from pathlib import Path

from chunking.fixed_size_chunker import BaseChunker
from src.db.chunck_repo import ChunkRepository
from src.db.document_repo import DocumentRepository
from src.db.models import Document
from src.parsers.basic_cleaning import TextCleaner
from src.parsers.parser_pdf import DocumentParser
from src.schemas.document import ChunkSchema
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class IngestionPipeline:
    def __init__(
        self,
        pdf_parser: DocumentParser,
        basic_cleaner: TextCleaner,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        chunker: BaseChunker,
    ):
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.basic_cleaner = basic_cleaner
        self.pdf_parser = pdf_parser
        self.chunker = chunker

    def __call__(self, path: Path) -> Document:
        log.info("Starting ingestion for %s", path)
        parsed_doc = self.pdf_parser(file_path=path)
        log.info("Parsed %s — %s pages", parsed_doc.doc_name, parsed_doc.metadata.num_pages)
        parsed_doc.clean_text = self.basic_cleaner(parsed_doc.raw_text)
        log.info("Text cleaned for %s", parsed_doc.doc_name)
        chuncks_txt = self.chunker(parsed_doc.clean_text)
        chunks = self._build_chunk_schemas(chuncks_txt)
        db_doc = self.document_repo.from_document_schema(parsed_doc)
        existing = self.document_repo.get_by_hash(db_doc.binary_hash)
        if existing:
            log.info(
                "Document %s already ingested (id %s), skipping.", existing.filename, existing.id
            )
            return existing
        written_doc = self.document_repo.add(db_doc)
        db_chunks = self.chunk_repo.from_chunks_schema(chunks, written_doc.id)
        self.chunk_repo.add_batch(db_chunks)

        log.info(
            "Ingestion of %s Chunks complete for %s — stored with id %s",
            len(db_chunks),
            written_doc.doc_name,
            written_doc.id,
        )
        return written_doc

    def _build_chunk_schemas(self, raw_chunks: list[str]) -> list[ChunkSchema]:
        return [ChunkSchema(content=text, position=i) for i, text in enumerate(raw_chunks)]
