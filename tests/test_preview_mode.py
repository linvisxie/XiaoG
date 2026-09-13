"""Deterministic WP-1 tests; no listener, Provider, secret, or local user DB is used."""

from __future__ import annotations

import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.config import RuntimeConfig
from backend.database.db import initialize_database, use_database_path
from backend.preview import PreviewSessionRegistry, preview_provider_allowlist, preview_surface_options
from backend.providers.base import ProviderStatus
from backend.services.conversation_service import ConversationService
from backend.services.model_registry import ModelRegistry


class _FakeProvider:
    def __init__(self, provider_id: str) -> None:
        self.provider_id = provider_id
        self.health_calls = 0

    async def health_check(self) -> ProviderStatus:
        self.health_calls += 1
        return ProviderStatus(self.provider_id, True, "available", [{"id": "deepseek-v4-flash"}])


class PreviewModeTests(unittest.TestCase):
    def test_local_defaults_remain_local_and_preview_requires_explicit_identity(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            local = RuntimeConfig()
        self.assertEqual(local.runtime_mode, "local")
        self.assertEqual(local.host, "127.0.0.1")
        self.assertEqual(local.port, 8000)
        self.assertEqual(local.data_dir, (Path(__file__).resolve().parents[1] / "data").resolve())

        with tempfile.TemporaryDirectory() as temporary:
            with patch.dict(os.environ, {
                "XIAOG_RUNTIME_MODE": "preview", "XIAOG_DATA_DIR": temporary,
                "XIAOG_RELEASE_ID": "wp1-test-release", "XIAOG_PREVIEW_PROVIDER_ALLOWLIST": "deepseek", "XIAOG_PREVIEW_INVITES": '{"test":"fake-preview-invite-credential-123456"}',
            }, clear=True):
                preview = RuntimeConfig()
        self.assertTrue(preview.preview_enabled)
        self.assertNotEqual(preview.data_dir, local.data_dir)
        self.assertEqual(preview_provider_allowlist(preview), frozenset({"deepseek"}))
        self.assertEqual(preview_surface_options(preview), {"docs_url": None, "redoc_url": None, "openapi_url": None})

        with patch.dict(os.environ, {"XIAOG_RUNTIME_MODE": "preview"}, clear=True):
            with self.assertRaises(ValueError):
                RuntimeConfig()

        with tempfile.TemporaryDirectory() as temporary:
            with patch.dict(os.environ, {
                "XIAOG_RUNTIME_MODE": "preview", "XIAOG_DATA_DIR": temporary,
                "XIAOG_RELEASE_ID": "wp1-test-release", "XIAOG_PREVIEW_PROVIDER_ALLOWLIST": "deepseek,terra",
            }, clear=True):
                with self.assertRaises(ValueError):
                    RuntimeConfig()

    def test_preview_sessions_are_transient_and_cannot_read_each_others_conversations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            registry = PreviewSessionRegistry(Path(temporary))
            registry.reset_for_startup()
            token_a, database_a, created_a = registry.database_for(None)
            token_b, database_b, created_b = registry.database_for(None)
            self.assertTrue(created_a and created_b)
            self.assertNotEqual(token_a, token_b)
            self.assertNotEqual(database_a, database_b)

            with use_database_path(database_a):
                initialize_database()
                conversation_a = ConversationService().create_conversation("A only")
                self.assertEqual([item["id"] for item in ConversationService().list_conversations()], [conversation_a["id"]])
            with use_database_path(database_b):
                initialize_database()
                self.assertEqual(ConversationService().list_conversations(), [])
                self.assertIsNone(ConversationService().get_conversation(conversation_a["id"]))

            registry.reset_for_startup()
            self.assertFalse(database_a.exists())
            self.assertFalse(database_b.exists())

    def test_preview_provider_policy_allows_deepseek_without_calling_terra(self) -> None:
        deepseek = _FakeProvider("deepseek")
        terra = _FakeProvider("openai_codex")
        registry = ModelRegistry({"deepseek": deepseek, "terra": terra}, frozenset({"deepseek"}))
        snapshot = asyncio.run(registry.snapshot())
        models = {item["selection_key"]: item for item in snapshot["models"]}
        self.assertTrue(models["deepseek"]["availability"])
        self.assertFalse(models["terra"]["availability"])
        self.assertEqual(deepseek.health_calls, 1)
        self.assertEqual(terra.health_calls, 0)


if __name__ == "__main__":
    unittest.main()
