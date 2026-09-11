"""GPT-5.6 Terra adapter using only the official local Codex App Server."""

from collections.abc import AsyncIterator
from typing import Any

from backend.config import settings

from backend.providers.base import ModelProvider, ProviderError, ProviderStatus
from backend.providers.codex_app_server import CodexAppServerClient, build_canonical_context


TERRA_MODEL_ID = "gpt-5.6-terra"


class TerraProvider(ModelProvider):
    name = "openai_codex"
    model_id = TERRA_MODEL_ID
    billing_type = "subscription"

    async def _discover(self, include_rate_limits: bool = False) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
        async with CodexAppServerClient() as client:
            account = await client.request("account/read", {"refreshToken": False})
            models_result = await client.request("model/list", {"limit": 100, "includeHidden": False})
            rate_limits = None
            if include_rate_limits:
                try:
                    rate_limits = await client.request("account/rateLimits/read", {})
                except ProviderError:
                    rate_limits = None
        return account, models_result.get("data") or [], rate_limits

    async def health_check(self) -> ProviderStatus:
        try:
            account, models, rate_limits = await self._discover(include_rate_limits=True)
        except ProviderError as exc:
            return ProviderStatus(self.name, False, str(exc), [], {"auth": "unavailable"})

        account_data = account.get("account") or {}
        model_available = any(item.get("id") == TERRA_MODEL_ID and not item.get("hidden", False) for item in models)
        details = {
            "auth_mode": account_data.get("type"),
            "plan_type": account_data.get("planType"),
            "rate_limits": self._sanitize_rate_limits(rate_limits),
        }
        if account_data.get("type") != "chatgpt":
            return ProviderStatus(self.name, False, "ChatGPT 登录已失效，请在官方 Codex 中重新登录。", models, details)
        if not model_available:
            return ProviderStatus(self.name, False, "当前账户未提供 GPT-5.6 Terra", models, details)
        return ProviderStatus(self.name, True, "GPT-5.6 Terra 已通过官方 Codex App Server 验证可用。", models, details)

    async def list_models(self) -> list[dict[str, Any]]:
        _account, models, _rate_limits = await self._discover()
        return models

    async def stream_chat(self, messages: list[dict[str, str]]) -> AsyncIterator[dict[str, Any]]:
        async with CodexAppServerClient() as client:
            account = await client.request("account/read", {"refreshToken": False})
            if (account.get("account") or {}).get("type") != "chatgpt":
                raise ProviderError("ChatGPT 登录已失效，请在官方 Codex 中重新登录。")
            models_result = await client.request("model/list", {"limit": 100, "includeHidden": False})
            if not any(item.get("id") == TERRA_MODEL_ID and not item.get("hidden", False) for item in models_result.get("data") or []):
                raise ProviderError("当前账户未提供 GPT-5.6 Terra")

            thread_result = await client.request("thread/start", {
                "model": TERRA_MODEL_ID,
                "cwd": str(settings.project_root),
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "serviceName": "xiaog",
            })
            thread_id = (thread_result.get("thread") or {}).get("id")
            if not thread_id:
                raise ProviderError("Codex App Server 未能创建 Terra 会话。")
            turn_result = await client.request("turn/start", {
                "threadId": thread_id,
                "input": [{"type": "text", "text": build_canonical_context(messages)}],
                "model": TERRA_MODEL_ID,
            })
            turn = turn_result.get("turn") or {}
            turn_id = turn.get("id")
            if not turn_id:
                raise ProviderError("Codex App Server 未能启动 Terra 回复。")
            completed = False
            async for event in client.events_until_turn_complete(turn_id):
                method = event.get("method")
                params = event.get("params") or {}
                if method == "item/agentMessage/delta":
                    delta = params.get("delta")
                    if isinstance(delta, str) and delta:
                        yield {"type": "delta", "content": delta, "model": TERRA_MODEL_ID}
                if method == "turn/completed":
                    final_turn = params.get("turn") or {}
                    completed = final_turn.get("status") == "completed"
                    if not completed:
                        error = final_turn.get("error") or {}
                        raise ProviderError(f"Terra 未完成回复：{error.get('message', final_turn.get('status', 'unknown'))}")
            if not completed:
                raise ProviderError("Terra 未完成回复。")

    async def send_message(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        content = ""
        async for event in self.stream_chat(messages):
            if event["type"] == "delta":
                content += event["content"]
        return {"content": content, "usage": None, "model": TERRA_MODEL_ID}

    async def get_usage(self) -> dict[str, Any] | None:
        try:
            _account, _models, rate_limits = await self._discover(include_rate_limits=True)
            return self._sanitize_rate_limits(rate_limits)
        except ProviderError:
            return None

    @staticmethod
    def _sanitize_rate_limits(rate_limits: dict[str, Any] | None) -> dict[str, Any] | None:
        if not rate_limits:
            return None
        groups = rate_limits.get("rateLimitsByLimitId") or {}
        if not groups and rate_limits.get("rateLimits"):
            groups = {rate_limits["rateLimits"].get("limitId", "codex"): rate_limits["rateLimits"]}
        return {
            key: {
                "used_percent": (value.get("primary") or {}).get("usedPercent"),
                "window_minutes": (value.get("primary") or {}).get("windowDurationMins"),
                "resets_at": (value.get("primary") or {}).get("resetsAt"),
                "plan_type": value.get("planType"),
            }
            for key, value in groups.items()
        }