"""Configuration for the deliberately small Pstral demonstration profile."""

from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
APP_DIR = BACKEND_DIR / "app"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Pstral — Assistant interne de démonstration"
    API_V1_STR: str = "/api/v1"
    DEMO_PROFILE: Literal["synthetic", "business"] = "synthetic"

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:8080"]
    DATA_DIR: Path = BACKEND_DIR / "data"
    DOCUMENTS_DIR: Path = APP_DIR / "demo_assets" / "documents"
    DOCUMENT_INDEX_PATH: Path | None = None
    SQL_CATALOG_PATH: Path = APP_DIR / "demo_assets" / "sql" / "catalog.json"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3.5:2b"
    OLLAMA_KEEP_ALIVE: str = "30m"
    OLLAMA_NUM_THREADS: int = 2
    OLLAMA_NO_CLOUD: bool = True

    MODEL_CONTEXT_TOKENS: int = 2048
    CHAT_OUTPUT_TOKENS: int = 240
    SQL_OUTPUT_TOKENS: int = 192
    MAX_HISTORY_TURNS: int = 2
    MAX_MESSAGE_CHARS: int = 2000
    MAX_HTTP_BODY_BYTES: int = 32768
    CHAT_TIMEOUT_SECONDS: int = 90

    # The running application rejects the empty default instead of creating a new key.
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    @field_validator("DATA_DIR", "DOCUMENTS_DIR", "SQL_CATALOG_PATH", mode="before")
    @classmethod
    def expand_paths(cls, value: str | Path) -> Path:
        return Path(value).expanduser()

    @property
    def document_index_path(self) -> Path:
        return self.DOCUMENT_INDEX_PATH or self.DATA_DIR / "documents.db"

    @property
    def users_db_path(self) -> Path:
        return self.DATA_DIR / "users.db"

    @property
    def audit_db_path(self) -> Path:
        return self.DATA_DIR / "audit.db"

    def validate_runtime(self) -> None:
        insecure_values = {
            "",
            "change-me-in-production",
            "change-me",
            "secret",
            "admin123",
            "replace-with-a-random-32-character-secret",
        }
        if self.SECRET_KEY.strip() in insecure_values or len(self.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY doit être configurée avec une valeur aléatoire d'au moins 32 caractères.")
        if self.DEMO_PROFILE == "business" and not self.DOCUMENTS_DIR.exists():
            raise RuntimeError("DOCUMENTS_DIR est requis pour le profil business.")
        if not self.SQL_CATALOG_PATH.is_file():
            raise RuntimeError("SQL_CATALOG_PATH est introuvable ou invalide.")


settings = Settings()
