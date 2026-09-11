"""Small, transparent model router. Auto defaults to DeepSeek in v0.1."""

from backend.providers.base import ModelProvider, ProviderError
from backend.providers.deepseek import DeepSeekProvider
from backend.providers.terra import TerraProvider


class ModelRouter:
    def __init__(self) -> None:
        self.deepseek = DeepSeekProvider()
        self.terra = TerraProvider()

    async def select(self, preference: str) -> tuple[ModelProvider, str]:
        if preference == "terra":
            status = await self.terra.health_check()
            if not status.available:
                raise ProviderError(status.message)
            return self.terra, "GPT-5.6 Terra"
        # Auto is intentionally simple and visible: v0.1 always chooses DeepSeek.
        return self.deepseek, "DeepSeek"

    async def status(self) -> dict:
        deepseek = await self.deepseek.health_check()
        terra = await self.terra.health_check()
        return {
            "deepseek": {"available": deepseek.available, "message": deepseek.message, "models": deepseek.models, "details": deepseek.details},
            "terra": {"available": terra.available, "message": terra.message, "models": terra.models, "details": terra.details},
            "auto": {"available": deepseek.available, "message": "Auto 在 v0.1 默认使用 DeepSeek。"},
        }


model_router = ModelRouter()