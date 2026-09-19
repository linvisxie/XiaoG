"""Real-browser verification that runtime diagnostics never occupy the chat header."""

from __future__ import annotations

import asyncio
import os

from playwright.async_api import async_playwright


EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE_URL = os.environ.get("XIAOG_E2E_BASE_URL", "http://127.0.0.1:8000")


async def assert_hidden(page, stage: str) -> None:
    locator = page.locator("#runtime-status")
    assert await locator.count() == 1, f"{stage}: expected one runtime status node"
    state = await locator.evaluate(
        "element => ({hidden: element.hidden, display: getComputedStyle(element).display, text: element.textContent})"
    )
    assert state["hidden"] is True, f"{stage}: hidden was false"
    assert state["display"] == "none", f"{stage}: computed display was {state['display']}"
    assert "后端在线" in state["text"], f"{stage}: runtime status reading did not complete"
    print(f"{stage}: hidden=true display=none status-data=retained")


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=EDGE, headless=True)
        try:
            page = await browser.new_page()
            await page.goto(f"{BASE_URL}/?runtime-status-e2e=r3", wait_until="domcontentloaded")
            await page.wait_for_function("document.querySelector('#runtime-status')?.textContent.includes('后端在线')")
            await assert_hidden(page, "fresh-page")

            await page.locator("#runtime-status").evaluate("element => { element.hidden = false; }")
            stale_display = await page.locator("#runtime-status").evaluate("element => getComputedStyle(element).display")
            assert stale_display == "none", f"stale-dom: computed display was {stale_display}"
            print("stale-dom-before-refresh: hidden=false display=none")
            await page.reload(wait_until="domcontentloaded")
            await page.wait_for_function("document.querySelector('#runtime-status')?.textContent.includes('后端在线')")
            await assert_hidden(page, "stale-tab-refresh")

            current = await page.locator("#model-select").input_value()
            target = "deepseek" if current != "deepseek" else "auto"
            await page.select_option("#model-select", target)
            await page.wait_for_timeout(250)
            await assert_hidden(page, "model-switch")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
