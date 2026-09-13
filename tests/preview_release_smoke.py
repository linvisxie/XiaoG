"""Run a deterministic, no-network Preview release smoke in a separate Python process."""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


async def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        os.environ.update({
            "XIAOG_RUNTIME_MODE": "preview", "XIAOG_DATA_DIR": temporary,
            "XIAOG_LOG_DIR": f"{temporary}/logs", "XIAOG_RELEASE_ID": "wp2-local-smoke",
            "XIAOG_PREVIEW_PROVIDER_ALLOWLIST": "deepseek",
            "XIAOG_PREVIEW_INVITES": '{"smoke":"fake-preview-invite-credential-123456"}',
            # Deliberately non-real placeholder: no provider request is made in this smoke.
            "DEEPSEEK_API_KEY": "preview-smoke-placeholder",
        })
        import httpx
        from backend import main as api

        try:
            async with api.lifespan(api.app):
                transport = httpx.ASGITransport(app=api.app)
                async with httpx.AsyncClient(transport=transport, base_url="http://preview.local") as client:
                    assert (await client.get("/")).status_code == 200
                    assert (await client.get("/static/app.js")).status_code == 200
                    health = await client.get("/health")
                    assert health.status_code == 200
                    assert health.json()["runtime_mode"] == "preview"
                    assert health.json()["release_id"] == "wp2-local-smoke"
                    for route in ("/docs", "/redoc", "/openapi.json"):
                        assert (await client.get(route)).status_code == 404
                    access = await client.post("/api/preview/access", json={"credential": "fake-preview-invite-credential-123456"})
                    assert access.status_code == 200
                    cookie = access.headers["set-cookie"].split(";", 1)[0]
                    created = await client.post("/api/conversations", json={"title": "release smoke"}, headers={"cookie": cookie})
                    assert created.status_code == 201
                    assert "xiaog_preview_session=" in access.headers.get("set-cookie", "")
        finally:
            root = logging.getLogger()
            for handler in list(root.handlers):
                # This dedicated subprocess creates no other file handlers.
                # Remove all of them because Windows may canonicalize temp paths to 8.3 names.
                if isinstance(handler, logging.FileHandler):
                    root.removeHandler(handler)
                    handler.close()
            root._xiaog_diagnostics_configured = False  # type: ignore[attr-defined]
        print("Preview release smoke: passed (ASGI, fake/local dependencies only).")


if __name__ == "__main__":
    asyncio.run(main())
