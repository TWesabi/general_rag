import pytest

from src.db.database import ENGINE, Base, get_session


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(ENGINE)
    yield
    Base.metadata.drop_all(ENGINE)


@pytest.fixture
def db_session():
    session = get_session()
    yield session
    session.rollback()
    session.close()
