"""Regression coverage for v0.4.3 Provider Management metadata."""

import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from backend.main import get_providers
from backend.providers.base import ProviderStatus
from backend.router.model_router import model_router
from backend.services.model_registry import ModelRegistry


class StubProvider:
    def __init__(self, status: ProviderStatus) -> None:
        self._status = status

    async def health_check(self) -> ProviderStatus:
        return self._status


class ProviderManagementTests(unittest.IsolatedAsyncioTestCase):
    async def test_registry_exposes_safe_provider_management_metadata(self) -> None:
        registry = ModelRegistry(
            {
                "deepseek": StubProvider(ProviderStatus("deepseek", True, "ok", [{"id": "deepseek-v4-flash"}])),
                "terra": StubProvider(
                    ProviderStatus(
                        "openai_codex", True, "ok",
                        [{"id": "gpt-5.6-terra", "supportedReasoningEfforts": [{"reasoningEffort": "low"}], "defaultReasoningEffort": "low"}],
                    )
                ),
            }
        )

        snapshot = await registry.snapshot()
        providers = {provider["selection_key"]: provider for provider in snapshot["providers"]}

        self.assertEqual(set(providers), {"deepseek", "terra"})
        self.assertEqual(providers["deepseek"]["status"], "available")
        self.assertEqual(providers["deepseek"]["health"], "healthy")
        self.assertTrue(providers["deepseek"]["routing_available"])
        self.assertEqual(providers["deepseek"]["usage_url"], "https://platform.deepseek.com/usage")
        self.assertEqual(providers["deepseek"]["billing_url"], "https://platform.deepseek.com/balance")
        self.assertEqual(providers["deepseek"]["recharge_url"], "https://platform.deepseek.com/top_up")
        self.assertIsNone(providers["deepseek"]["recharge_strategy"])
        self.assertEqual(providers["deepseek"]["action_capabilities"], {"usage": True, "billing": True, "recharge": True, "console": True})
        self.assertEqual(providers["terra"]["console_url"], "https://chatgpt.com/")
        self.assertEqual(providers["terra"]["usage_url"], "https://platform.openai.com/usage")
        self.assertEqual(providers["terra"]["billing_url"], "https://platform.openai.com/account/billing/overview")
        self.assertEqual(providers["terra"]["recharge_url"], "https://platform.openai.com/account/billing/overview")
        self.assertEqual(providers["terra"]["recharge_strategy"], "billing_overview")
        self.assertEqual(providers["terra"]["action_capabilities"], {"usage": True, "billing": True, "recharge": True, "console": True})
        self.assertNotEqual(providers["terra"]["recharge_url"], providers["deepseek"]["recharge_url"])
        rendered = repr(snapshot).lower()
        self.assertNotIn("sk-", rendered)
        self.assertNotIn("api_key=", rendered)

    def test_provider_management_actions_are_metadata_capability_driven(self) -> None:
        frontend = (Path(__file__).resolve().parents[1] / "frontend" / "app.js").read_text(encoding="utf-8")
        self.assertIn('[["usage", "查看用量", provider.usage_url], ["billing", "管理账单 / 额度", provider.billing_url], ["recharge", "充值", provider.recharge_url], ["console", "打开官方控制台", provider.console_url]]', frontend)
        self.assertIn("actionCapabilities && actionCapabilities[action] !== true", frontend)
        self.assertIn("renderManualReasoning(); renderProviderManagement(); syncModelStatus();", frontend)
        self.assertNotIn("provider.recharge_url || provider.billing_url", frontend)
    async def test_provider_management_endpoint_reuses_registry_snapshot(self) -> None:
        expected = {"providers": [{"selection_key": "test", "status": "available"}], "models": []}
        with patch.object(model_router.registry, "snapshot", AsyncMock(return_value=expected)) as snapshot:
            self.assertEqual(await get_providers(), expected)
        snapshot.assert_awaited_once_with()


if __name__ == "__main__":
    unittest.main()
