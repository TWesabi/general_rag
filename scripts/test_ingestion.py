from pathlib import Path

from chunking.fixed_size_chunker import FixedSizeChunker
from src.config import settings
from src.db.chunck_repo import ChunkRepository
from src.db.database import get_session
from src.db.document_repo import DocumentRepository
from src.parsers.basic_cleaning import BasicTextCleaner
from src.parsers.parser_pdf import PdfParser
from src.pipelines.ingestion import IngestionPipeline
from src.utils.logger import setup_logger

log = setup_logger(__name__)


def main():
    file_path = Path("./docs/to_index/Test_Text.pdf")

    parser = PdfParser()
    cleaner = BasicTextCleaner()
    chunker = FixedSizeChunker(
        chunk_size=settings.CHUNKING__CHUNK_SIZE, chunk_overlap=settings.CHUNKING__CHUNK_OVERLAP
    )
    session = get_session()
    doc_repo = DocumentRepository(session=session)
    chunk_repo = ChunkRepository(session=session)

    pipeline = IngestionPipeline(
        pdf_parser=parser,
        basic_cleaner=cleaner,
        document_repo=doc_repo,
        chunk_repo=chunk_repo,
        chunker=chunker,
    )

    doc = pipeline(file_path)
    log.info("Pipeline is done! Document is %s", doc.filename)

    chunks = chunk_repo.get_by_document_id(doc.id)
    log.info("Retrieved %s chunks for document %s", len(chunks), doc.id)
    log.info("First chunk (pos %s): %s", chunks[0].position, chunks[0].content[:100])
    log.info("Last chunk (pos %s): %s", chunks[-1].position, chunks[-1].content[:100])

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
