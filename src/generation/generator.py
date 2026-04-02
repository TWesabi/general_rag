from abc import ABC, abstractmethod

import httpx

from src.config import settings
from src.generation.constants import RAG_PROMPT_TEMPLATE
from src.schemas.query import RetrievalResult
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class BaseGenerator(ABC):

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    def __call__(self, user_query: str, context: list[RetrievalResult]) -> str: ...


class OllamaGenerator(BaseGenerator):

    def __init__(self):
        self.chat_url = f"{settings.OLLAMA__BASE_URL}/chat/completions"
        self.generating_model = settings.OLLAMA__CHAT_MODEL
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __call__(self, user_query: str, context: list[RetrievalResult]):

        body = {
            "model": self.generating_model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": self._build_prompt(user_query, context)},
            ],
            "stream": False,
        }

        try:
            response = httpx.post(url=self.chat_url, headers=self.headers, json=body, timeout=120)
            response.raise_for_status()
            return response.json().get("choices")[0].get("message").get("content")
        except ConnectionError as e:
            log.error("Cannot connect to Ollama at %s: %s", self.chat_url, e)
            raise
        except httpx.HTTPStatusError as e:
            log.error("Ollama returned error: %s", e)
            raise

    def _build_prompt(self, user_query: str, context: list[RetrievalResult]) -> str:
        enrichment = ""
        for idx, result in enumerate(context):
            result_text = f"{idx}. score({result.score}) - {result.content} \n"
            enrichment += result_text
        prompt = RAG_PROMPT_TEMPLATE.format(user_query=user_query, context=enrichment)
        return prompt
