"""Embedding generator supporting Ollama and sentence-transformers."""

import os
from typing import List

from ..config import settings


class Embedder:
    """Embedding generator supporting multiple providers (Ollama, sentence-transformers)."""

    def __init__(
        self,
        provider: str | None = None,
        model_name: str | None = None,
        batch_size: int | None = None,
    ):
        """
        Initialize the embedder.

        Args:
            provider: "ollama" or "sentence_transformers" (default from config)
            model_name: Model name (overrides config)
            batch_size: Batch size for embedding generation
        """
        self.provider = provider or settings.embedding.provider
        self.batch_size = batch_size or settings.embedding.batch_size
        self._model = None  # Lazy-loaded for sentence_transformers

        if self.provider == "ollama":
            self.model_name = model_name or settings.embedding.ollama_model
            self.base_url = settings.embedding.ollama_base_url
        else:
            self.model_name = model_name or settings.embedding.model_name
            self.device = settings.embedding.device
            self._init_sentence_transformers()

    def _init_sentence_transformers(self):
        """Initialize sentence-transformers (with optional SSL workaround)."""
        # SSL workaround for Hugging Face
        if os.environ.get("EMBEDDING_DISABLE_SSL_VERIFY", "").strip().lower() in (
            "true",
            "1",
            "on",
        ):
            try:
                import requests
                from huggingface_hub import configure_http_backend

                def _hf_backend_factory():
                    s = requests.Session()
                    s.verify = False
                    return s

                configure_http_backend(backend_factory=_hf_backend_factory)
            except Exception:
                pass

        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(self.model_name, device=self.device)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        if self.provider == "ollama":
            return self._embed_ollama(texts)
        else:
            return self._embed_sentence_transformers(texts)

    def _embed_ollama(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama."""
        import httpx

        embeddings = []
        url = f"{self.base_url.rstrip('/')}/api/embeddings"

        for text in texts:
            response = httpx.post(
                url,
                json={"model": self.model_name, "prompt": text},
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            embeddings.append(data["embedding"])

        return embeddings

    def _embed_sentence_transformers(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence-transformers."""
        embeddings = self._model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        return self.embed([text])[0]

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings.

        Returns:
            Embedding dimension
        """
        dummy_embedding = self.embed_single("test")
        return len(dummy_embedding)
