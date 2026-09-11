"""Reserved official Codex App Server adapter for Phase 3. Intentionally inactive in v0.1."""

from collections.abc import AsyncIterator
from backend.providers.base import ModelProvider, ProviderError, ProviderStatus


class TerraProvider(ModelProvider):
    name = "openai_codex"

    async def health_check(self) -> ProviderStatus:
        return ProviderStatus(self.name, False, "GPT-5.6 Terra 尚未在 XiaoG v0.1 接入。", [])

    async def list_models(self) -> list[dict]:
        return []

    async def stream_chat(self, messages: list[dict[str, str]]) -> AsyncIterator[dict]:
        raise ProviderError("GPT-5.6 Terra 将在 Phase 3 通过官方 Codex App Server 接入。")
        yield  # makes this an async generator for the interface

    async def send_message(self, messages: list[dict[str, str]]) -> dict:
        raise ProviderError("GPT-5.6 Terra 将在 Phase 3 通过官方 Codex App Server 接入。")

    async def get_usage(self) -> dict | None:
        return None
