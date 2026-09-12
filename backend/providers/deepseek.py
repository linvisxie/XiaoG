"""Official DeepSeek Chat Completions adapter, isolated from XiaoG core."""

from collections.abc import AsyncIterator
import json

import httpx

from backend.config import settings
from backend.providers.base import ModelProvider, ProviderError, ProviderStatus


class DeepSeekProvider(ModelProvider):
    name = "deepseek"

    def _configured(self) -> bool:
        return bool(settings.deepseek_api_key)

    async def health_check(self) -> ProviderStatus:
        if not self._configured():
            return ProviderStatus(self.name, False, "DeepSeek API尚未配置。", await self.list_models())
        return ProviderStatus(self.name, True, "DeepSeek 已配置；实际连通性会在发送消息时验证。", await self.list_models())

    async def list_models(self) -> list[dict[str, str | bool]]:
        return [{
            "id": settings.deepseek_model_id,
            "display_name": "DeepSeek V4 Flash",
            "available": self._configured(),
        }]

    def _headers(self) -> dict[str, str]:
        if not self._configured():
            raise ProviderError("DeepSeek API尚未配置。请在 .env 中填写 DEEPSEEK_API_KEY 后重启小G。")
        return {"Authorization": f"Bearer {settings.deepseek_api_key}", "Content-Type": "application/json"}

    def _payload(self, messages: list[dict[str, str]], stream: bool) -> dict:
        return {
            "model": settings.deepseek_model_id,
            "messages": messages,
            "stream": stream,
            "stream_options": {"include_usage": True} if stream else None,
            "thinking": {"type": "disabled"},
        }

    @staticmethod
    def _friendly_error(status_code: int, body: str) -> str:
        lower = body.lower()
        if status_code in (401, 403):
            return "DeepSeek API Key 无效或没有权限，请检查 .env 配置。"
        if status_code == 402 or "insufficient balance" in lower or "balance" in lower:
            return "DeepSeek余额不足，请前往 DeepSeek 平台充值后重试。"
        if status_code == 429:
            return "DeepSeek请求过于频繁，请稍后再试。"
        if status_code >= 500:
            return "DeepSeek服务暂时不可用，请稍后重试。"
        return "DeepSeek连接失败，请检查网络、API配置或稍后重试。"

    async def stream_chat(self, messages: list[dict[str, str]], reasoning_effort: str | None = None) -> AsyncIterator[dict]:
        url = f"{settings.deepseek_base_url}/chat/completions"
        timeout = httpx.Timeout(connect=15.0, read=180.0, write=30.0, pool=30.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, headers=self._headers(), json=self._payload(messages, True)) as response:
                    if response.status_code >= 400:
                        body = await response.aread()
                        raise ProviderError(self._friendly_error(response.status_code, body.decode("utf-8", "ignore")))
                    async for line in response.aiter_lines():
                        if not line or line.startswith(":") or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        choices = chunk.get("choices") or []
                        if choices:
                            delta = choices[0].get("delta") or {}
                            content = delta.get("content")
                            if content:
                                yield {"type": "delta", "content": content}
                        if chunk.get("usage"):
                            yield {"type": "usage", "usage": chunk["usage"], "model": chunk.get("model", settings.deepseek_model_id)}
        except ProviderError:
            raise
        except httpx.TimeoutException as exc:
            raise ProviderError("DeepSeek响应超时，请检查网络或稍后重试。") from exc
        except httpx.RequestError as exc:
            raise ProviderError("DeepSeek连接失败，请检查网络或API配置。") from exc

    async def send_message(self, messages: list[dict[str, str]], reasoning_effort: str | None = None) -> dict:
        text = ""
        usage = None
        model = settings.deepseek_model_id
        async for event in self.stream_chat(messages, reasoning_effort):
            if event["type"] == "delta":
                text += event["content"]
            elif event["type"] == "usage":
                usage, model = event["usage"], event["model"]
        return {"content": text, "usage": usage, "model": model}

    async def get_usage(self) -> dict | None:
        return None
