"""Central registry; future tools must be registered here, not directly in providers."""

from backend.permissions import local_permission_policy
from backend.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list_definitions(self) -> list[dict]:
        definitions = []
        for tool in self._tools.values():
            request = tool.permission_request()
            definitions.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "requires_confirmation": tool.requires_confirmation,
                    "permission": {
                        "action": request.action,
                        "scope": request.scope,
                        **local_permission_policy.evaluate(request).as_dict(),
                    },
                }
            )
        return definitions


tool_registry = ToolRegistry()