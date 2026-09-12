"""Small, transparent router for explicit Manual model and reasoning choices."""

from backend.providers.base import ModelProvider, ProviderError
from backend.providers.deepseek import DeepSeekProvider
from backend.providers.terra import TerraProvider
from backend.services.model_registry import ModelRegistry


class ModelRouter:
    def __init__(self) -> None:
        self.deepseek = DeepSeekProvider()
        self.terra = TerraProvider()
        self.registry = ModelRegistry({"deepseek": self.deepseek, "terra": self.terra})

    async def select(self, preference: str) -> tuple[ModelProvider, str]:
        provider, display_name, _effort, _model = await self.select_manual(preference, None)
        return provider, display_name

    async def select_manual(self, preference: str, reasoning_effort: str | None) -> tuple[ModelProvider, str, str | None, dict]:
        # Auto is still disabled; the legacy auto preference remains explicit DeepSeek fallback.
        selection_key = preference if preference in {"deepseek", "terra"} else "deepseek"
        _status, model, selected_effort = await self.registry.resolve_manual_reasoning(selection_key, reasoning_effort)
        provider = self.terra if selection_key == "terra" else self.deepseek
        return provider, model["display_name"], selected_effort, model

    async def status(self) -> dict:
        return await self.registry.provider_status()


model_router = ModelRouter()