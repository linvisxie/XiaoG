"""Small, transparent model router. Manual routing remains explicit in v0.4.0."""

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
        if preference == "terra":
            status = await self.terra.health_check()
            if not status.available:
                raise ProviderError(status.message)
            return self.terra, self.registry.display_name_for_selection("terra")
        # Auto routing is not implemented in v0.4.0; existing non-Terra behavior remains DeepSeek.
        return self.deepseek, self.registry.display_name_for_selection("deepseek")

    async def status(self) -> dict:
        return await self.registry.provider_status()


model_router = ModelRouter()