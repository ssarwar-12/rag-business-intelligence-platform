from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./dev.db",
        alias="DATABASE_URL",
    )
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    vector_store: str = Field(default="local", alias="VECTOR_STORE")
    pinecone_api_key: str | None = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_index: str | None = Field(default=None, alias="PINECONE_INDEX")
    upload_dir: Path = Field(default=Path("./uploads"), alias="UPLOAD_DIR")
    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")
    demo_user_email: str = Field(default="demo@example.com", alias="DEMO_USER_EMAIL")
    auto_create_tables: bool = Field(default=True, alias="AUTO_CREATE_TABLES")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
