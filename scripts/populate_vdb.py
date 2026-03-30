from src.db.database import get_session
from src.factory import create_indexing_pipeline, create_vector_store

session = get_session()
v_store = create_vector_store()
indexing_pipeline = create_indexing_pipeline(session=session, vector_store=v_store)
indexing_pipeline()
session.commit()
session.close()
