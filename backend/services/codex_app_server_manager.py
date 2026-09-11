"""Lifecycle manager for XiaoG's single local Codex App Server process.

It retains no authentication material. ChatGPT authentication remains owned by
the official Codex CLI; this manager only keeps a process, sanitized account
metadata, and the model list in memory.
"""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from backend.providers.base import ProviderError
from backend.providers.codex_app_server import CodexAppServerClient


logger = logging.getLogger(__name__)


class CodexAppServerManager:
    """One async-safe, long-lived JSON-RPC connection for all Terra requests."""

    def __init__(self) -> None:
        self._client: CodexAppServerClient | None = None
        self._operation_lock = asyncio.Lock()
        self._account: dict[str, Any] | None = None
        self._models: list[dict[str, Any]] = []
        self._rate_limits: dict[str, Any] | None = None

    async def start(self) -> None:
        """Start and initialize the server once, or reuse a healthy instance."""
        async with self._operation_lock:
            await self._ensure_started_locked()

    async def close(self) -> None:
        """Safely stop the child process during XiaoG shutdown."""
        async with self._operation_lock:
            await self._close_locked()

    async def refresh(self, include_rate_limits: bool = False) -> None:
        """Explicit refresh hook; ordinary Terra turns never invoke this."""
        async with self._operation_lock:
            await self._ensure_started_locked()
            await self._refresh_locked(include_rate_limits=include_rate_limits)

    async def discovery(self, include_rate_limits: bool = False) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
        """Return cached discovery data, starting once if XiaoG began offline."""
        async with self._operation_lock:
            await self._ensure_started_locked()
            if include_rate_limits and self._rate_limits is None:
                try:
                    self._rate_limits = await self._client_request_locked("account/rateLimits/read", {})
                except ProviderError:
                    self._rate_limits = None
            return dict(self._account or {}), list(self._models), self._rate_limits

    @asynccontextmanager
    async def turn_session(self) -> AsyncIterator[CodexAppServerClient]:
        """Lease the stdio connection for one complete streamed Terra turn.

        JSON-RPC responses and notifications share one stdout stream, therefore
        a lease intentionally serializes simultaneous Terra requests.
        """
        async with self._operation_lock:
            await self._ensure_started_locked()
            assert self._client is not None
            try:
                yield self._client
            except ProviderError:
                if not self._client.is_running:
                    logger.warning("Codex App Server exited during a Terra request; next request will reconnect.")
                    await self._close_locked()
                raise

    async def restart(self) -> None:
        """Reconnect after an unexpected child-process exit without exposing credentials."""
        async with self._operation_lock:
            await self._close_locked()
            await self._ensure_started_locked()

    @property
    def models(self) -> list[dict[str, Any]]:
        return list(self._models)

    @property
    def account(self) -> dict[str, Any]:
        return dict(self._account or {})

    @property
    def process_id(self) -> int | None:
        return self._client.process_id if self._client and self._client.is_running else None

    async def _ensure_started_locked(self) -> None:
        if self._client and self._client.is_running:
            return
        await self._close_locked()
        client = CodexAppServerClient()
        try:
            await client.start()
            self._client = client
            await self._refresh_locked(include_rate_limits=True)
            logger.info("Codex App Server ready (pid=%s).", client.process_id)
        except Exception:
            await client.close()
            self._client = None
            self._account = None
            self._models = []
            self._rate_limits = None
            raise

    async def _refresh_locked(self, include_rate_limits: bool) -> None:
        account = await self._client_request_locked("account/read", {"refreshToken": False})
        models_result = await self._client_request_locked("model/list", {"limit": 100, "includeHidden": False})
        account_data = account.get("account") or {}
        self._account = {"type": account_data.get("type"), "planType": account_data.get("planType")}
        self._models = models_result.get("data") or []
        self._rate_limits = None
        if include_rate_limits:
            try:
                self._rate_limits = await self._client_request_locked("account/rateLimits/read", {})
            except ProviderError:
                self._rate_limits = None

    async def _client_request_locked(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self._client:
            raise ProviderError("Codex App Server 未启动。")
        return await self._client.request(method, params)

    async def _close_locked(self) -> None:
        if self._client:
            await self._client.close()
        self._client = None
        self._account = None
        self._models = []
        self._rate_limits = None


codex_app_server_manager = CodexAppServerManager()
