"""Transparent local rules for Auto Router v1; it never calls an LLM to route."""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any


@dataclass(frozen=True)
class RoutingDecision:
    selection_key: str
    selected_effort: str | None
    task_class: str
    routing_time_ms: float
    routing_explanation: str


class AutoRouter:
    """Choose only from currently available Registry models using local signals."""

    _CODE_MARKERS = ("```", "def ", "class ", "function ", "traceback", "error:", "bug", "debug", "代码", "报错", "调试")
    _STRUCTURED_MARKERS = ("json", "schema", "table", "plan", "compare", "design", "分析", "比较", "方案", "设计", "步骤", "结构化")
    _REASONING_MARKERS = ("why", "prove", "reason", "tradeoff", "because", "为什么", "推理", "论证", "权衡", "深入")

    @classmethod
    def decide(cls, content: str, context_characters: int, models: dict[str, dict[str, Any]]) -> RoutingDecision:
        started = perf_counter()
        normalized = content.lower()
        score = 0
        tags: list[str] = []
        if len(content) >= 900:
            score += 2
            tags.append("long_input")
        elif len(content) >= 350:
            score += 1
            tags.append("medium_input")
        if context_characters >= 12000:
            score += 2
            tags.append("long_context")
        elif context_characters >= 5000:
            score += 1
            tags.append("context")
        if any(marker in normalized for marker in cls._CODE_MARKERS):
            score += 3
            tags.append("code")
        if any(marker in normalized for marker in cls._STRUCTURED_MARKERS):
            score += 2
            tags.append("structured")
        if any(marker in normalized for marker in cls._REASONING_MARKERS):
            score += 2
            tags.append("reasoning")

        terra = models.get("terra")
        deepseek = models.get("deepseek")
        if score >= 4 and terra and terra.get("availability"):
            effort = cls._effort(terra, "high" if score >= 6 else "medium")
            task_class = "complex_" + (tags[0] if tags else "task")
            key = "terra"
        elif deepseek and deepseek.get("availability"):
            effort = cls._effort(deepseek, "high" if score >= 3 else "low")
            task_class = "standard_" + (tags[0] if tags else "chat")
            key = "deepseek"
        elif terra and terra.get("availability"):
            effort = cls._effort(terra, "medium")
            task_class = "fallback_terra"
            key = "terra"
        else:
            raise ValueError("没有可用模型可供 Auto Router 选择。")
        return RoutingDecision(key, effort, task_class, round((perf_counter() - started) * 1000, 3), f"local_rules:{task_class}")

    @staticmethod
    def _effort(model: dict[str, Any], preferred: str) -> str | None:
        supported = model.get("supported_reasoning_efforts") or []
        if not supported:
            return None
        return preferred if preferred in supported else model.get("default_reasoning_effort") or supported[0]
