from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from src.config import settings


class Base(DeclarativeBase):
    pass


ENGINE: Engine = create_engine(settings.DATABASE_URL)


def create_tables():
    Base.metadata.create_all(ENGINE)


def get_session() -> Session:
    return Session(ENGINE)
