"""Centralized configuration. Secrets are read only from the local .env file."""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    database_path: Path = PROJECT_ROOT / "data" / "xiaog.db"
    log_dir: Path = PROJECT_ROOT / "data" / "logs"
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "").strip()
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    deepseek_model_id: str = os.getenv("DEEPSEEK_MODEL_ID", "deepseek-v4-flash").strip()
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()


settings = Settings()
