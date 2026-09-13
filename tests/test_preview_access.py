"""Deterministic WP-3 boundary tests; no network or real credential is used."""
from __future__ import annotations
import os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from backend.config import RuntimeConfig
from backend.diagnostics import redact_text
from backend.preview_access import PreviewAccessControl
from backend.database.db import initialize_database, use_database_path
from backend.services.conversation_service import ConversationService

FAKE_A="fake-invite-a-credential-1234567890"; FAKE_B="fake-invite-b-credential-1234567890"

class PreviewAccessTests(unittest.TestCase):
 def make(self, directory, **overrides):
  env={"XIAOG_RUNTIME_MODE":"preview","XIAOG_DATA_DIR":directory,"XIAOG_RELEASE_ID":"test","XIAOG_PREVIEW_PROVIDER_ALLOWLIST":"deepseek","XIAOG_PREVIEW_INVITES":'{"invite-a":"'+FAKE_A+'","invite-b":"'+FAKE_B+'"}',"XIAOG_PREVIEW_REQUEST_LIMIT":"1","XIAOG_PREVIEW_GENERATION_LIMIT":"1","XIAOG_PREVIEW_MAX_CONCURRENT_PER_INVITE":"1","XIAOG_PREVIEW_MAX_CONCURRENT_GLOBAL":"1"}; env.update(overrides)
  with patch.dict(os.environ, env, clear=True): return RuntimeConfig()
 def test_invalid_invite_creates_no_session_or_database_and_redacts_secret(self):
  with tempfile.TemporaryDirectory() as d:
   control=PreviewAccessControl(self.make(d)); root=Path(d)/"preview-sessions"; root.mkdir()
   self.assertIsNone(control.exchange("wrong-credential",root)); self.assertEqual(list(root.glob("*.db")),[]); self.assertNotIn(FAKE_A,redact_text(f"token={FAKE_A}"))
 def test_invite_binding_cross_invite_isolation_and_no_secret_in_sqlite(self):
  with tempfile.TemporaryDirectory() as d:
   control=PreviewAccessControl(self.make(d)); root=Path(d)/"preview-sessions"; root.mkdir(); a=control.exchange(FAKE_A,root); b=control.exchange(FAKE_B,root)
   self.assertEqual(control.session(a.token).invite_id,"invite-a"); self.assertEqual(control.session(b.token).invite_id,"invite-b")
   with use_database_path(a.database_path): initialize_database(); c=ConversationService().create_conversation("A")
   with use_database_path(b.database_path): initialize_database(); self.assertIsNone(ConversationService().get_conversation(c["id"]))
   self.assertNotIn(FAKE_A,a.database_path.read_bytes().decode("latin1")); self.assertNotIn(FAKE_B,b.database_path.read_bytes().decode("latin1"))
 def test_request_generation_and_concurrency_limits_release(self):
  with tempfile.TemporaryDirectory() as d:
   control=PreviewAccessControl(self.make(d)); self.assertTrue(control.allow_request("invite-a")); self.assertFalse(control.allow_request("invite-a")); self.assertTrue(control.allow_request("invite-b")); self.assertFalse(control.allow_request("invite-b"))
   control=PreviewAccessControl(self.make(d)); self.assertTrue(control.acquire_generation("invite-a")); self.assertFalse(control.acquire_generation("invite-a")); self.assertFalse(control.acquire_generation("invite-b")); control.release_generation("invite-a"); self.assertTrue(control.acquire_generation("invite-b")); control.release_generation("invite-b"); self.assertEqual(control.global_active,0)
 def test_logout_invalidates_original_session(self):
  with tempfile.TemporaryDirectory() as d:
   control=PreviewAccessControl(self.make(d)); root=Path(d)/"preview-sessions"; root.mkdir(); session=control.exchange(FAKE_A,root); control.logout(session.token); self.assertIsNone(control.session(session.token))

if __name__=="__main__": unittest.main()
