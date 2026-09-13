from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from backend.database import db as database
from backend.services.backup_service import BackupConflictError, BackupService
from backend.services.conversation_service import ConversationService

class BackupServiceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.path=Path(self.temp.name)/"backup.db"; self.patch=patch.object(database,"settings",SimpleNamespace(database_path=self.path)); self.patch.start(); database.initialize_database(); self.conversations=ConversationService(); self.service=BackupService()
 def tearDown(self): self.patch.stop(); self.temp.cleanup()
 def test_export_and_safe_additive_import(self):
  conversation=self.conversations.create_conversation("可迁移对话"); self.conversations.add_message(conversation["id"],"user","保留内容"); snapshot=self.service.export_snapshot(); self.assertEqual(snapshot["format"],"xiaog-local-backup"); self.assertEqual(len(snapshot["data"]["conversations"]),1)
  target=Path(self.temp.name)/"target.db"
  with patch.object(database,"settings",SimpleNamespace(database_path=target)):
   database.initialize_database(); result=BackupService().import_snapshot(snapshot); self.assertEqual(result["conversations"],1); self.assertEqual(ConversationService().list_conversations()[0]["title"],"可迁移对话")
 def test_conflict_never_overwrites_existing_data(self):
  self.conversations.create_conversation("本地数据"); snapshot=self.service.export_snapshot()
  with self.assertRaises(BackupConflictError): self.service.import_snapshot(snapshot)
  self.assertEqual(self.conversations.list_conversations()[0]["title"],"本地数据")
if __name__=="__main__": unittest.main()
