"""Explicit, local-testable safety boundary for the non-persistent Preview runtime."""

from __future__ import annotations

import secrets
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from backend.config import RuntimeConfig


@dataclass
class PreviewSessionRegistry:
    """Keeps opaque browser sessions and their databases process-local and transient."""

    data_dir: Path
    _sessions: dict[str, Path] = field(default_factory=dict)

    @property
    def session_dir(self) -> Path:
        return self.data_dir / "preview-sessions"

    def reset_for_startup(self) -> None:
        # This path is Preview-owned and configuration rejects the local data dir.
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self._sessions.clear()

    def database_for(self, session_token: str | None) -> tuple[str, Path, bool]:
        if session_token and session_token in self._sessions:
            return session_token, self._sessions[session_token], False
        token = secrets.token_urlsafe(32)
        database_path = self.session_dir / f"{secrets.token_hex(16)}.db"
        self._sessions[token] = database_path
        return token, database_path, True


def preview_provider_allowlist(runtime: RuntimeConfig) -> frozenset[str] | None:
    """Return a generic Preview provider policy; local mode keeps the full Registry."""
    return frozenset(runtime.preview_provider_allowlist) if runtime.preview_enabled else None


def preview_surface_options(runtime: RuntimeConfig) -> dict[str, str | None]:
    """Keep framework documentation closed whenever the explicit Preview mode is active."""
    if runtime.preview_enabled:
        return {"docs_url": None, "redoc_url": None, "openapi_url": None}
    return {"docs_url": "/docs", "redoc_url": "/redoc", "openapi_url": "/openapi.json"}
