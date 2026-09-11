"""Future G-BRIDGE tool contract. No real system controls exist in v0.1."""

from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str
    requires_confirmation: bool = True

    @abstractmethod
    async def run(self, arguments: dict) -> str: ...
