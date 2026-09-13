"""Regression coverage for the local-first permission abstraction."""

from __future__ import annotations

import asyncio
import unittest

from backend.permissions import (
    LocalPermissionPolicy,
    PermissionAction,
    PermissionDecision,
    PermissionRequest,
    PermissionScope,
)
from backend.tools.base import Tool
from backend.tools.registry import ToolRegistry


class LocalPermissionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = LocalPermissionPolicy()

    def test_local_read_and_write_are_allowed(self) -> None:
        for action in (PermissionAction.READ, PermissionAction.WRITE):
            result = self.policy.evaluate(PermissionRequest(action, "conversation:local"))
            self.assertEqual(result.decision, PermissionDecision.ALLOW)

    def test_delete_and_external_actions_require_explicit_confirmation(self) -> None:
        for action in (PermissionAction.DELETE, PermissionAction.EXTERNAL_ACTION):
            result = self.policy.evaluate(PermissionRequest(action, "conversation:local"))
            self.assertEqual(result.decision, PermissionDecision.REQUIRE_CONFIRMATION)

    def test_sensitive_and_non_local_actions_are_denied_by_default(self) -> None:
        sensitive = self.policy.evaluate(PermissionRequest(PermissionAction.SENSITIVE_ACTION, "provider:credential"))
        remote = self.policy.evaluate(
            PermissionRequest(PermissionAction.READ, "remote:file", scope=PermissionScope.REMOTE)
        )
        self.assertEqual(sensitive.decision, PermissionDecision.DENY)
        self.assertEqual(remote.decision, PermissionDecision.DENY)

    def test_tool_registry_exposes_the_same_permission_contract(self) -> None:
        class BrowserTool(Tool):
            name = "open_browser"
            description = "Open an external provider console."

            async def run(self, arguments: dict) -> str:
                return "opened"

        registry = ToolRegistry()
        registry.register(BrowserTool())
        definition = registry.list_definitions()[0]

        self.assertEqual(definition["permission"]["action"], PermissionAction.EXTERNAL_ACTION)
        self.assertEqual(definition["permission"]["scope"], PermissionScope.LOCAL)
        self.assertEqual(definition["permission"]["decision"], PermissionDecision.REQUIRE_CONFIRMATION)
        self.assertEqual(asyncio.run(BrowserTool().run({})), "opened")


if __name__ == "__main__":
    unittest.main()