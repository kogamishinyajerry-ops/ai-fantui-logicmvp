import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const outDir = "/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/tmp/slides/fantui_logicmvp_demo_pages/screens";
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 810 },
  deviceScaleFactor: 1,
});

async function shot(page, file) {
  await page.screenshot({ path: path.join(outDir, file), fullPage: false });
}

async function waitQuiet(page) {
  await page.waitForTimeout(800);
}

try {
  const demo = await context.newPage();
  await demo.goto("http://127.0.0.1:8812/demo.html", { waitUntil: "networkidle" });
  await demo.click('button[data-preset="max-reverse"]');
  await waitQuiet(demo);
  await shot(demo, "demo-fantui-cockpit.png");

  const etras = await context.newPage();
  await etras.goto("http://127.0.0.1:8812/c919_etras_workstation.html", { waitUntil: "networkidle" });
  await etras.click('button[data-preset="landing-deploy"]');
  await waitQuiet(etras);
  await shot(etras, "demo-c919-workstation.png");

  const timeline = await context.newPage();
  await timeline.goto("http://127.0.0.1:8812/timeline-sim.html", { waitUntil: "networkidle" });
  await timeline.selectOption("#presetSelect", "fantui_sw1_stuck");
  await timeline.click("#runBtn");
  await timeline.waitForFunction(() => {
    const status = document.querySelector("#status")?.textContent || "";
    const outcome = document.querySelector("#outcomeGrid")?.textContent || "";
    return /完成|OK|成功/i.test(status) || /blocked|FAILED|阻塞|true|false/i.test(outcome);
  }, { timeout: 10000 }).catch(async () => waitQuiet(timeline));
  await shot(timeline, "demo-timeline-sim.png");

  const fanSim = await context.newPage();
  await fanSim.goto("http://127.0.0.1:8812/fan_sim_panel.html", { waitUntil: "networkidle" });
  await waitQuiet(fanSim);
  await shot(fanSim, "demo-monitor-timeline.png");
} finally {
  await browser.close();
}

console.log(`screens=${outDir}`);
