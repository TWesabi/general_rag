from pathlib import Path

from src.db.chunck_repo import ChunkRepository
from src.db.database import get_session
from src.factory import create_ingestion_pipeline
from src.utils.logger import setup_logger

log = setup_logger(__name__)


def main():
    file_path = Path("./docs/to_index/Test_Text.pdf")

    session = get_session()
    pipeline = create_ingestion_pipeline(session=session)

    doc = pipeline(file_path)
    log.info("Pipeline is done! Document is %s", doc.filename)

    chunk_repo = ChunkRepository(session=session)
    chunks = chunk_repo.get_by_document_id(doc.id)
    log.info("Retrieved %s chunks for document %s", len(chunks), doc.id)
    log.info("First chunk (pos %s): %s", chunks[0].position, chunks[0].content[:100])
    log.info("Last chunk (pos %s): %s", chunks[-1].position, chunks[-1].content[:100])

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
