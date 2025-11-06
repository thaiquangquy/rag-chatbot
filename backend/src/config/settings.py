from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RAG Chatbot"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str | None = None
    ollama_base_url: str | None = None
    service_account_path: str | None = None
    embedding_provider: str = "lm_studio"
    embedding_dimension: int = 768
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_embedding_model: str = "text-embedding-nomic-embed-text-v1.5"
    lm_studio_timeout_seconds: float = 30.0


@lru_cache
def get_settings() -> Settings:
    return Settings()