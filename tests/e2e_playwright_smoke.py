"""Deterministic local Playwright/Edge and HTTP-readiness smoke.

This starts an isolated in-process HTTP server, proves readiness with HTTP 200,
and performs one DOM click in headless Edge. It makes no XiaoG API or Provider
call and is not a product-experience test.
"""
from __future__ import annotations

import asyncio
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.request import urlopen

from playwright.async_api import async_playwright


EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def mark(stage: str) -> None:
    print(f"{time.monotonic():.3f} {stage}", flush=True)


async def bounded(stage: str, operation):
    mark(f"{stage}:begin")
    try:
        result = await asyncio.wait_for(operation, timeout=10)
    except TimeoutError as exc:
        mark(f"{stage}:timeout")
        raise RuntimeError(f"E2E smoke timed out at {stage}") from exc
    mark(f"{stage}:end")
    return result


def start_server() -> tuple[ThreadingHTTPServer, str]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args) -> None:
            return

        def do_GET(self) -> None:
            if self.path == "/health":
                payload = b"ok"
            elif self.path == "/":
                payload = b"<button id='ok'>OK</button>"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}"


async def wait_ready(base: str) -> None:
    last_error = ""
    for _ in range(50):
        try:
            status = await asyncio.to_thread(lambda: urlopen(base + "/health", timeout=1).status)
            if status == 200:
                mark("SERVER_READY_HTTP_200")
                return
        except (OSError, URLError) as exc:
            last_error = repr(exc)
        await asyncio.sleep(0.1)
    raise RuntimeError(f"E2E smoke server readiness timed out: {last_error}")


async def main() -> None:
    server, base = start_server()
    mark("SERVER_START")
    try:
        await wait_ready(base)
        async with async_playwright() as playwright:
            browser = await bounded(
                "browser.launch",
                playwright.chromium.launch(executable_path=EDGE, headless=True, timeout=10_000),
            )
            try:
                page = await bounded("browser.new_page", browser.new_page())
                await bounded("page.goto", page.goto(base, wait_until="domcontentloaded", timeout=10_000))
                await bounded("page.click", page.locator("#ok").click())
            finally:
                await bounded("browser.close", browser.close())
    finally:
        server.shutdown()
        server.server_close()
        mark("SERVER_STOPPED")
    mark("smoke:pass")


if __name__ == "__main__":
    asyncio.run(main())