"""The provider contract. XiaoG core calls this, never a vendor SDK directly."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


class ProviderError(Exception):
    """A safe, user-facing provider error."""


@dataclass
class ProviderStatus:
    provider: str
    available: bool
    message: str
    models: list[dict[str, Any]]
    details: dict[str, Any] = field(default_factory=dict)


class ModelProvider(ABC):
    name: str

    @abstractmethod
    async def health_check(self) -> ProviderStatus: ...

    @abstractmethod
    async def list_models(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def stream_chat(self, messages: list[dict[str, str]], reasoning_effort: str | None = None) -> AsyncIterator[dict[str, Any]]: ...

    @abstractmethod
    async def send_message(self, messages: list[dict[str, str]], reasoning_effort: str | None = None) -> dict[str, Any]: ...

    @abstractmethod
    async def get_usage(self) -> dict[str, Any] | None: ...