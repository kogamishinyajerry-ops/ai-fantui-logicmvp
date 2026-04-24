from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


OUT = Path("/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/tmp/pdfs/fantui_demo_pdf/screenshots")
VIEWPORT = {"width": 1672, "height": 941}


def safe_click(page, text: str, timeout: int = 2500) -> None:
    try:
        page.get_by_text(text, exact=True).click(timeout=timeout)
    except Exception:
        page.get_by_text(text).first.click(timeout=timeout)


def capture() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto("http://127.0.0.1:8002/demo.html", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(800)
        safe_click(page, "最大反推")
        page.wait_for_timeout(900)
        page.screenshot(path=OUT / "demo-cockpit.png", full_page=False)
        page.close()

        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto("http://127.0.0.1:8002/c919_etras_workstation.html", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(900)
        safe_click(page, "最大反推（MAX REV）")
        page.wait_for_timeout(900)
        page.screenshot(path=OUT / "c919-workstation.png", full_page=False)
        page.close()

        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto("http://127.0.0.1:8002/timeline-sim.html", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(800)
        page.locator("#presetSelect").select_option(label="C919 E-TRAS · TR_Inhibited 阻塞")
        page.locator("#loadPreset").click()
        page.locator("#runBtn").click()
        page.wait_for_timeout(1600)
        page.screenshot(path=OUT / "timeline-sim.png", full_page=False)
        page.close()

        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto("http://127.0.0.1:9191/", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(800)
        safe_click(page, "完全展开")
        page.wait_for_timeout(500)
        try:
            page.locator("#btnChart").click(timeout=1000)
            page.wait_for_timeout(500)
        except Exception:
            pass
        page.screenshot(path=OUT / "c919-panel.png", full_page=False)
        page.close()

        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto("http://127.0.0.1:8002/workbench.html", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(900)
        try:
            safe_click(page, "一键通过验收")
            page.wait_for_timeout(2600)
        except Exception:
            # The workbench still makes a useful artifact screenshot in its initial state.
            page.wait_for_timeout(800)
        page.screenshot(path=OUT / "workbench-bundle.png", full_page=False)
        page.close()

        browser.close()
    print(OUT)


if __name__ == "__main__":
    capture()
