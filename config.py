"""
app/core/config.py

Central configuration for Anqa. Every setting the app needs lives here,
loaded once from environment variables. Nothing else in the codebase
should call os.environ directly — always import `settings` from this file.

Why this pattern: it makes the whole app's configuration surface
auditable in one place, and it's the standard FastAPI production
pattern (pydantic-settings) rather than scattered os.getenv() calls.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App identity ---
    app_name: str = "Anqa"
    app_version: str = "0.1.0"
    environment: str = "development"  # "development" | "production"

    # --- OpenRouter (LLM provider) ---
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-3.5-sonnet"
    # Vision-capable fallback model, used when the request includes images
    vision_model: str = "anthropic/claude-3.5-sonnet"

    # --- Auth ---
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    # --- Database (chat history, users) ---
    database_url: str = "sqlite+aiosqlite:///./anqa.db"

    # --- Vector memory store ---
    # Local-first (chromadb) so the project runs with zero paid infra.
    # Swappable later for a hosted vector DB (Qdrant/Pinecone) without
    # touching any router code — see app/memory/store.py
    vector_store_path: str = "./anqa_vector_store"
    memory_top_k: int = 5  # how many past memories to retrieve per turn

    # --- File uploads ---
    upload_dir: str = "./uploads"
    max_upload_mb: int = 25
    allowed_image_types: list[str] = ["image/png", "image/jpeg", "image/webp"]
    allowed_doc_types: list[str] = ["application/pdf"]
    allowed_video_types: list[str] = ["video/mp4", "video/quicktime"]

    # --- Voice ---
    # STT/TTS provider keys are optional at boot so the rest of the app
    # still runs if voice isn't configured yet.
    stt_provider: str = "openai"  # "openai" (Whisper API) is simplest to start
    tts_provider: str = "openai"
    stt_api_key: str | None = None
    tts_api_key: str | None = None

    # --- CORS ---
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. FastAPI dependency-injects this so settings
    are parsed from env exactly once per process, not on every request.
    """
    return Settings()


settings = get_settings()
