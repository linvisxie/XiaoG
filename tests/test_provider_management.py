"""Regression coverage for v0.4.3 Provider Management metadata."""

import unittest
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
        self.assertEqual(providers["deepseek"]["usage_url"], "https://platform.deepseek.com/usage")
        self.assertEqual(providers["deepseek"]["billing_url"], "https://platform.deepseek.com/balance")
        self.assertEqual(providers["deepseek"]["recharge_url"], "https://platform.deepseek.com/top_up")
        self.assertEqual(providers["terra"]["console_url"], "https://chatgpt.com/")
        self.assertIsNone(providers["terra"]["recharge_url"])
        rendered = repr(snapshot).lower()
        self.assertNotIn("sk-", rendered)
        self.assertNotIn("api_key=", rendered)

    async def test_provider_management_endpoint_reuses_registry_snapshot(self) -> None:
        expected = {"providers": [{"selection_key": "test", "status": "available"}], "models": []}
        with patch.object(model_router.registry, "snapshot", AsyncMock(return_value=expected)) as snapshot:
            self.assertEqual(await get_providers(), expected)
        snapshot.assert_awaited_once_with()


if __name__ == "__main__":
    unittest.main()
