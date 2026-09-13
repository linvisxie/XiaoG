"""Model selection facade for strict Manual and transparent Auto modes."""

from backend.diagnostics import diagnostic_logger, log_event
from backend.providers.base import ModelProvider, ProviderError
from backend.providers.deepseek import DeepSeekProvider
from backend.providers.terra import TerraProvider
from backend.router.auto_router import AutoRouter
from backend.services.model_registry import ModelRegistry


logger = diagnostic_logger('router')


class ModelRouter:
    def __init__(self) -> None:
        self.deepseek = DeepSeekProvider()
        self.terra = TerraProvider()
        self.registry = ModelRegistry({"deepseek": self.deepseek, "terra": self.terra})

    async def select(self, preference: str) -> tuple[ModelProvider, str]:
        provider, display_name, _effort, _model = await self.select_manual(preference, None)
        return provider, display_name

    async def select_manual(self, preference: str, reasoning_effort: str | None) -> tuple[ModelProvider, str, str | None, dict]:
        selection_key = preference if preference in {"deepseek", "terra"} else "deepseek"
        _status, model, selected_effort = await self.registry.resolve_manual_reasoning(selection_key, reasoning_effort)
        provider = self.terra if selection_key == "terra" else self.deepseek
        log_event(logger, 20, "manual_model_selected", selection_key=selection_key, reasoning_effort=selected_effort)
        return provider, model["display_name"], selected_effort, model

    async def select_auto(self, content: str, context_characters: int) -> tuple[ModelProvider, str, str | None, dict, dict]:
        states = await self.registry._provider_states()
        snapshot = self.registry._snapshot_from_states(states)
        models = {model["selection_key"]: model for model in snapshot["models"]}
        try:
            decision = AutoRouter.decide(content, context_characters, models)
        except ValueError as exc:
            raise ProviderError(str(exc)) from exc
        _status, model, effort = await self.registry.resolve_manual_reasoning(decision.selection_key, decision.selected_effort)
        provider = self.terra if decision.selection_key == "terra" else self.deepseek
        routing = {
            "selected_provider": model["provider_id"], "selected_model": model["model_id"],
            "selected_effort": effort, "task_class": decision.task_class,
            "routing_time_ms": decision.routing_time_ms, "routing_explanation": decision.routing_explanation,
        }
        log_event(logger, 20, "auto_model_selected", selection_key=decision.selection_key, task_class=decision.task_class, reasoning_effort=effort)
        return provider, model["display_name"], effort, model, routing

    async def status(self) -> dict:
        return await self.registry.provider_status()


model_router = ModelRouter()
