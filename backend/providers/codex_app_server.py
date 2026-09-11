"""Official Codex App Server JSON-RPC client.

It delegates ChatGPT authentication to the installed Codex CLI.  It never reads,
stores, forwards, or logs ChatGPT credentials.
"""

import asyncio
import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from backend.config import settings
from backend.providers.base import ProviderError


class CodexAppServerClient:
    """One stdio JSON-RPC session to the locally installed official Codex CLI."""

    def __init__(self) -> None:
        self._process: asyncio.subprocess.Process | None = None
        self._next_id = 1
        self._buffered_events: list[dict[str, Any]] = []

    async def __aenter__(self) -> "CodexAppServerClient":
        await self.start()
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.close()

    async def start(self) -> None:
        if self.is_running:
            return
        try:
            self._process = await asyncio.create_subprocess_exec(
                "codex", "app-server",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(settings.project_root),
            )
        except FileNotFoundError as exc:
            raise ProviderError("未找到 Codex CLI。请安装或更新官方 Codex 后重试。") from exc
        await self.request("initialize", {
            "clientInfo": {"name": "xiaog", "title": "XiaoG", "version": "0.1.0"},
        })
        await self.notify("initialized", {})

    @property
    def is_running(self) -> bool:
        return bool(self._process and self._process.returncode is None)

    @property
    def process_id(self) -> int | None:
        return self._process.pid if self.is_running and self._process else None

    async def close(self) -> None:
        if not self._process:
            return
        if self._process.stdin:
            self._process.stdin.close()
            try:
                await self._process.stdin.wait_closed()
            except (ConnectionError, BrokenPipeError):
                pass
        if self._process.returncode is None:
            self._process.terminate()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=3)
            except TimeoutError:
                self._process.kill()
                await self._process.wait()
        self._process = None

    async def notify(self, method: str, params: dict[str, Any]) -> None:
        await self._send({"method": method, "params": params})

    async def request(self, method: str, params: dict[str, Any], timeout: float = 30) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        await self._send({"id": request_id, "method": method, "params": params})
        while True:
            message = await self._read(timeout)
            if message.get("id") != request_id:
                if "method" in message:
                    self._buffered_events.append(message)
                continue
            if "error" in message:
                error = message["error"]
                raise ProviderError(self._friendly_protocol_error(method, str(error.get("message", error))))
            return message.get("result") or {}

    async def events_until_turn_complete(self, turn_id: str) -> AsyncIterator[dict[str, Any]]:
        while self._buffered_events:
            yield self._buffered_events.pop(0)
        while True:
            message = await self._read(180)
            if "method" not in message:
                continue
            yield message
            if message["method"] == "turn/completed":
                turn = (message.get("params") or {}).get("turn") or {}
                if turn.get("id") == turn_id:
                    return

    async def _send(self, message: dict[str, Any]) -> None:
        if not self._process or not self._process.stdin:
            raise ProviderError("Codex App Server 未启动。")
        self._process.stdin.write((json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8"))
        await self._process.stdin.drain()

    async def _read(self, timeout: float) -> dict[str, Any]:
        if not self._process or not self._process.stdout:
            raise ProviderError("Codex App Server 未启动。")
        try:
            line = await asyncio.wait_for(self._process.stdout.readline(), timeout=timeout)
        except TimeoutError as exc:
            raise ProviderError("Codex App Server 响应超时，请稍后重试。") from exc
        if not line:
            raise ProviderError("Codex App Server 意外停止。请检查 Codex 登录状态。")
        try:
            return json.loads(line.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ProviderError("Codex App Server 返回了无法识别的数据。") from exc

    @staticmethod
    def _friendly_protocol_error(method: str, message: str) -> str:
        lower = message.lower()
        if "unauthorized" in lower or "login" in lower or "auth" in lower:
            return "ChatGPT 登录已失效，请在官方 Codex 中重新登录后重试。"
        if method == "model/list":
            return "无法读取当前 ChatGPT 账户的 Codex 模型列表。"
        return f"Codex App Server 请求失败：{message}"


def build_canonical_context(messages: list[dict[str, str]]) -> str:
    """Render XiaoG-owned history as a single, transparent input for Codex."""
    labels = {"system": "小G系统指令", "user": "用户", "assistant": "小G", "tool": "工具"}
    lines = [
        "你正在作为个人 AI 助手“小G”回答。",
        "以下是 XiaoG 自己保存的规范上下文。保持其中的人格和对话连续性。",
        "这是普通聊天任务：不要调用工具、不要执行命令、不要修改文件。直接给出自然、诚实、简洁的回答。",
        "--- XiaoG 上下文开始 ---",
    ]
    for message in messages:
        role = labels.get(message.get("role", "user"), "用户")
        lines.append(f"[{role}]\n{message.get('content', '')}")
    lines.append("--- XiaoG 上下文结束 ---")
    lines.append("请只回答最后一条用户消息，不要解释这段上下文的格式。")
    return "\n\n".join(lines)