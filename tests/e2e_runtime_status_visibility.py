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


async def assert_provider_note_hidden(page, stage: str) -> None:
    locator = page.locator("#provider-note")
    assert await locator.count() == 1, f"{stage}: expected one provider note node"
    state = await locator.evaluate(
        "element => ({hidden: element.hidden, display: getComputedStyle(element).display, text: element.textContent})"
    )
    assert state["hidden"] is True, f"{stage}: provider note hidden was false"
    assert state["display"] == "none", f"{stage}: provider note display was {state['display']}"
    assert state["text"] != "正在检查模型状态…", f"{stage}: provider status reading did not complete"
    print(f"{stage}: provider-note hidden=true display=none status-data=retained")


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=EDGE, headless=True)
        try:
            page = await browser.new_page()
            await page.goto(f"{BASE_URL}/?status-visibility-e2e=r4", wait_until="domcontentloaded")
            await page.wait_for_function("document.querySelector('#runtime-status')?.textContent.includes('后端在线')")
            await page.wait_for_function("document.querySelector('#provider-note')?.textContent !== '正在检查模型状态…'")
            await assert_hidden(page, "fresh-page")
            await assert_provider_note_hidden(page, "fresh-page")
            provider_response = await page.request.get(f"{BASE_URL}/api/provider-status")
            assert provider_response.ok, f"provider status returned {provider_response.status}"
            provider_status = await provider_response.json()
            assert provider_status["deepseek"]["available"] is True, "DeepSeek should remain available"
            assert provider_status["terra"]["available"] is False, "test requires Terra unavailable evidence"
            provider_note_text = await page.locator("#provider-note").text_content()
            assert provider_note_text == provider_status["terra"]["message"], "provider diagnostic data was not retained"
            print("provider-api: DeepSeek available, Terra unavailable diagnostic retained off-screen")

            await page.locator("#runtime-status").evaluate("element => { element.hidden = false; }")
            await page.locator("#provider-note").evaluate("element => { element.hidden = false; }")
            stale_display = await page.locator("#runtime-status").evaluate("element => getComputedStyle(element).display")
            stale_provider_display = await page.locator("#provider-note").evaluate("element => getComputedStyle(element).display")
            assert stale_display == "none", f"stale-dom: computed display was {stale_display}"
            assert stale_provider_display == "none", f"stale-dom: provider note display was {stale_provider_display}"
            print("stale-dom-before-refresh: hidden=false display=none")
            await page.reload(wait_until="domcontentloaded")
            await page.wait_for_function("document.querySelector('#runtime-status')?.textContent.includes('后端在线')")
            await page.wait_for_function("document.querySelector('#provider-note')?.textContent !== '正在检查模型状态…'")
            await assert_hidden(page, "stale-tab-refresh")
            await assert_provider_note_hidden(page, "stale-tab-refresh")

            current = await page.locator("#model-select").input_value()
            target = "deepseek" if current != "deepseek" else "auto"
            await page.select_option("#model-select", target)
            await page.wait_for_timeout(250)
            await assert_hidden(page, "model-switch")
            await assert_provider_note_hidden(page, "model-switch")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
