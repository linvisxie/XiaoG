"""Unified XiaoG configuration boundaries.

Provider secrets stay local in .env. User preferences live in SQLite, product
metadata in product_info.json, and transient process state stays in services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class RuntimeConfig:
    """Local development/runtime paths and non-secret process behavior."""

    project_root: Path = PROJECT_ROOT
    database_path: Path = PROJECT_ROOT / "data" / "xiaog.db"
    log_dir: Path = PROJECT_ROOT / "data" / "logs"
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()


@dataclass(frozen=True)
class ProviderConfig:
    """Provider endpoints and model identifiers that are safe to describe."""

    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    deepseek_model_id: str = os.getenv("DEEPSEEK_MODEL_ID", "deepseek-v4-flash").strip()


@dataclass(frozen=True)
class ProviderSecrets:
    """Credentials are process-local and must never enter public metadata/logs."""

    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "").strip()


@dataclass(frozen=True)
class Settings:
    """Compatibility facade over explicit XiaoG configuration boundaries."""

    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    providers: ProviderConfig = field(default_factory=ProviderConfig)
    provider_secrets: ProviderSecrets = field(default_factory=ProviderSecrets)

    @property
    def project_root(self) -> Path:
        return self.runtime.project_root

    @property
    def database_path(self) -> Path:
        return self.runtime.database_path

    @property
    def log_dir(self) -> Path:
        return self.runtime.log_dir

    @property
    def log_level(self) -> str:
        return self.runtime.log_level

    @property
    def deepseek_base_url(self) -> str:
        return self.providers.deepseek_base_url

    @property
    def deepseek_model_id(self) -> str:
        return self.providers.deepseek_model_id

    @property
    def deepseek_api_key(self) -> str:
        return self.provider_secrets.deepseek_api_key


def configuration_summary(active: Settings = None) -> dict[str, object]:
    """Describe ownership boundaries without returning secret values."""
    current = active or settings
    return {
        "runtime": {
            "project_root": str(current.project_root),
            "database_path": str(current.database_path),
            "log_dir": str(current.log_dir),
            "log_level": current.log_level,
        },
        "provider_configuration": {
            "deepseek_base_url": current.deepseek_base_url,
            "deepseek_model_id": current.deepseek_model_id,
        },
        "provider_secrets": {"source": "local .env", "exposed": False},
        "user_settings": {"source": "SQLite settings table"},
        "product_metadata": {"source": "product_info.json"},
        "runtime_state": {"source": "in-memory service state"},
    }


settings = Settings()