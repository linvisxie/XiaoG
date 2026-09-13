"""Product-owned provider, model, and capability metadata registry.

The registry describes provider capabilities without carrying credentials or
changing a provider's request path. It is the single source for model display
metadata used by XiaoG's API and interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.config import settings
from backend.providers.base import ModelProvider, ProviderError, ProviderStatus, ReasoningEffortError
from backend.providers.terra import TERRA_MODEL_ID
from backend.services.provider_health import provider_health_service


@dataclass(frozen=True)
class ProviderDefinition:
    """Non-sensitive product metadata for one registered provider."""

    selection_key: str
    provider_id: str
    display_name: str
    capabilities: tuple[str, ...]
    configuration: dict[str, str]
    console_url: str | None = None
    usage_url: str | None = None
    billing_url: str | None = None
    recharge_url: str | None = None
    recharge_strategy: str | None = None


class ModelRegistry:
    """Adapt live provider discovery into stable XiaoG model metadata."""

    _definitions = {
        "deepseek": ProviderDefinition(
            selection_key="deepseek",
            provider_id="deepseek",
            display_name="DeepSeek",
            capabilities=("text", "streaming", "reasoning", "tool_use"),
            configuration={"credential_type": "api_key", "model_id_source": "DEEPSEEK_MODEL_ID"},
            console_url="https://platform.deepseek.com/",
            usage_url="https://platform.deepseek.com/usage",
            billing_url="https://platform.deepseek.com/balance",
            recharge_url="https://platform.deepseek.com/top_up",
        ),
        "terra": ProviderDefinition(
            selection_key="terra",
            provider_id="openai_codex",
            display_name="OpenAI Codex",
            capabilities=("text", "streaming", "reasoning"),
            configuration={"credential_type": "chatgpt_session", "transport": "official_codex_app_server"},
            console_url="https://chatgpt.com/",
            usage_url="https://platform.openai.com/usage",
            billing_url="https://platform.openai.com/account/billing/overview",
            # OpenAI documents recharging from Billing Overview: users select
            # "Buy credits" or "Add to credit balance" on that official page.
            recharge_url="https://platform.openai.com/account/billing/overview",
            recharge_strategy="billing_overview",
        ),
    }

    def __init__(self, providers: dict[str, ModelProvider], allowed_provider_keys: frozenset[str] | None = None) -> None:
        self._providers = providers
        self._allowed_provider_keys = allowed_provider_keys

    async def snapshot(self) -> dict[str, Any]:
        """Return one public, credential-free snapshot of registered models."""
        return self._snapshot_from_states(await self._provider_states())

    async def provider_status(self) -> dict[str, Any]:
        """Provide the legacy status shape, sourced entirely from the registry."""
        states = await self._provider_states()
        registry = self._snapshot_from_states(states)
        models_by_key: dict[str, list[dict[str, Any]]] = {key: [] for key in self._definitions}
        for model in registry["models"]:
            models_by_key[model["selection_key"]].append(model)

        result: dict[str, Any] = {}
        for selection_key, status in states.items():
            definition = self._definitions[selection_key]
            result[selection_key] = {
                "provider_id": definition.provider_id,
                "display_name": definition.display_name,
                "available": status.available,
                "message": status.message,
                "models": models_by_key[selection_key],
                "details": self._safe_details(status.details),
            }
        available = [model for model in registry["models"] if model["availability"]]
        result["auto"] = {"available": bool(available), "message": "本地规则会在可用模型间自动选择。" if available else "没有可用模型可供自动选择。"}
        result["registry"] = registry
        return result

    async def resolve_manual_reasoning(self, selection_key: str, requested_effort: str | None) -> tuple[ProviderStatus, dict[str, Any], str | None]:
        """Resolve a manual selection against the selected model's live metadata."""
        if selection_key not in self._definitions:
            raise ReasoningEffortError("请选择可用模型后再设置推理档位。")
        status = (await self._provider_states())[selection_key]
        model = self._models_for(selection_key, status)[0]
        if not model["availability"]:
            raise ProviderError(status.message)
        supported = model["supported_reasoning_efforts"]
        if not supported:
            if requested_effort:
                raise ReasoningEffortError("当前模型不支持推理档位选择。")
            return status, model, None
        effort = requested_effort or model["default_reasoning_effort"]
        if effort not in supported:
            raise ReasoningEffortError(
                f"当前模型不支持推理档位“{effort}”。请刷新模型状态后重试。"
            )
        return status, model, effort


    def display_name_for_selection(self, selection_key: str) -> str:
        if selection_key == "deepseek":
            return self._deepseek_display_name(settings.deepseek_model_id)
        if selection_key == "terra":
            return "GPT-5.6 Terra"
        return selection_key

    async def _provider_states(self) -> dict[str, ProviderStatus]:
        states: dict[str, ProviderStatus] = {}
        for selection_key, definition in self._definitions.items():
            if self._allowed_provider_keys is not None and selection_key not in self._allowed_provider_keys:
                states[selection_key] = ProviderStatus(
                    definition.provider_id, False, "当前运行模式未启用该 Provider。", []
                )
                continue
            provider = self._providers[selection_key]
            try:
                states[selection_key] = await provider.health_check()
            except ProviderError as exc:
                states[selection_key] = ProviderStatus(definition.provider_id, False, str(exc), [])
        return states

    def _snapshot_from_states(self, states: dict[str, ProviderStatus]) -> dict[str, Any]:
        providers: list[dict[str, Any]] = []
        models: list[dict[str, Any]] = []
        for selection_key, definition in self._definitions.items():
            status = states[selection_key]
            provider_models = self._models_for(selection_key, status)
            health = provider_health_service.assess(status, any(model["availability"] for model in provider_models))
            for model in provider_models:
                model["health"] = health.state
                model["routing_available"] = bool(model["availability"] and health.routing_available)
            models.extend(provider_models)
            providers.append({
                "selection_key": definition.selection_key,
                "provider_id": definition.provider_id,
                "display_name": definition.display_name,
                "status": "available" if status.available else "unavailable",
                "health": health.state,
                "routing_available": health.routing_available,
                "capabilities": list(definition.capabilities),
                "configuration": dict(definition.configuration),
                "console_url": definition.console_url,
                "usage_url": definition.usage_url,
                "billing_url": definition.billing_url,
                "recharge_url": definition.recharge_url,
                "recharge_strategy": definition.recharge_strategy,
                "action_capabilities": {
                    "usage": bool(definition.usage_url),
                    "billing": bool(definition.billing_url),
                    "recharge": bool(definition.recharge_url),
                    "console": bool(definition.console_url),
                },
            })
        return {"providers": providers, "models": models}

    def _models_for(self, selection_key: str, status: ProviderStatus) -> list[dict[str, Any]]:
        if selection_key == "deepseek":
            return [self._deepseek_model(status)]
        return self._terra_models(status)

    def _deepseek_model(self, status: ProviderStatus) -> dict[str, Any]:
        model_id = next((item.get("id") for item in status.models if item.get("id")), settings.deepseek_model_id)
        known = model_id == "deepseek-v4-flash"
        return {
            "selection_key": "deepseek",
            "provider_id": "deepseek",
            "model_id": model_id,
            "display_name": self._deepseek_display_name(model_id),
            "availability": status.available,
            "streaming": True,
            "reasoning_supported": True if known else None,
            "supported_reasoning_efforts": ["none", "low", "high", "max"] if known else [],
            # DeepSeek documents enabled thinking with a default effort of high.
            "default_reasoning_effort": "high" if known else None,
            "vision": False if known else None,
            "audio": False if known else None,
            "tool_use": True if known else None,
            "context_window": None,
            "cost_type": "api",
            "capabilities": ["text", "streaming", "reasoning", "tool_use"] if known else ["text", "streaming"],
        }

    def _terra_models(self, status: ProviderStatus) -> list[dict[str, Any]]:
        raw_model = next((item for item in status.models if item.get("id") == TERRA_MODEL_ID and not item.get("hidden", False)), None)
        efforts = [
            item.get("reasoningEffort")
            for item in (raw_model or {}).get("supportedReasoningEfforts") or []
            if isinstance(item.get("reasoningEffort"), str)
        ]
        return [{
            "selection_key": "terra",
            "provider_id": "openai_codex",
            "model_id": TERRA_MODEL_ID,
            "display_name": "GPT-5.6 Terra",
            "availability": bool(status.available and raw_model),
            "streaming": True,
            "reasoning_supported": bool(efforts) if raw_model else None,
            "supported_reasoning_efforts": efforts,
            "default_reasoning_effort": (raw_model or {}).get("defaultReasoningEffort"),
            "vision": None,
            "audio": None,
            "tool_use": None,
            "context_window": None,
            "cost_type": "subscription",
            "capabilities": ["text", "streaming", "reasoning"] if efforts else ["text", "streaming"],
        }]

    @staticmethod
    def _deepseek_display_name(model_id: str) -> str:
        return "DeepSeek V4 Flash" if model_id == "deepseek-v4-flash" else model_id

    @staticmethod
    def _safe_details(details: dict[str, Any]) -> dict[str, Any]:
        """Provider status details are already sanitized by adapters; copy them."""
        return dict(details)
