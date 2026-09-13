"""Deterministic core coverage for the Engineering Foundation test suite."""

from __future__ import annotations

import asyncio
import logging
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from backend import main as api
from backend.config import configuration_summary
from backend.database import db as database
from backend.diagnostics import RecentDiagnosticsHandler, redact_text
from backend.errors import error_detail, normalize_http_detail
from fastapi import HTTPException
from backend.database.models import ConversationCreate, PersonalizationSettingsUpdate, SettingsUpdate
from backend.router.auto_router import AutoRouter
from backend.services.conversation_service import ConversationService
from backend.services.search_service import SearchService


class CoreFoundationTests(unittest.TestCase):
    """Exercise application contracts without external Provider calls."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "xiaog-test.db"
        self.settings_patch = patch.object(database, "settings", SimpleNamespace(database_path=self.database_path))
        self.settings_patch.start()
        database.initialize_database()
        self.service = ConversationService()
        self.search = SearchService()

    def tearDown(self) -> None:
        self.settings_patch.stop()
        self.temp_dir.cleanup()

    def test_safe_additive_migration_preserves_a_legacy_conversation(self) -> None:
        self.settings_patch.stop()
        legacy_path = Path(self.temp_dir.name) / "legacy.db"
        connection = sqlite3.connect(legacy_path)
        try:
            connection.executescript(
                """
                CREATE TABLE conversations (id TEXT PRIMARY KEY, title TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
                CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
                INSERT INTO conversations VALUES ('legacy-1', '保留的历史会话', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00');
                """
            )
            connection.commit()
        finally:
            connection.close()
        self.database_path = legacy_path
        self.settings_patch = patch.object(database, "settings", SimpleNamespace(database_path=legacy_path))
        self.settings_patch.start()

        database.initialize_database()

        connection = sqlite3.connect(legacy_path)
        try:
            row = connection.execute("SELECT id, title FROM conversations WHERE id = 'legacy-1'").fetchone()
            columns = {item[1] for item in connection.execute("PRAGMA table_info(conversations)").fetchall()}
        finally:
            connection.close()
        self.assertEqual(row, ("legacy-1", "保留的历史会话"))
        self.assertTrue({"archived_at", "deleted_at", "model_mode", "manual_reasoning_preferences"}.issubset(columns))
        expected_history = ["001_core_schema", "002_conversation_lifecycle", "003_personalization_defaults", "004_file_artifact_lifecycle"]
        self.assertEqual([item["version"] for item in database.migration_history()], expected_history)
        self.assertEqual(database.schema_version(), "004_file_artifact_lifecycle")
        database.initialize_database()
        self.assertEqual([item["version"] for item in database.migration_history()], expected_history)

    def test_conversation_lifecycle_search_and_settings_contracts(self) -> None:
        conversation = self.service.create_conversation("百分号 100%_会话")
        self.service.add_message(conversation["id"], "user", "这是一条可搜索的 100%_消息")
        self.service.add_message(conversation["id"], "assistant", "已收到")

        matches = self.search.search("100%_消息")["conversations"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["conversation_id"], conversation["id"])
        self.assertEqual(matches[0]["match_type"], "user_message")

        self.assertTrue(self.service.archive_conversation(conversation["id"]))
        self.assertEqual(self.service.list_conversations(), [])
        self.assertEqual(self.service.list_conversations(archived=True)[0]["id"], conversation["id"])
        self.assertTrue(self.service.move_to_trash(conversation["id"]))
        self.assertEqual(self.search.search("100%_消息")["conversations"], [])
        self.assertTrue(self.service.restore_from_trash(conversation["id"]))
        self.assertEqual(self.service.list_conversations(archived=True)[0]["id"], conversation["id"])
        self.assertTrue(self.service.restore_conversation(conversation["id"]))
        self.assertEqual(self.service.list_conversations()[0]["id"], conversation["id"])

        self.service.update_settings("系统提示", "用户资料")
        self.service.update_personalization_settings(
            {"default_model": "terra", "manual_reasoning_preferences": {"terra": "high", "deepseek": "low"}}
        )
        preferences = self.service.get_personalization_settings()
        self.assertEqual(self.service.get_setting("system_prompt"), "系统提示")
        self.assertEqual(preferences["default_model"], "terra")
        self.assertEqual(preferences["manual_reasoning_preferences"], {"terra": "high", "deepseek": "low"})

    def test_direct_api_contracts_use_local_services(self) -> None:
        with (
            patch.object(api, "conversation_service", self.service),
            patch.object(api, "search_service", self.search),
        ):
            health = asyncio.run(api.health())
            created = asyncio.run(api.create_conversation(ConversationCreate(title="API 会话")))
            listed = asyncio.run(api.list_conversations())
            settings_result = asyncio.run(api.update_settings(SettingsUpdate(system_prompt="提示", user_profile="资料")))
            personalization = asyncio.run(
                api.update_personalization_settings(
                    PersonalizationSettingsUpdate(theme_mode="dark", color_scheme="blue", default_model="auto")
                )
            )
            searched = asyncio.run(api.search("API 会话"))

        self.assertEqual(health["status"], "ok")
        self.assertEqual(created["title"], "API 会话")
        self.assertEqual([item["id"] for item in listed], [created["id"]])
        self.assertEqual(settings_result["message"], "设置已保存。")
        self.assertEqual(personalization["theme_mode"], "dark")
        self.assertEqual(searched["results"][0]["conversation_id"], created["id"])

    def test_configuration_summary_separates_ownership_without_secret_values(self) -> None:
        summary = configuration_summary()
        self.assertEqual(summary["provider_secrets"], {"source": "local .env", "exposed": False})
        self.assertEqual(summary["user_settings"]["source"], "SQLite settings table")
        self.assertEqual(summary["product_metadata"]["source"], "product_info.json")
        self.assertEqual(summary["runtime_state"]["source"], "in-memory service state")
        self.assertNotIn("deepseek_api_key", repr(summary).lower())
    def test_error_contract_preserves_message_and_exposes_retry_metadata(self) -> None:
        provider = normalize_http_detail(
            HTTPException(status_code=503, detail={"code": "provider_unavailable", "message": "Provider 暂不可用。"})
        )
        missing = normalize_http_detail(HTTPException(status_code=404, detail="找不到该会话。"))
        unexpected = error_detail("internal_error", "请稍后重试。", retryable=True)

        self.assertEqual(provider, {"code": "provider_unavailable", "message": "Provider 暂不可用。", "retryable": True, "retry_action": "retry"})
        self.assertEqual(missing, {"code": "not_found", "message": "找不到该会话。", "retryable": False, "retry_action": None})
        self.assertEqual(unexpected["retry_action"], "retry")
    def test_diagnostics_redact_credentials_from_text_and_recent_events(self) -> None:
        secret = "sk-this-must-not-appear-123456789"
        safe = redact_text(f"Authorization: Bearer {secret}; api_key={secret}; token={secret}")
        self.assertNotIn(secret, safe)
        self.assertIn("[REDACTED]", safe)

        handler = RecentDiagnosticsHandler(limit=2)
        handler.emit(logging.LogRecord("test", logging.WARNING, __file__, 1, "request failed: %s", (f"Bearer {secret}",), None))
        event = handler.snapshot()[0]
        self.assertEqual(event["logger"], "test")
        self.assertNotIn(secret, event["message"])
    def test_auto_router_is_deterministic_and_uses_available_registry_models(self) -> None:
        models = {
            "deepseek": {
                "availability": True,
                "supported_reasoning_efforts": ["low", "high"],
                "default_reasoning_effort": "high",
            },
            "terra": {
                "availability": True,
                "supported_reasoning_efforts": ["medium", "high"],
                "default_reasoning_effort": "medium",
            },
        }
        complex_decision = AutoRouter.decide("请分析这个复杂代码 bug 并给出方案", 0, models)
        standard_decision = AutoRouter.decide("你好", 0, models)
        fallback = AutoRouter.decide("分析代码 bug", 0, {**models, "terra": {**models["terra"], "availability": False}})

        self.assertEqual((complex_decision.selection_key, complex_decision.selected_effort), ("terra", "medium"))
        self.assertEqual((standard_decision.selection_key, standard_decision.selected_effort), ("deepseek", "low"))
        self.assertEqual(fallback.selection_key, "deepseek")


if __name__ == "__main__":
    unittest.main()