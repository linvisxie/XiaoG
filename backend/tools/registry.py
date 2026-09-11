"""Central registry; future tools must be registered here, not directly in providers."""

from backend.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list_definitions(self) -> list[dict]:
        return [{"name": tool.name, "description": tool.description, "requires_confirmation": tool.requires_confirmation} for tool in self._tools.values()]


tool_registry = ToolRegistry()
