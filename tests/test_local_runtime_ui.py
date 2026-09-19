import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LocalRuntimeUiTests(unittest.TestCase):
    def test_diagnostic_status_nodes_are_hidden_from_chat_header(self) -> None:
        html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "frontend" / "style.css").read_text(encoding="utf-8")
        self.assertRegex(html, r'id="provider-note"[^>]*\bhidden\b')
        self.assertRegex(html, r'id="runtime-status"[^>]*\bhidden\b')
        self.assertIn(".provider-note { display:none !important; }", css)
        self.assertIn(".runtime-status { display:none !important; }", css)
        self.assertNotIn(".runtime-status[hidden]", css)
        self.assertIn("local-runtime-r4", html)

    def test_runtime_status_reader_is_retained_for_future_diagnostics(self) -> None:
        source = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
        self.assertIn('const providerNote = $("#provider-note"); if (providerNote) providerNote.hidden = true;', source)
        self.assertIn('request("/api/provider-status")', source)
        self.assertIn("async function loadRuntimeStatus()", source)
        self.assertIn('const element = $("#runtime-status"); if (!element) return;\n  element.hidden = true;', source)
        self.assertIn('request("/health", { cache: "no-store" })', source)


if __name__ == "__main__":
    unittest.main()
