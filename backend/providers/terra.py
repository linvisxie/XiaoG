"""GPT-5.6 Terra adapter using the persistent official Codex App Server."""

import logging
from collections.abc import AsyncIterator
from typing import Any

from backend.config import settings
from backend.providers.base import ModelProvider, ProviderError, ProviderStatus
from backend.providers.codex_app_server import build_canonical_context
from backend.services.codex_app_server_manager import codex_app_server_manager
from backend.services.conversation_service import conversation_service


TERRA_MODEL_ID = "gpt-5.6-terra"
logger = logging.getLogger(__name__)


class TerraProvider(ModelProvider):
    name = "openai_codex"
    model_id = TERRA_MODEL_ID
    billing_type = "subscription"

    async def _discover(self, include_rate_limits: bool = False) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
        return await codex_app_server_manager.discovery(include_rate_limits=include_rate_limits)

    async def health_check(self) -> ProviderStatus:
        try:
            account, models, rate_limits = await self._discover(include_rate_limits=True)
        except ProviderError as exc:
            return ProviderStatus(self.name, False, str(exc), [], {"auth": "unavailable"})

        model = self._terra_model(models)
        details = {
            "auth_mode": account.get("type"),
            "plan_type": account.get("planType"),
            "rate_limits": self._sanitize_rate_limits(rate_limits),
            "supported_reasoning_efforts": self._supported_efforts(model),
            "default_reasoning_effort": (model or {}).get("defaultReasoningEffort"),
            "app_server_pid": codex_app_server_manager.process_id,
        }
        if account.get("type") != "chatgpt":
            return ProviderStatus(self.name, False, "ChatGPT 登录已失效，请在官方 Codex 中重新登录。", models, details)
        if not model:
            return ProviderStatus(self.name, False, "当前账户未提供 GPT-5.6 Terra", models, details)
        return ProviderStatus(self.name, True, "GPT-5.6 Terra 已通过官方 Codex App Server 验证可用。", models, details)

    async def list_models(self) -> list[dict[str, Any]]:
        _account, models, _rate_limits = await self._discover()
        return models

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        reasoning_effort: str | None = None,
        conversation_id: str | None = None,
        user_message_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream one Terra turn over the shared app-server connection.

        A persisted XiaoG conversation reuses its Codex thread.  On later Terra
        turns, only messages written by non-Terra providers since the previous
        synchronized user message are injected, retaining cross-model context
        without resending the whole SQLite history.
        """
        async with codex_app_server_manager.turn_session() as client:
            account = codex_app_server_manager.account
            models = codex_app_server_manager.models
            if account.get("type") != "chatgpt":
                raise ProviderError("ChatGPT 登录已失效，请在官方 Codex 中重新登录。")
            model = self._terra_model(models)
            if not model:
                raise ProviderError("当前账户未提供 GPT-5.6 Terra")
            supported_efforts = self._supported_efforts(model)
            effort = reasoning_effort or model.get("defaultReasoningEffort")
            if effort not in supported_efforts:
                raise ProviderError("当前账户不支持所选的 Terra 推理档位，请刷新页面后重试。")

            conversation = conversation_service.get_conversation(conversation_id) if conversation_id else None
            thread_id = (conversation or {}).get("codex_thread_id")
            resumed = False
            if thread_id:
                try:
                    await client.request("thread/resume", {"threadId": thread_id})
                    resumed = True
                except ProviderError:
                    # The Codex thread may have been deleted externally. Recreate
                    # it from XiaoG-owned history and update only the local ID.
                    logger.warning("Stored Codex thread could not be resumed; creating a replacement thread.")
                    conversation_service.clear_codex_thread(conversation_id)
                    thread_id = None
                    conversation = conversation_service.get_conversation(conversation_id)

            if not thread_id:
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
                if conversation_id:
                    conversation_service.set_codex_thread(conversation_id, thread_id)

            prompt = self._resumed_context(messages, conversation, conversation_id, user_message_id) if resumed else build_canonical_context(messages)
            turn_result = await client.request("turn/start", {
                "threadId": thread_id,
                "input": [{"type": "text", "text": prompt}],
                "model": TERRA_MODEL_ID,
                "effort": effort,
            })
            turn = turn_result.get("turn") or {}
            turn_id = turn.get("id")
            if not turn_id:
                raise ProviderError("Codex App Server 未能启动 Terra 回复。")
            if conversation_id and user_message_id:
                # The current user input is already part of this Codex turn.
                conversation_service.set_codex_last_synced_message(conversation_id, user_message_id)

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

    def _resumed_context(
        self,
        messages: list[dict[str, str]],
        conversation: dict[str, Any] | None,
        conversation_id: str | None,
        user_message_id: str | None,
    ) -> str:
        if not conversation or not conversation_id or not user_message_id:
            return build_canonical_context(messages)
        marker = conversation.get("codex_last_synced_message_id")
        if not marker:
            return build_canonical_context(messages)
        pending = conversation_service.messages_after(conversation_id, marker)
        # Codex already has its own prior Terra turns. Keep all user messages and
        # sync DeepSeek assistant/tool output so model switching remains coherent.
        pending = [item for item in pending if item.get("provider") != self.name]
        compact_messages = ([messages[0]] if messages and messages[0].get("role") == "system" else []) + [
            {"role": item["role"], "content": item["content"]}
            for item in pending
            if item.get("role") in ("user", "assistant", "tool")
        ]
        return build_canonical_context(compact_messages or messages)

    async def send_message(self, messages: list[dict[str, str]], reasoning_effort: str | None = None) -> dict[str, Any]:
        content = ""
        async for event in self.stream_chat(messages, reasoning_effort):
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

    @staticmethod
    def _terra_model(models: list[dict[str, Any]]) -> dict[str, Any] | None:
        return next((item for item in models if item.get("id") == TERRA_MODEL_ID and not item.get("hidden", False)), None)

    @staticmethod
    def _supported_efforts(model: dict[str, Any] | None) -> list[str]:
        return [
            item["reasoningEffort"]
            for item in (model or {}).get("supportedReasoningEfforts") or []
            if isinstance(item.get("reasoningEffort"), str)
        ]