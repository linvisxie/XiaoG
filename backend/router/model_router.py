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
            raise ProviderError("当前账户未提供 GPT-5.6 Terra。它将在 Phase 3 按官方 Codex App Server 方案接入后检测。")
        # Auto is intentionally simple and visible: v0.1 always chooses DeepSeek.
        return self.deepseek, "DeepSeek"

    async def status(self) -> dict:
        deepseek = await self.deepseek.health_check()
        terra = await self.terra.health_check()
        return {
            "deepseek": {"available": deepseek.available, "message": deepseek.message, "models": deepseek.models},
            "terra": {"available": terra.available, "message": terra.message, "models": terra.models},
            "auto": {"available": deepseek.available, "message": "Auto 在 v0.1 默认使用 DeepSeek。"},
        }


model_router = ModelRouter()
