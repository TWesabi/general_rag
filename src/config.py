"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    DATABASE_URL: str = "DATABASE_URL", "postgresql://rag_user:rag_password@localhost:5432/rag_db"


settings = Settings()
