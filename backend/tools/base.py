"""Future G-BRIDGE tool contract. No real system controls exist in v0.1."""

from abc import ABC, abstractmethod

from backend.permissions import PermissionAction, PermissionRequest


class Tool(ABC):
    name: str
    description: str
    requires_confirmation: bool = True
    permission_action: PermissionAction = PermissionAction.EXTERNAL_ACTION

    def permission_request(self) -> PermissionRequest:
        """Return the capability a future caller must evaluate before running."""

        return PermissionRequest(
            action=self.permission_action,
            resource=f"tool:{self.name}",
            reason=self.description,
        )

    @abstractmethod
    async def run(self, arguments: dict) -> str: ...