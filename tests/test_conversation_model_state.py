"""Targeted regression tests for v0.4.2 conversation-scoped model state."""

import asyncio
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from backend.database import db as database
from backend.database.models import ChatRequest
from backend.main import chat, resolved_default_conversation_model_settings
from backend.router.model_router import model_router
from backend.services.conversation_service import ConversationService


class ConversationModelStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "xiaog-test.db"
        self.settings_patch = patch.object(
            database,
            "settings",
            SimpleNamespace(database_path=self.database_path),
        )
        self.settings_patch.start()
        database.initialize_database()
        self.service = ConversationService()

    def tearDown(self) -> None:
        self.settings_patch.stop()
        self.temp_dir.cleanup()

    def conversation_count(self) -> int:
        connection = sqlite3.connect(self.database_path)
        try:
            return connection.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        finally:
            connection.close()

    def test_reading_draft_defaults_does_not_create_empty_conversations(self) -> None:
        before = self.conversation_count()

        first = self.service.default_model_settings()
        second = self.service.default_model_settings()
        third = self.service.default_model_settings()

        self.assertEqual(before, self.conversation_count())
        self.assertEqual(first, second)
        self.assertEqual(second, third)
        self.assertEqual(
            first,
            {
                "model_mode": "manual",
                "manual_model": "deepseek",
                "manual_reasoning_effort": None,
            },
        )

    def test_new_conversations_snapshot_current_defaults_without_overwriting_existing(self) -> None:
        self.service.update_personalization_settings(
            {
                "default_model": "auto",
                "manual_reasoning_preferences": {"deepseek": "low", "terra": "high"},
            }
        )
        first = self.service.create_conversation()

        self.service.update_personalization_settings({"default_model": "terra"})
        second = self.service.create_conversation()

        self.assertEqual(
            self.service.get_conversation(first["id"])["model_mode"],
            "auto",
        )
        self.assertEqual(
            self.service.get_conversation(first["id"])["manual_model"],
            "deepseek",
        )
        self.assertIsNone(
            self.service.get_conversation(first["id"])["manual_reasoning_effort"],
        )
        self.assertEqual(
            self.service.get_conversation(second["id"])["model_mode"],
            "manual",
        )
        self.assertEqual(
            self.service.get_conversation(second["id"])["manual_model"],
            "terra",
        )
        self.assertEqual(
            self.service.get_conversation(second["id"])["manual_reasoning_effort"],
            "high",
        )

    def test_conversations_keep_independent_model_mode_model_and_reasoning(self) -> None:
        conversations = [self.service.create_conversation() for _ in range(3)]
        identifiers = [conversation["id"] for conversation in conversations]

        self.service.update_model_settings(identifiers[0], "manual", "deepseek", "low")
        self.service.update_model_settings(identifiers[1], "auto", "deepseek", None)
        self.service.update_model_settings(identifiers[2], "manual", "terra", "high")

        states = [
            {
                key: self.service.get_conversation(identifier)[key]
                for key in ("model_mode", "manual_model", "manual_reasoning_effort")
            }
            for identifier in identifiers
        ]
        self.assertEqual(
            states,
            [
                {
                    "model_mode": "manual",
                    "manual_model": "deepseek",
                    "manual_reasoning_effort": "low",
                },
                {
                    "model_mode": "auto",
                    "manual_model": "deepseek",
                    "manual_reasoning_effort": None,
                },
                {
                    "model_mode": "manual",
                    "manual_model": "terra",
                    "manual_reasoning_effort": "high",
                },
            ],
        )

    def registry_status(self) -> dict:
        return {
            "registry": {
                "models": [
                    {
                        "selection_key": "deepseek",
                        "model_id": "deepseek-v4-flash",
                        "supported_reasoning_efforts": ["none", "low", "high", "max"],
                        "default_reasoning_effort": "high",
                    },
                    {
                        "selection_key": "terra",
                        "model_id": "gpt-5.6-terra",
                        "supported_reasoning_efforts": ["low", "medium", "high", "xhigh", "max", "ultra"],
                        "default_reasoning_effort": "medium",
                    },
                ]
            }
        }

    def test_system_defaults_resolve_per_model_preferences_from_registry(self) -> None:
        self.service.update_personalization_settings(
            {
                "default_model": "terra",
                "manual_reasoning_preferences": {
                    "deepseek": "none",
                    "terra": "ultra",
                },
            }
        )
        with patch.object(model_router, "status", AsyncMock(return_value=self.registry_status())):
            terra_defaults = asyncio.run(resolved_default_conversation_model_settings())

        self.assertEqual(
            terra_defaults,
            {
                "model_mode": "manual",
                "manual_model": "terra",
                "manual_reasoning_effort": "ultra",
            },
        )

        self.service.update_personalization_settings(
            {
                "default_model": "deepseek",
                "manual_reasoning_preferences": {
                    "deepseek-v4-flash": "low",
                    "gpt-5.6-terra": "ultra",
                },
            }
        )
        with patch.object(model_router, "status", AsyncMock(return_value=self.registry_status())):
            legacy_defaults = asyncio.run(resolved_default_conversation_model_settings())

        self.assertEqual(legacy_defaults["manual_model"], "deepseek")
        self.assertEqual(legacy_defaults["manual_reasoning_effort"], "low")

    def test_auto_default_preserves_manual_preferences_and_new_conversation_snapshots_defaults(self) -> None:
        self.service.update_personalization_settings(
            {
                "default_model": "deepseek",
                "manual_reasoning_preferences": {"deepseek": "low", "terra": "ultra"},
            }
        )
        with patch.object(model_router, "status", AsyncMock(return_value=self.registry_status())):
            first_defaults = asyncio.run(resolved_default_conversation_model_settings())
        existing = self.service.create_conversation(model_settings=first_defaults)

        self.service.update_personalization_settings({"default_model": "auto"})
        with patch.object(model_router, "status", AsyncMock(return_value=self.registry_status())):
            auto_defaults = asyncio.run(resolved_default_conversation_model_settings())
        draft = self.service.default_model_settings()

        self.assertEqual(auto_defaults["model_mode"], "auto")
        self.assertIsNone(auto_defaults["manual_reasoning_effort"])
        self.assertEqual(draft["model_mode"], "auto")
        self.assertEqual(
            self.service.get_manual_reasoning_preferences(),
            {"deepseek": "low", "terra": "ultra"},
        )
        self.assertEqual(
            self.service.get_conversation(existing["id"])["manual_reasoning_effort"],
            "low",
        )

        self.service.update_personalization_settings({"default_model": "terra"})
        with patch.object(model_router, "status", AsyncMock(return_value=self.registry_status())):
            terra_defaults = asyncio.run(resolved_default_conversation_model_settings())
        new_conversation = self.service.create_conversation(model_settings=terra_defaults)

        self.assertEqual(
            self.service.get_conversation(new_conversation["id"])["manual_reasoning_effort"],
            "ultra",
        )
        self.assertEqual(
            self.service.get_conversation(existing["id"])["manual_model"],
            "deepseek",
        )

    def test_chat_uses_persisted_manual_state_not_conflicting_request_fields(self) -> None:
        conversation = self.service.create_conversation()
        self.service.update_model_settings(
            conversation["id"],
            "manual",
            "deepseek",
            "low",
        )
        provider = SimpleNamespace(name="test")
        select_manual = AsyncMock(
            return_value=(
                provider,
                "DeepSeek V4 Flash",
                "low",
                {"provider_id": "deepseek", "model_id": "deepseek-v4-flash"},
            )
        )
        select_auto = AsyncMock()

        async def exercise() -> None:
            response = await chat(
                conversation["id"],
                ChatRequest(
                    content="manual contract",
                    model_preference="terra",
                    reasoning_effort="ultra",
                ),
            )
            await response.body_iterator.aclose()

        with (
            patch.object(model_router, "select_manual", select_manual),
            patch.object(model_router, "select_auto", select_auto),
        ):
            asyncio.run(exercise())

        select_manual.assert_awaited_once_with("deepseek", "low")
        select_auto.assert_not_awaited()

    def test_chat_uses_auto_router_when_conversation_is_auto(self) -> None:
        conversation = self.service.create_conversation()
        self.service.update_model_settings(
            conversation["id"],
            "auto",
            "terra",
            "max",
        )
        provider = SimpleNamespace(name="test")
        select_auto = AsyncMock(
            return_value=(
                provider,
                "Auto Test",
                "medium",
                {"provider_id": "openai_codex", "model_id": "gpt-test"},
                {"rule": "test"},
            )
        )
        select_manual = AsyncMock()

        async def exercise() -> None:
            response = await chat(
                conversation["id"],
                ChatRequest(
                    content="auto contract",
                    model_preference="deepseek",
                    reasoning_effort="none",
                ),
            )
            await response.body_iterator.aclose()

        with (
            patch.object(model_router, "select_auto", select_auto),
            patch.object(model_router, "select_manual", select_manual),
        ):
            asyncio.run(exercise())

        select_auto.assert_awaited_once_with("auto contract", 0)
        select_manual.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()