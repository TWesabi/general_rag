from sentence_transformers import SentenceTransformer

from src.config import settings
from src.embeddings.embedding import BaseEmbedder
from utils.logger import setup_logger

log = setup_logger(__name__)


class TransformerEmbedder(BaseEmbedder):

    def __init__(self):
        self.model = SentenceTransformer(model_name_or_path=settings.TRANSFORMERS__EMBEDDING_MODEL)

    def __call__(self, text_list: list[str]) -> list[list[float]]:

        if not text_list:
            raise ValueError("Text list is empty!")
        embeddings_list = self.model.encode(text_list)

        return embeddings_list.tolist()
