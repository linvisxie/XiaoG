"""Targeted regression tests for v0.4.2 conversation-scoped model state."""

import asyncio
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from backend.database import db as database
from backend.database.models import ChatRequest, ConversationModelSettingsUpdate
from backend.main import chat, resolved_conversation_model_settings, resolved_default_conversation_model_settings
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
                "manual_reasoning_preferences": {},
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
                "manual_reasoning_preferences": {"terra": "ultra"},
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

    def resolve_and_save(self, conversation_id: str, mode: str, model: str, preferences: dict[str, str], scalar: str | None = None) -> dict:
        payload = ConversationModelSettingsUpdate(
            model_mode=mode,
            manual_model=model,
            manual_reasoning_effort=scalar,
            manual_reasoning_preferences=preferences,
        )
        with patch.object(model_router, "status", AsyncMock(return_value=self.registry_status())):
            resolved = asyncio.run(
                resolved_conversation_model_settings(self.service.get_conversation(conversation_id), payload)
            )
        saved = self.service.update_model_settings(conversation_id, **resolved)
        assert saved is not None
        return saved

    def test_conversation_manual_reasoning_is_scoped_by_model_and_persists(self) -> None:
        self.service.update_personalization_settings(
            {"default_model": "terra", "manual_reasoning_preferences": {"terra": "low", "deepseek": "max"}}
        )
        conversation = self.service.create_conversation(
            model_settings={
                "model_mode": "manual", "manual_model": "terra", "manual_reasoning_effort": "low",
                "manual_reasoning_preferences": {"terra": "low"},
            }
        )
        terra_high = self.resolve_and_save(conversation["id"], "manual", "terra", {"terra": "high"}, "high")
        self.assertEqual(terra_high["manual_reasoning_preferences"], {"terra": "high"})

        # The stale scalar deliberately says high. First DeepSeek use must still be its max default.
        deepseek_max = self.resolve_and_save(conversation["id"], "manual", "deepseek", {"terra": "high"}, "high")
        self.assertEqual(deepseek_max["manual_reasoning_effort"], "max")
        self.assertEqual(deepseek_max["manual_reasoning_preferences"], {"terra": "high", "deepseek": "max"})

        deepseek_low = self.resolve_and_save(conversation["id"], "manual", "deepseek", {"terra": "high", "deepseek": "low"}, "low")
        terra_restored = self.resolve_and_save(conversation["id"], "manual", "terra", deepseek_low["manual_reasoning_preferences"], "low")
        deepseek_restored = self.resolve_and_save(conversation["id"], "manual", "deepseek", terra_restored["manual_reasoning_preferences"], "high")
        self.assertEqual(terra_restored["manual_reasoning_effort"], "high")
        self.assertEqual(deepseek_restored["manual_reasoning_effort"], "low")
        self.assertEqual(self.service.get_conversation(conversation["id"])["manual_reasoning_preferences"], {"terra": "high", "deepseek": "low"})

    def test_manual_preferences_are_isolated_across_conversations_and_auto_preserves_them(self) -> None:
        self.service.update_personalization_settings(
            {"default_model": "terra", "manual_reasoning_preferences": {"terra": "low", "deepseek": "max"}}
        )
        first = self.service.create_conversation(model_settings={"model_mode": "manual", "manual_model": "terra", "manual_reasoning_effort": "low", "manual_reasoning_preferences": {"terra": "low"}})
        second = self.service.create_conversation(model_settings={"model_mode": "manual", "manual_model": "terra", "manual_reasoning_effort": "low", "manual_reasoning_preferences": {"terra": "low"}})
        first_high = self.resolve_and_save(first["id"], "manual", "terra", {"terra": "high"}, "high")
        second_low = self.resolve_and_save(second["id"], "manual", "terra", {"terra": "low"}, "low")
        self.assertEqual(first_high["manual_reasoning_effort"], "high")
        self.assertEqual(second_low["manual_reasoning_effort"], "low")

        auto = self.resolve_and_save(first["id"], "auto", "terra", first_high["manual_reasoning_preferences"])
        deepseek = self.resolve_and_save(first["id"], "manual", "deepseek", auto["manual_reasoning_preferences"], "high")
        terra = self.resolve_and_save(first["id"], "manual", "terra", deepseek["manual_reasoning_preferences"], "max")
        self.assertIsNone(auto["manual_reasoning_effort"])
        self.assertEqual(deepseek["manual_reasoning_effort"], "max")
        self.assertEqual(terra["manual_reasoning_effort"], "high")
        self.assertEqual(self.service.get_conversation(second["id"])["manual_reasoning_effort"], "low")

    def test_legacy_scalar_only_row_belongs_only_to_its_current_manual_model(self) -> None:
        conversation = self.service.create_conversation()
        # Simulate a pre-migration row: scalar only, no JSON map written.
        with database.get_connection() as conn:
            conn.execute(
                "UPDATE conversations SET model_mode = 'manual', manual_model = 'terra', manual_reasoning_effort = 'high', manual_reasoning_preferences = NULL WHERE id = ?",
                (conversation["id"],),
            )
        legacy = self.service.get_conversation(conversation["id"])
        self.assertEqual(legacy["manual_reasoning_preferences"], {"terra": "high"})
        self.service.update_personalization_settings({"manual_reasoning_preferences": {"deepseek": "max", "terra": "low"}})
        deepseek = self.resolve_and_save(conversation["id"], "manual", "deepseek", legacy["manual_reasoning_preferences"], "high")
        self.assertEqual(deepseek["manual_reasoning_effort"], "max")
        self.assertEqual(deepseek["manual_reasoning_preferences"], {"terra": "high", "deepseek": "max"})
    def test_chat_uses_persisted_manual_state_not_conflicting_request_fields(self) -> None:
        conversation = self.service.create_conversation()
        # The active scalar is DeepSeek/low while Terra retains a distinct high.
        # chat() must send the selected model's persisted effort, never Terra's.
        self.service.update_model_settings(
            conversation["id"],
            "manual",
            "deepseek",
            "low",
            {"terra": "high", "deepseek": "low"},
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