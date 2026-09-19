import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LocalRuntimeUiTests(unittest.TestCase):
    def test_runtime_status_is_hidden_from_chat_header(self) -> None:
        html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "frontend" / "style.css").read_text(encoding="utf-8")
        self.assertRegex(html, r'id="runtime-status"[^>]*\bhidden\b')
        self.assertIn(".runtime-status[hidden] { display:none !important; }", css)
        self.assertIn("local-runtime-r2", html)

    def test_runtime_status_reader_is_retained_for_future_diagnostics(self) -> None:
        source = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
        self.assertIn("async function loadRuntimeStatus()", source)
        self.assertIn('request("/health", { cache: "no-store" })', source)


if __name__ == "__main__":
    unittest.main()
