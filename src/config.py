"""Configuration management using pydantic-settings."""

from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WeaviateConfig(BaseSettings):
    """Weaviate configuration."""

    model_config = SettingsConfigDict(env_prefix="WEAVIATE_")

    url: str = Field(default="http://localhost:8080", description="Weaviate server URL")
    api_key: Optional[str] = Field(default=None, description="Weaviate API key")
    use_grpc: bool = Field(default=False, description="Use gRPC for communication")


class EmbeddingConfig(BaseSettings):
    """Embedding model configuration."""

    model_config = SettingsConfigDict(env_prefix="EMBEDDING_")

    # Provider: "ollama" or "sentence_transformers"
    provider: Literal["ollama", "sentence_transformers"] = Field(
        default="ollama",
        description="Embedding provider: 'ollama' (local) or 'sentence_transformers' (Hugging Face)",
    )
    # Ollama settings
    ollama_model: str = Field(
        default="bge-m3:latest",
        description="Ollama embedding model name",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL for embeddings",
    )
    # Sentence-transformers settings
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence-transformers model name (when provider=sentence_transformers)",
    )
    device: str = Field(default="cpu", description="Device to run embeddings on")
    batch_size: int = Field(default=32, description="Batch size for embedding generation")
    disable_ssl_verify: bool = Field(
        default=False,
        description="Disable SSL verification for Hugging Face downloads (sentence_transformers only)",
    )


class OllamaConfig(BaseSettings):
    """Ollama configuration."""

    model_config = SettingsConfigDict(env_prefix="OLLAMA_")

    base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    model: str = Field(default="qwen3:latest", description="Ollama model name")


class AzureOpenAIConfig(BaseSettings):
    """Azure OpenAI configuration."""

    model_config = SettingsConfigDict(env_prefix="AZURE_OPENAI_")

    api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    api_version: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version",
    )
    deployment_name: Optional[str] = Field(
        default=None,
        description="Azure OpenAI deployment name",
    )


class LLMConfig(BaseSettings):
    """LLM provider configuration."""

    model_config = SettingsConfigDict(env_prefix="LLM_")

    provider: Literal["ollama", "azure_openai"] = Field(
        default="ollama",
        description="LLM provider to use",
    )
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    azure_openai: AzureOpenAIConfig = Field(default_factory=AzureOpenAIConfig)


class MLflowConfig(BaseSettings):
    """MLflow configuration."""

    model_config = SettingsConfigDict(env_prefix="MLFLOW_")

    tracking_uri: str = Field(
        default="http://localhost:5000",
        description="MLflow tracking URI",
    )
    experiment_name: str = Field(
        default="rag-system",
        description="MLflow experiment name",
    )


class ZenMLConfig(BaseSettings):
    """ZenML configuration."""

    model_config = SettingsConfigDict(env_prefix="ZENML_")

    store_type: str = Field(default="local", description="ZenML store type")
    store_path: str = Field(default=".zen", description="ZenML store path")


class ChunkingConfig(BaseSettings):
    """Chunking configuration."""

    model_config = SettingsConfigDict(env_prefix="CHUNK_")

    size: int = Field(default=512, description="Chunk size in characters")
    overlap: int = Field(default=50, description="Chunk overlap in characters")


class RetrievalConfig(BaseSettings):
    """Retrieval configuration."""

    model_config = SettingsConfigDict(env_prefix="RETRIEVAL_")

    top_k: int = Field(default=5, description="Number of top results to retrieve")
    score_threshold: float = Field(
        default=0.0,
        description="Minimum score threshold for retrieval",
    )


class APIConfig(BaseSettings):
    """FastAPI configuration."""

    model_config = SettingsConfigDict(env_prefix="API_")

    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8010, description="API port")
    reload: bool = Field(default=True, description="Enable auto-reload")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    weaviate: WeaviateConfig = Field(default_factory=WeaviateConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)
    zenml: ZenMLConfig = Field(default_factory=ZenMLConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    LOGGER_LEVEL: str = "INFO"


# Global settings instance
settings = Settings()
