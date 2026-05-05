from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = "sk-placeholder"
    openai_model: str = "gpt-4o-mini"

    # Embedding
    embedding_mode: Literal["openai", "local"] = "local"

    # ChromaDB
    chroma_persist_path: str = "./chroma_db"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()