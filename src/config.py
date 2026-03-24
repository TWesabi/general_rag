"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    DATABASE_URL: str = "DATABASE_URL", "postgresql://rag_user:rag_password@localhost:5432/rag_db"

    CHUNKING__CHUNK_SIZE: int = 500
    CHUNKING__CHUNK_OVERLAP: int = 100
    OLLAMA__BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA__EMBEDDING_MODEL: str = "bge-m3"
    TRANSFORMERS__EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"


settings = Settings()
