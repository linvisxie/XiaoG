from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from backend.database import db as database
from backend.services.artifact_service import ArtifactKind, ArtifactPersistence, ArtifactScope, ArtifactService
class ArtifactLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir=tempfile.TemporaryDirectory(); self.patch=patch.object(database,"settings",SimpleNamespace(database_path=Path(self.temp_dir.name)/"artifacts.db")); self.patch.start(); database.initialize_database(); self.service=ArtifactService()
    def tearDown(self): self.patch.stop(); self.temp_dir.cleanup()
    def test_each_kind_has_own_scope_and_persistence(self):
        temporary=self.service.create_metadata(ArtifactKind.TEMPORARY_CHAT_ATTACHMENT,"upload.txt",conversation_id="c-1")
        artifact=self.service.create_metadata(ArtifactKind.ARTIFACT,"report.md",conversation_id="c-1")
        knowledge=self.service.create_metadata(ArtifactKind.KNOWLEDGE_FILE,"manual.pdf")
        project=self.service.create_metadata(ArtifactKind.PROJECT_ASSET,"logo.svg",project_id="p-1")
        self.assertEqual((temporary["scope"],temporary["persistence"]),(ArtifactScope.CONVERSATION,ArtifactPersistence.TEMPORARY))
        self.assertEqual((artifact["scope"],artifact["persistence"]),(ArtifactScope.CONVERSATION,ArtifactPersistence.DURABLE))
        self.assertEqual((knowledge["scope"],knowledge["persistence"]),(ArtifactScope.GLOBAL,ArtifactPersistence.DURABLE))
        self.assertEqual((project["scope"],project["persistence"]),(ArtifactScope.PROJECT,ArtifactPersistence.DURABLE))
    def test_ownership_and_recoverable_delete(self):
        with self.assertRaises(ValueError): self.service.create_metadata(ArtifactKind.ARTIFACT,"missing")
        with self.assertRaises(ValueError): self.service.create_metadata(ArtifactKind.KNOWLEDGE_FILE,"wrong",conversation_id="c-1")
        item=self.service.create_metadata(ArtifactKind.ARTIFACT,"recover.txt",conversation_id="c-1")
        self.assertTrue(self.service.move_to_trash(item["id"])); self.assertIsNotNone(self.service.get_metadata(item["id"])["deleted_at"])
        self.assertTrue(self.service.restore_from_trash(item["id"])); self.assertIsNone(self.service.get_metadata(item["id"])["deleted_at"])
if __name__ == "__main__": unittest.main()