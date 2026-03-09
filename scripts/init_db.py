from src.db.database import create_tables, get_session
from src.db.models import Document
from utils.logger import setup_logger

log = setup_logger(__name__)

if __name__ == "__main__":
    create_tables()
    session = get_session()
    with session as sess:
        document = Document(
            doc_name="Tariq_Test_1",
            filename="Tariq_name_1",
            binary_hash="1234abchash",
            status="cleaned",
        )
        sess.add(document)
        sess.commit()
        document = sess.query(Document).filter(Document.doc_name == "Tariq_Test").first()
        result = document.status
        log.info("%s is the status of the queried document: ", document.status)
        log.info("%s is the doc_name of the queried document: ", document.doc_name)
        log.info("%s is the binary_hash of the queried document: ", document.binary_hash)
        log.info("%s is the id of the queried document: ", document.id)
        log.info("%s is the creation time of the queried document: ", document.created_at)
        sess.close()
