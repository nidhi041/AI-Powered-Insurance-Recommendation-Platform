import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _storage_path(variable: str, default: str) -> str:
    """Resolve relative storage paths from the backend directory, not cwd."""
    configured_path = Path(os.getenv(variable, default)).expanduser()
    if not configured_path.is_absolute():
        configured_path = BACKEND_DIR / configured_path
    return str(configured_path)


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # ChromaDB persistent directory.
    # On Render, point this to a Persistent Disk mount path, e.g. /var/data/chroma_db
    CHROMA_PERSIST_DIR: str = _storage_path(
        "CHROMA_PERSIST_DIR",
        "chroma_db",
    )

    # SQLite database path for document metadata.
    # On Render, point this to a Persistent Disk mount path, e.g. /var/data/insureiq.db
    # Locally it defaults to the backend directory.
    DOCUMENT_DB_PATH: str = _storage_path(
        "DOCUMENT_DB_PATH",
        "insureiq.db",
    )

    CHUNK_SIZE: int = 1500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5

    # Maximum allowed PDF upload size in bytes (default: 50 MB)
    MAX_PDF_SIZE_BYTES: int = int(os.getenv("MAX_PDF_SIZE_BYTES", str(50 * 1024 * 1024)))


settings = Settings()