"""Regression coverage for the one unified local Search Service boundary."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from backend.database import db as database
from backend.services.conversation_service import ConversationService
from backend.services.search_service import SearchDomain, SearchService


class UnifiedSearchBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "xiaog-search-test.db"
        self.settings_patch = patch.object(database, "settings", SimpleNamespace(database_path=self.database_path))
        self.settings_patch.start()
        database.initialize_database()
        self.conversations = ConversationService()
        self.search = SearchService()

    def tearDown(self) -> None:
        self.settings_patch.stop()
        self.temp_dir.cleanup()

    def test_only_implemented_conversation_domain_is_advertised(self) -> None:
        self.assertEqual(self.search.available_domains(), [SearchDomain.CONVERSATIONS])

    def test_dispatcher_keeps_domain_selection_inside_one_service(self) -> None:
        conversation = self.conversations.create_conversation("统一搜索边界")
        self.conversations.add_message(conversation["id"], "user", "可通过统一服务查找")

        all_results = self.search.search("统一服务")
        no_domains = self.search.search("统一服务", domains=())
        conversation_results = self.search.search("统一服务", domains=(SearchDomain.CONVERSATIONS,))

        self.assertEqual(len(all_results["conversations"]), 1)
        self.assertEqual(no_domains, {})
        self.assertEqual(conversation_results, all_results)


if __name__ == "__main__":
    unittest.main()