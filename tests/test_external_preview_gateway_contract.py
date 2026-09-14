"""Static, no-network checks for the WP-5B Nginx gateway contract."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "deploy" / "nginx" / "xiaog-preview.conf.template"
GUIDE = ROOT / "deploy" / "WEB_PREVIEW_WP5B_EXTERNAL_GATEWAY.md"


class ExternalPreviewGatewayContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.template = TEMPLATE.read_text(encoding="utf-8")
        self.guide = GUIDE.read_text(encoding="utf-8")

    def test_gateway_keeps_xiaog_loopback_private_and_preserves_sse(self) -> None:
        self.assertIn("proxy_pass http://127.0.0.1:8000;", self.template)
        self.assertIn("proxy_buffering off;", self.template)
        self.assertIn("proxy_read_timeout 3600s;", self.template)
        self.assertIn("proxy_send_timeout 3600s;", self.template)
        self.assertIn("X-Forwarded-Proto https", self.template)

    def test_gateway_redirects_http_and_rate_limits_invite_exchange(self) -> None:
        self.assertIn("return 308 https://__XIAOG_PUBLIC_HOST__$request_uri;", self.template)
        self.assertIn("location = /api/preview/access", self.template)
        self.assertIn("limit_req zone=xiaog_preview_access", self.template)

    def test_gateway_log_contract_excludes_secret_bearing_request_parts(self) -> None:
        access_log = self.template.split("log_format xiaog_preview_safe", 1)[1].split("limit_req_zone", 1)[0]
        self.assertNotIn("$request ", access_log)
        self.assertNotIn("$http_cookie", access_log)
        self.assertNotIn("$http_authorization", access_log)
        self.assertNotIn("$request_body", access_log)
        self.assertIn("TCP 8000 stays closed publicly", self.guide)
        self.assertIn("Terra remains unavailable/not routed", self.guide)


if __name__ == "__main__":
    unittest.main()
