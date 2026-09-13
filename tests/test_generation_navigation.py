"""Permanent regression for navigation during an originating Conversation stream."""
from pathlib import Path
import unittest
class GenerationNavigationTests(unittest.TestCase):
 def test_generation_is_owned_by_its_origin_not_global_active_ui(self):
  source=(Path(__file__).resolve().parents[1]/"frontend"/"app.js").read_text(encoding="utf-8")
  self.assertIn("generation: null",source)
  self.assertIn("const originatingConversationId = state.conversationId",source)
  self.assertIn("conversationId: originatingConversationId, controller",source)
  self.assertIn("/api/conversations/${originatingConversationId}/chat",source)
  self.assertIn("state.conversationId === originatingConversationId",source)
  self.assertNotIn("state.generating",source)
  self.assertNotIn("state.abortController",source)
 def test_navigation_and_settings_are_not_guarded_by_generation(self):
  source=(Path(__file__).resolve().parents[1]/"frontend"/"app.js").read_text(encoding="utf-8")
  for name in ("startDraft", "openConversation", "showView", "openSettings"):
   start=source.index(f"function {name}") if f"function {name}" in source else source.index(f"async function {name}")
   body=source[start:start+900]
   self.assertNotIn("isActiveGeneration()",body)
   self.assertNotIn("isCurrentConversationGenerating() return",body)
  self.assertIn("if (isCurrentConversationGenerating()) state.generation.controller.abort();",source)
if __name__=="__main__": unittest.main()