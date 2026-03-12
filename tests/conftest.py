import pytest

import src.db.models  # noqa: F401 — registers models with Base metadata
from src.db.database import ENGINE, Base


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(ENGINE)
    yield
    Base.metadata.drop_all(ENGINE)
