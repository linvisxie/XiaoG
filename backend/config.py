"""Unified XiaoG configuration boundaries.

Provider secrets stay local in .env. User preferences live in SQLite, product
metadata in product_info.json, and transient process state stays in services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import json

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _path_from_env(name: str, default: Path) -> Path:
    raw = os.getenv(name, "").strip()
    return Path(raw).expanduser().resolve() if raw else default.resolve()


def _runtime_mode() -> str:
    return os.getenv("XIAOG_RUNTIME_MODE", "local").strip().lower() or "local"


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime identity and paths. Preview is explicit and opt-in only."""

    project_root: Path = PROJECT_ROOT
    runtime_mode: str = field(default_factory=_runtime_mode)
    host: str = field(default_factory=lambda: os.getenv("XIAOG_HOST", "127.0.0.1").strip() or "127.0.0.1")
    port: int = field(default_factory=lambda: int(os.getenv("XIAOG_PORT", "8000")))
    data_dir: Path = field(default_factory=lambda: _path_from_env("XIAOG_DATA_DIR", PROJECT_ROOT / "data"))
    database_path: Path = field(default_factory=lambda: _path_from_env("XIAOG_DATABASE_PATH", _path_from_env("XIAOG_DATA_DIR", PROJECT_ROOT / "data") / "xiaog.db"))
    log_dir: Path = field(default_factory=lambda: _path_from_env("XIAOG_LOG_DIR", _path_from_env("XIAOG_DATA_DIR", PROJECT_ROOT / "data") / "logs"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    release_id: str = field(default_factory=lambda: os.getenv("XIAOG_RELEASE_ID", "local-development").strip() or "local-development")
    preview_provider_allowlist: tuple[str, ...] = field(
        default_factory=lambda: tuple(item.strip() for item in os.getenv("XIAOG_PREVIEW_PROVIDER_ALLOWLIST", "deepseek").split(",") if item.strip())
    )
    preview_invites: dict[str, str] = field(default_factory=lambda: json.loads(os.getenv("XIAOG_PREVIEW_INVITES", "{}")))
    preview_session_ttl_seconds: int = field(default_factory=lambda: int(os.getenv("XIAOG_PREVIEW_SESSION_TTL_SECONDS", "3600")))
    preview_request_limit: int = field(default_factory=lambda: int(os.getenv("XIAOG_PREVIEW_REQUEST_LIMIT", "30")))
    preview_generation_limit: int = field(default_factory=lambda: int(os.getenv("XIAOG_PREVIEW_GENERATION_LIMIT", "12")))
    preview_window_seconds: int = field(default_factory=lambda: int(os.getenv("XIAOG_PREVIEW_WINDOW_SECONDS", "60")))
    preview_max_concurrent_per_invite: int = field(default_factory=lambda: int(os.getenv("XIAOG_PREVIEW_MAX_CONCURRENT_PER_INVITE", "1")))
    preview_max_concurrent_global: int = field(default_factory=lambda: int(os.getenv("XIAOG_PREVIEW_MAX_CONCURRENT_GLOBAL", "3")))
    preview_max_input_chars: int = field(default_factory=lambda: int(os.getenv("XIAOG_PREVIEW_MAX_INPUT_CHARS", "12000")))

    def __post_init__(self) -> None:
        if self.runtime_mode not in {"local", "preview"}:
            raise ValueError("XIAOG_RUNTIME_MODE must be 'local' or 'preview'.")
        if not 1 <= self.port <= 65535:
            raise ValueError("XIAOG_PORT must be between 1 and 65535.")
        if self.runtime_mode == "preview":
            if not os.getenv("XIAOG_DATA_DIR", "").strip():
                raise ValueError("Preview mode requires an explicit XIAOG_DATA_DIR.")
            if self.data_dir == (PROJECT_ROOT / "data").resolve():
                raise ValueError("Preview mode must not use XiaoG's local data directory.")
            if self.release_id == "local-development":
                raise ValueError("Preview mode requires an explicit XIAOG_RELEASE_ID.")
            if set(self.preview_provider_allowlist) != {"deepseek"}:
                raise ValueError("WP-1 Preview permits only the DeepSeek provider allowlist.")
            if not self.preview_invites or not all(isinstance(key, str) and isinstance(value, str) and key and len(value) >= 16 for key, value in self.preview_invites.items()):
                raise ValueError("Preview requires XIAOG_PREVIEW_INVITES JSON with non-secret IDs and high-entropy credentials.")

    @property
    def preview_enabled(self) -> bool:
        return self.runtime_mode == "preview"


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


def validate_preview_startup(active: Settings | None = None) -> None:
    """Fail closed for an accidentally incomplete Preview runtime without exposing a secret."""
    current = active or settings
    if current.runtime.preview_enabled and not current.deepseek_api_key:
        raise RuntimeError(
            "Preview startup blocked: server-side DEEPSEEK_API_KEY is missing. "
            "Inject it only through the runtime secret environment; no value was logged."
        )


def configuration_summary(active: Settings = None) -> dict[str, object]:
    """Describe ownership boundaries without returning secret values."""
    current = active or settings
    return {
        "runtime": {
            "project_root": str(current.project_root),
            "runtime_mode": current.runtime.runtime_mode,
            "host": current.runtime.host,
            "port": current.runtime.port,
            "data_dir": str(current.runtime.data_dir),
            "database_path": str(current.database_path),
            "log_dir": str(current.log_dir),
            "log_level": current.log_level,
            "release_id": current.runtime.release_id,
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
