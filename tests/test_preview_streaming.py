"""WP-3 fake-stream regression: every terminal chat path releases Preview concurrency."""
from __future__ import annotations
import asyncio, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from backend import main as api
from backend.database.db import initialize_database, use_database_path
from backend.database.models import ChatRequest
from backend.providers.base import ProviderError
from backend.services.conversation_service import ConversationService

class Provider:
 name="deepseek"; billing_type="api"
 def __init__(self, mode): self.mode=mode; self.wait=asyncio.Event()
 async def stream_chat(self,*_args):
  if self.mode=="error": raise ProviderError("fake stream error")
  yield {"type":"delta","content":"ok"}
  if self.mode=="cancel": await self.wait.wait()
  yield {"type":"usage","usage":{},"model":"deepseek-v4-flash"}

class Router:
 def __init__(self,p): self.p=p
 async def select_manual(self,*_args): return self.p,"Fake",None,{"model_id":"deepseek-v4-flash","provider_id":"deepseek"}

class StreamingReleaseTests(unittest.TestCase):
 def run_path(self, mode):
  async def exercise():
   with tempfile.TemporaryDirectory() as d:
    from backend.preview_access import PreviewAccessControl
    runtime=SimpleNamespace(preview_enabled=True,preview_max_input_chars=1000,preview_generation_limit=10,preview_window_seconds=60,preview_max_concurrent_per_invite=1,preview_max_concurrent_global=1,preview_invites={"a":"x"})
    control=PreviewAccessControl(runtime); path=Path(d)/"a.db"
    with use_database_path(path): initialize_database(); conversation=ConversationService().create_conversation("stream")
    token=control.current_invite.set("a")
    try:
     with use_database_path(path), patch.object(api,"settings",SimpleNamespace(runtime=runtime)), patch.object(api,"preview_access",control), patch.object(api,"model_router",Router(Provider(mode))):
      response=await api.chat(conversation["id"],ChatRequest(content="hello")); iterator=response.body_iterator
      if mode=="cancel": await iterator.__anext__(); await iterator.aclose()
      else:
       async for _ in iterator: pass
      self.assertEqual(control.global_active,0); self.assertTrue(control.acquire_generation("a")); control.release_generation("a")
    finally: control.current_invite.reset(token)
  asyncio.run(exercise())
 def test_success_releases(self): self.run_path("success")
 def test_error_releases(self): self.run_path("error")
 def test_cancel_releases(self): self.run_path("cancel")
