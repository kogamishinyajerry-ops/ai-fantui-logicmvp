import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");
const outDir = path.resolve(repoRoot, "tmp/slides/logicmvp_project_proposal_20260424/live_screens");
const appBase = process.env.LOGICMVP_SCREENSHOT_BASE || "http://127.0.0.1:18002";

await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
  locale: "zh-CN",
});

async function capture(name, url, options = {}) {
  const page = await context.newPage();
  await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
  if (options.before) await options.before(page);
  await page.waitForTimeout(options.wait ?? 600);
  await page.screenshot({ path: path.resolve(outDir, `${name}.png`), fullPage: false });
  await page.close();
}

await capture("01_surface_index", `${appBase}/index.html`);

await capture("02_fantui_workstation", `${appBase}/demo.html`, {
  before: async (page) => {
    const button = page.getByText("着陆展开全链路").first();
    if (await button.count()) await button.click();
  },
  wait: 900,
});

await capture("03_c919_etras_workstation", `${appBase}/c919_etras_workstation.html`, {
  before: async (page) => {
    const button = page.getByText("着陆展开全链路").first();
    if (await button.count()) await button.click();
  },
  wait: 900,
});

await capture("04_timeline_simulator", `${appBase}/timeline-sim.html`, {
  before: async (page) => {
    await page.locator("#presetSelect").selectOption("fantui_sw1_stuck");
    await page.locator("#loadPreset").click();
    await page.locator("#runBtn").click();
    await page.waitForSelector(".logic-row", { timeout: 8000 }).catch(() => {});
  },
  wait: 1000,
});

await capture("05_validation_workbench", `${appBase}/workbench.html`, {
  before: async (page) => {
    const button = page.getByText("载入样例").first();
    if (await button.count()) await button.click();
    const generate = page.getByText("跑 Bundle").first();
    if (await generate.count()) await generate.click();
  },
  wait: 1200,
});

await capture("06_fantui_circuit", `${appBase}/fantui_circuit.html`);
await capture("07_c919_circuit", `${appBase}/c919_etras_panel/circuit.html`);
await capture("08_c919_mfd_panel", "http://127.0.0.1:9191/", {
  before: async (page) => {
    const deep = page.getByText("DEPLOY").first();
    if (await deep.count()) await deep.click().catch(() => {});
  },
  wait: 800,
});

await browser.close();

console.log(JSON.stringify({ outDir }, null, 2));
