from src.db.database import create_tables
from utils.logger import setup_logger

log = setup_logger(__name__)

if __name__ == "__main__":
    create_tables()
