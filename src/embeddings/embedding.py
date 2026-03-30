from abc import ABC, abstractmethod

import httpx

from src.config import settings
from utils.logger import setup_logger

log = setup_logger(__name__)


class BaseEmbedder(ABC):
    embeddings_url: str
    headers: dict

    @abstractmethod
    def __call__(self, text_list: list[str]) -> list[list[float]]: ...


class OllamaEmbedder(BaseEmbedder):

    def __init__(self):
        self.embeddings_url = f"{settings.OLLAMA__BASE_URL}/embeddings"
        self.model = settings.OLLAMA__EMBEDDING_MODEL
        self.headers = {
            "Authorization": "Bearer ollama",
            "Content-Type": "application/json",
        }

    def __call__(self, text_list: list[str]) -> list[list[float]]:

        if not text_list:
            raise ValueError("Text list is empty!")

        body = {"model": self.model, "input": text_list}

        try:
            response = httpx.post(self.embeddings_url, headers=self.headers, json=body, timeout=60)
            response.raise_for_status()
            embeddings_objects = response.json()["data"]
            embeddings_list = [obj["embedding"] for obj in embeddings_objects]
        except httpx.ConnectError as e:
            log.error("Cannot connect to Ollama at %s: %s", self.embeddings_url, e)
            raise
        except httpx.HTTPStatusError as e:
            log.error("Ollama returned error status: %s | body: %s", e, e.response.text)
            raise

        return embeddings_list
