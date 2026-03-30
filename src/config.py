"""Configuration management using pydantic-settings."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    DATABASE_URL: str = "postgresql://rag_user:rag_password@localhost:5432/rag_db"

    CHUNKING__CHUNK_SIZE: int = 500
    CHUNKING__CHUNK_OVERLAP: int = 100
    OLLAMA__BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA__EMBEDDING_MODEL: str = "bge-m3:latest"
    TRANSFORMERS__EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    QDRANT__COLLECTION_NAME: str = "rag_chunks"
    QDRANT__URL: str = "http://localhost:6333"
    QDRANT__VECTOR_SIZE: int = 1024
    QDRANT__SCROLL_SIZE: int = 100

    TOP_K: int = 3

    EMBEDDING_PROVIDER: Literal["ollama", "transformer"] = "ollama"
    CHUNKER_TYPE: Literal["fixed", "recursive"] = "fixed"


settings = Settings()
