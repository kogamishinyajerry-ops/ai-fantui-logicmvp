import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const { Presentation, PresentationFile } = await import("@oai/artifact-tool");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");
const outDir = __dirname;
const scratchDir = path.resolve(repoRoot, "tmp/slides/logicmvp_project_proposal_20260424");
const screenshotPath = path.resolve(repoRoot, "runs/codex_c919_reliability_screenshot.png");
const screenshotCropPath = path.resolve(scratchDir, "c919_workstation_top.png");
const liveScreenDir = path.resolve(scratchDir, "live_screens");
const finalPath = path.resolve(outDir, "ai_fantui_logicmvp_project_proposal.pptx");

const W = 1280;
const H = 720;

const C = {
  bg: "#071014",
  bg2: "#0B171C",
  panel: "#10232B",
  panel2: "#17313A",
  panel3: "#1F3B3F",
  line: "#2C5961",
  line2: "#3F6C75",
  teal: "#00B7C7",
  teal2: "#36E2D6",
  green: "#37D98B",
  amber: "#F2B84B",
  red: "#E95E63",
  white: "#F6FAFB",
  muted: "#9BB3BA",
  dim: "#587078",
  ink: "#0A1115",
};

const FONT = {
  title: "Microsoft YaHei",
  body: "Microsoft YaHei",
  mono: "Consolas",
};

const presentation = Presentation.create({
  slideSize: { width: W, height: H },
});

await fs.mkdir(scratchDir, { recursive: true });
await sharp(screenshotPath)
  .extract({ left: 0, top: 0, width: 1440, height: 900 })
  .png()
  .toFile(screenshotCropPath);

async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function saveBlobLike(blob, outputPath) {
  if (blob && typeof blob.save === "function") {
    await blob.save(outputPath);
    return;
  }
  if (blob instanceof Uint8Array) {
    await fs.writeFile(outputPath, blob);
    return;
  }
  if (blob instanceof ArrayBuffer) {
    await fs.writeFile(outputPath, new Uint8Array(blob));
    return;
  }
  if (blob?.data instanceof Uint8Array) {
    await fs.writeFile(outputPath, blob.data);
    return;
  }
  if (blob?.data instanceof ArrayBuffer) {
    await fs.writeFile(outputPath, new Uint8Array(blob.data));
    return;
  }
  if (typeof blob === "string") {
    const base64 = blob.startsWith("data:")
      ? blob.slice(blob.indexOf(",") + 1)
      : blob;
    await fs.writeFile(outputPath, Buffer.from(base64, "base64"));
    return;
  }
  if (blob && typeof blob.arrayBuffer === "function") {
    const data = await blob.arrayBuffer();
    await fs.writeFile(outputPath, new Uint8Array(data));
    return;
  }
  const tag = Object.prototype.toString.call(blob);
  const keys = blob && typeof blob === "object" ? Object.keys(blob).join(",") : "";
  throw new Error(`Unsupported export blob type ${tag} keys=[${keys}] for ${outputPath}`);
}

function addShape(slide, geometry, x, y, w, h, opts = {}) {
  const shape = slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h, rotation: opts.rotation || 0 },
    fill: opts.fill ?? "#00000000",
    line: opts.line ?? { style: "solid", fill: "#00000000", width: 0 },
    adjustmentList: opts.adjustmentList,
  });
  return shape;
}

function addText(slide, text, x, y, w, h, opts = {}) {
  const shape = addShape(slide, "rect", x, y, w, h, {
    fill: opts.fill ?? "#00000000",
    line: opts.line ?? { style: "solid", fill: "#00000000", width: 0 },
  });
  shape.text = text;
  shape.text.typeface = opts.typeface ?? FONT.body;
  shape.text.fontSize = opts.fontSize ?? 24;
  shape.text.color = opts.color ?? C.white;
  shape.text.bold = Boolean(opts.bold);
  shape.text.alignment = opts.align ?? "left";
  shape.text.verticalAlignment = opts.valign ?? "top";
  shape.text.insets = opts.insets ?? { left: 0, right: 0, top: 0, bottom: 0 };
  if (opts.autoFit) shape.text.autoFit = opts.autoFit;
  return shape;
}

function addTitle(slide, title, kicker = "") {
  if (kicker) {
    addText(slide, kicker, 72, 42, 640, 28, {
      fontSize: 16,
      color: C.teal2,
      bold: true,
      typeface: FONT.body,
    });
  }
  addText(slide, title, 72, 72, 860, 58, {
    fontSize: 36,
    bold: true,
    color: C.white,
    typeface: FONT.title,
    autoFit: "shrinkText",
  });
}

function addFooter(slide, page) {
  addText(slide, "AI FANTUI LogicMVP · 立项申请汇报", 72, 674, 420, 20, {
    fontSize: 12,
    color: C.dim,
  });
  addText(slide, String(page).padStart(2, "0"), 1168, 666, 42, 28, {
    fontSize: 18,
    color: C.teal2,
    bold: true,
    align: "right",
  });
  addShape(slide, "rect", 72, 650, 1136, 1, {
    fill: C.line,
    line: { style: "solid", fill: C.line, width: 0 },
  });
}

function bg(slide, variant = "default") {
  slide.background.fill = variant === "light" ? "#F5F7F8" : C.bg;
  addShape(slide, "rect", 0, 0, W, H, {
    fill: variant === "light" ? "#F5F7F8" : C.bg,
  });
  if (variant !== "light") {
    addShape(slide, "rect", 0, 0, W, 88, { fill: "#091922" });
    addShape(slide, "rect", 0, 620, W, 100, { fill: "#050B0E" });
    for (let i = 0; i < 9; i += 1) {
      addShape(slide, "rect", 80 + i * 140, 138 + (i % 3) * 62, 82, 1, {
        fill: i % 2 === 0 ? C.line : "#18323A",
      });
    }
  }
}

function card(slide, x, y, w, h, opts = {}) {
  return addShape(slide, "roundRect", x, y, w, h, {
    fill: opts.fill ?? C.panel,
    line: opts.line ?? { style: "solid", fill: C.line, width: 1.2 },
    adjustmentList: [{ name: "adj", formula: "val 14000" }],
  });
}

function chip(slide, text, x, y, w, color = C.teal2) {
  card(slide, x, y, w, 34, {
    fill: "#0D2027",
    line: { style: "solid", fill: color, width: 1 },
  });
  addText(slide, text, x + 12, y + 7, w - 24, 18, {
    fontSize: 13,
    color,
    bold: true,
    align: "center",
    valign: "middle",
  });
}

function metricCard(slide, label, value, note, x, y, w, h, color = C.teal2) {
  card(slide, x, y, w, h, { fill: "#0C1B21" });
  addText(slide, label, x + 18, y + 16, w - 36, 22, {
    fontSize: 14,
    color: C.muted,
  });
  addText(slide, value, x + 18, y + 45, w - 36, 42, {
    fontSize: 30,
    color,
    bold: true,
    autoFit: "shrinkText",
  });
  addText(slide, note, x + 18, y + 94, w - 36, h - 106, {
    fontSize: 13,
    color: C.muted,
    autoFit: "shrinkText",
  });
}

function liveScreen(name) {
  return path.resolve(liveScreenDir, `${name}.png`);
}

async function imagePlate(slide, imagePath, x, y, w, h, opts = {}) {
  const img = slide.images.add({
    blob: await readImageBlob(imagePath),
    fit: opts.fit ?? "cover",
    alt: opts.alt ?? path.basename(imagePath),
  });
  img.position = { left: x, top: y, width: w, height: h };
  if (opts.crop) img.crop = opts.crop;
  addShape(slide, "rect", x, y, w, h, {
    fill: "#00000000",
    line: { style: "solid", fill: opts.border ?? C.line2, width: opts.borderWidth ?? 1.2 },
  });
  if (opts.label) {
    addShape(slide, "rect", x, y, w, 30, { fill: "#061017CC" });
    addText(slide, opts.label, x + 12, y + 7, w - 24, 16, {
      fontSize: opts.labelSize ?? 13,
      color: opts.labelColor ?? C.teal2,
      bold: true,
      autoFit: "shrinkText",
    });
  }
  return img;
}

function bullet(slide, text, x, y, w, color = C.teal2) {
  addShape(slide, "ellipse", x, y + 7, 8, 8, { fill: color });
  addText(slide, text, x + 18, y, w - 18, 34, {
    fontSize: 17,
    color: C.white,
    autoFit: "shrinkText",
  });
}

function addSpeakerNotes(slide, notes) {
  if (slide.speakerNotes?.setText) {
    slide.speakerNotes.setText(notes);
  }
}

function addMiniGrid(slide, x, y, w, h) {
  for (let i = 0; i <= 5; i += 1) {
    addShape(slide, "rect", x, y + (h / 5) * i, w, 1, { fill: "#17343C" });
  }
  for (let i = 0; i <= 8; i += 1) {
    addShape(slide, "rect", x + (w / 8) * i, y, 1, h, { fill: "#17343C" });
  }
}

function slide1() {
  const slide = presentation.slides.add();
  bg(slide);
  addMiniGrid(slide, 668, 116, 468, 312);
  addShape(slide, "rect", 0, 0, W, H, { fill: "#071014" });
  addShape(slide, "rect", 52, 42, 1176, 600, {
    fill: "#091820",
    line: { style: "solid", fill: "#163741", width: 1.2 },
  });
  addShape(slide, "rect", 52, 42, 8, 600, { fill: C.teal });
  addText(slide, "AI FANTUI LogicMVP", 92, 82, 420, 34, {
    fontSize: 18,
    color: C.teal2,
    bold: true,
  });
  addText(slide, "飞控/机电控制逻辑\n数字孪生验证工作台", 92, 142, 740, 128, {
    fontSize: 46,
    bold: true,
    color: C.white,
    typeface: FONT.title,
    autoFit: "shrinkText",
  });
  addText(slide, "项目立项申请汇报", 96, 292, 560, 34, {
    fontSize: 22,
    color: C.muted,
  });
  chip(slide, "不替代飞控", 96, 366, 136, C.green);
  chip(slide, "不训练大模型", 248, 366, 150, C.amber);
  chip(slide, "做验证与审计底座", 414, 366, 190, C.teal2);
  metricCard(slide, "推荐建设周期", "18个月", "T0+6个月看到试点，T0+18个月形成生产验证能力", 96, 452, 250, 126, C.teal2);
  metricCard(slide, "经费测算", "1800–2600万", "推荐按生产验证型预算申报，采购以正式询价为准", 372, 452, 286, 126, C.amber);
  metricCard(slide, "算力资源", "既有数据中心", "首期不新建大型训练中心，按资源池分阶段扩容", 684, 452, 292, 126, C.green);
  card(slide, 768, 122, 366, 244, { fill: "#0B1D24" });
  addText(slide, "项目一句话", 800, 154, 140, 24, { fontSize: 16, color: C.teal2, bold: true });
  addText(slide, "把复杂控制逻辑的“人工经验验证”，升级为可复现、可审计、可扩展的数字孪生验证工作台。", 800, 198, 286, 90, {
    fontSize: 24,
    color: C.white,
    bold: true,
    autoFit: "shrinkText",
  });
  addText(slide, "当前已有样机基础：C919 电反推逻辑工作台、时间线仿真、适配器边界、765项测试通过。", 800, 304, 286, 42, {
    fontSize: 13,
    color: C.muted,
    autoFit: "shrinkText",
  });
  addText(slide, "2026-04-25", 1090, 600, 100, 20, { fontSize: 12, color: C.dim, align: "right" });
  addSpeakerNotes(slide, "开场只讲三件事：本项目不是替代飞控，不是堆大模型训练集群，而是做航空控制逻辑验证、诊断、审计的数字孪生工作台。后续重点回答预算、周期、算力和阶段成果。");
}

function slide2() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "本次立项申请的关键事项", "Executive request");
  const items = [
    ["立项预算", "建议按18个月生产验证型申报：1800–2600万元，推荐中值2200万元。"],
    ["试点范围", "先选1个真实子系统做PoC，再扩至3–5个子系统进入生产验证。"],
    ["算力资源", "首期使用既有数据中心资源池；生产验证期配置4–8张数据中心GPU。"],
    ["数据授权", "提供规范文档、典型故障场景、验证流程样例，不要求敏感飞控源码外传。"],
  ];
  items.forEach((it, idx) => {
    const x = 84 + (idx % 2) * 560;
    const y = 176 + Math.floor(idx / 2) * 166;
    card(slide, x, y, 510, 126, { fill: idx === 0 ? "#172E30" : C.panel });
    addText(slide, `0${idx + 1}`, x + 22, y + 18, 42, 36, { fontSize: 26, color: idx === 0 ? C.amber : C.teal2, bold: true });
    addText(slide, it[0], x + 84, y + 20, 190, 30, { fontSize: 23, color: C.white, bold: true });
    addText(slide, it[1], x + 84, y + 60, 380, 42, { fontSize: 17, color: C.muted, autoFit: "shrinkText" });
  });
  card(slide, 84, 532, 1070, 68, { fill: "#101F25", line: { style: "solid", fill: C.amber, width: 1.4 } });
  addText(slide, "推荐审批口径", 110, 550, 142, 24, { fontSize: 17, color: C.amber, bold: true });
  addText(slide, "“先试点、后生产验证、再平台化”：资金分阶段拨付，算力分阶段上架，成果每3–6个月可见。", 268, 549, 810, 28, {
    fontSize: 22,
    color: C.white,
    bold: true,
    autoFit: "shrinkText",
  });
  addFooter(slide, 2);
  addSpeakerNotes(slide, "这一页先把申请讲透，不急着讲技术细节。需要明确预算、数据授权、算力资源和阶段成果。");
}

function slide3() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "为什么现在需要这个项目", "Strategic problem");
  const left = [
    ["系统复杂", "一条控制链路跨传感器、执行机构、状态门限、保护逻辑，人工审查容易漏条件。"],
    ["专家瓶颈", "关键诊断依赖少数专家经验，问题复现和传承成本高。"],
    ["证据分散", "文档、仿真、测试、评审、故障记录分散，难形成可复用资产。"],
    ["AI不可裸用", "安全关键系统不能让概率模型直接给出真值判断。"],
  ];
  left.forEach((it, idx) => {
    const y = 162 + idx * 102;
    addText(slide, it[0], 94, y, 120, 26, { fontSize: 22, color: idx === 3 ? C.amber : C.teal2, bold: true });
    addText(slide, it[1], 230, y - 2, 420, 46, { fontSize: 17, color: C.white, autoFit: "shrinkText" });
    addShape(slide, "rect", 90, y + 54, 530, 1, { fill: "#1D3E46" });
  });
  card(slide, 724, 154, 410, 358, { fill: "#0C1B20" });
  addText(slide, "立项窗口", 758, 190, 120, 28, { fontSize: 20, color: C.green, bold: true });
  addText(slide, "把“单点演示样机”升级为“企业级验证能力”，越早建设，越早沉淀跨系统控制逻辑资产。", 758, 232, 314, 86, {
    fontSize: 27,
    color: C.white,
    bold: true,
    autoFit: "shrinkText",
  });
  addShape(slide, "rect", 758, 344, 316, 1, { fill: C.line });
  addText(slide, "核心判断", 758, 366, 120, 24, { fontSize: 16, color: C.teal2, bold: true });
  addText(slide, "本项目的价值不在“炫技”，而在把验证过程标准化、证据化、可审计化。", 758, 400, 310, 52, {
    fontSize: 18,
    color: C.muted,
    autoFit: "shrinkText",
  });
  addFooter(slide, 3);
  addSpeakerNotes(slide, "这一页强调行业痛点：复杂、专家瓶颈、证据分散、AI不能直接做安全判断。我们的解决方向是把真值、仿真、诊断和审计变成企业能力。");
}

function slide4() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "项目定位：做验证工作台，不做飞控替代", "Positioning");
  const noItems = ["不接管飞机控制命令", "不让AI决定控制逻辑真值", "不替代现有PLM/MBSE工具链", "不在首期训练基础大模型"];
  const yesItems = ["把规范文档转成可执行验证对象", "用确定性真值引擎跑仿真与故障注入", "自动生成诊断证据与审计包", "逐步沉淀跨系统知识资产"];
  card(slide, 86, 158, 494, 392, { fill: "#171D21", line: { style: "solid", fill: C.red, width: 1.2 } });
  addText(slide, "边界", 118, 190, 120, 30, { fontSize: 24, color: C.red, bold: true });
  noItems.forEach((t, i) => {
    addShape(slide, "rect", 122, 246 + i * 58, 16, 3, { fill: C.red });
    addText(slide, t, 156, 232 + i * 58, 344, 28, { fontSize: 20, color: C.white });
  });
  card(slide, 646, 158, 494, 392, { fill: "#0E272A", line: { style: "solid", fill: C.green, width: 1.2 } });
  addText(slide, "建设内容", 680, 190, 150, 30, { fontSize: 24, color: C.green, bold: true });
  yesItems.forEach((t, i) => {
    addShape(slide, "ellipse", 684, 236 + i * 58, 14, 14, { fill: C.green });
    addText(slide, t, 718, 228 + i * 58, 360, 30, { fontSize: 20, color: C.white, autoFit: "shrinkText" });
  });
  card(slide, 184, 588, 864, 46, { fill: "#0A171C", line: { style: "solid", fill: C.teal, width: 1 } });
  addText(slide, "一句话定位：安全关键控制逻辑的“验证、诊断、证据、复用”工作台。", 216, 600, 800, 22, {
    fontSize: 21,
    color: C.teal2,
    bold: true,
    align: "center",
  });
  addFooter(slide, 4);
  addSpeakerNotes(slide, "这里主动说明安全边界：不接管控制，不让AI做真值，不替代现有系统。本项目做验证和审计层。");
}

function slide5() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "项目工作流架构：从规范到验证证据闭环", "Workflow architecture");
  const steps = [
    ["资料输入", "规范文档\n故障记录\n试验流程"],
    ["规格澄清", "节点/门限\n歧义确认\n版本冻结"],
    ["系统适配", "真值接口\n硬件映射\n元数据"],
    ["时间线仿真", "指令/状态表\n故障注入\n批量回放"],
    ["诊断与知识", "根因链路\n修复建议\n知识沉淀"],
    ["审计归档", "报告包\n哈希/版本\n可复现证据"],
  ];
  steps.forEach((s, i) => {
    const x = 74 + i * 188;
    card(slide, x, 238, 150, 150, { fill: i % 2 === 0 ? "#10252B" : "#132D31" });
    addText(slide, `${i + 1}`, x + 18, 258, 28, 30, { fontSize: 22, color: i < 3 ? C.teal2 : C.amber, bold: true });
    addText(slide, s[0], x + 50, 260, 82, 26, { fontSize: 20, color: C.white, bold: true, autoFit: "shrinkText" });
    addText(slide, s[1], x + 20, 310, 110, 60, { fontSize: 16, color: C.muted, align: "center", autoFit: "shrinkText" });
    if (i < steps.length - 1) {
      addShape(slide, "rightArrow", x + 152, 294, 42, 38, { fill: i < 2 ? C.teal : C.amber });
    }
  });
  const lanes = [
    ["工程真值层", "确定性计算，所有关键判断可复现"],
    ["仿真验证层", "把场景、故障、批量回放变成证据"],
    ["知识审计层", "沉淀经验，形成报告、追溯和复用"],
  ];
  lanes.forEach((l, i) => {
    const y = 464 + i * 54;
    addText(slide, l[0], 154, y, 140, 24, { fontSize: 17, color: [C.teal2, C.amber, C.green][i], bold: true });
    addShape(slide, "rect", 304, y + 11, 610, 2, { fill: [C.teal2, C.amber, C.green][i] });
    addText(slide, l[1], 936, y, 250, 24, { fontSize: 16, color: C.muted });
  });
  addFooter(slide, 5);
  addSpeakerNotes(slide, "这一页是整套工作流架构，不展开代码。重点展示资料进入、规格澄清、适配、仿真、诊断、归档的闭环。");
}

async function slide6() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "真实工作台界面总览", "Current workbench surfaces");
  await imagePlate(slide, liveScreen("01_surface_index"), 72, 148, 332, 190, { label: "统一入口" });
  await imagePlate(slide, liveScreen("02_fantui_workstation"), 424, 148, 332, 190, { label: "反推逻辑工作台" });
  await imagePlate(slide, liveScreen("03_c919_etras_workstation"), 776, 148, 332, 190, { label: "C919 E-TRAS 工作台" });
  await imagePlate(slide, liveScreen("04_timeline_simulator"), 72, 372, 332, 190, { label: "全流程时间线仿真" });
  await imagePlate(slide, liveScreen("07_c919_circuit"), 424, 372, 332, 190, { label: "E-TRAS 电路拓扑" });
  await imagePlate(slide, liveScreen("08_c919_mfd_panel"), 776, 372, 332, 190, { label: "C919 MFD 仿真面板" });
  card(slide, 1130, 148, 70, 414, { fill: "#0A171C", line: { style: "solid", fill: C.teal, width: 1 } });
  addText(slide, "已形成\n多界面\n工作台", 1143, 206, 44, 154, {
    fontSize: 23,
    color: C.teal2,
    bold: true,
    align: "center",
    autoFit: "shrinkText",
  });
  addText(slide, "这些画面来自当前本地服务实时截屏。", 80, 590, 620, 20, { fontSize: 12, color: C.dim });
  addFooter(slide, 6);
  addSpeakerNotes(slide, "这一页回应可视化不足的问题：展示当前已有的真实工作台界面，包括入口、两类工作台、时间线仿真、电路拓扑和MFD面板。");
}

async function slide7Screens() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "核心工作台：两条控制逻辑链路并行展示", "Workbench screenshots");
  await imagePlate(slide, liveScreen("02_fantui_workstation"), 72, 154, 530, 338, {
    label: "FANTUI 反推逻辑工作台",
  });
  await imagePlate(slide, liveScreen("03_c919_etras_workstation"), 650, 154, 530, 338, {
    label: "C919 E-TRAS 逻辑工作台",
  });
  const notes = [
    ["同一类操作", "拉杆、条件、故障注入、链路高亮"],
    ["不同系统真值", "反推链与C919 E-TRAS通过适配器接入"],
    ["正式展示面", "可直接用于项目介绍和阶段验收演示"],
  ];
  notes.forEach((n, i) => {
    const x = 110 + i * 360;
    card(slide, x, 532, 306, 58, { fill: "#0E2026" });
    addText(slide, n[0], x + 18, 544, 110, 18, { fontSize: 15, color: [C.teal2, C.amber, C.green][i], bold: true });
    addText(slide, n[1], x + 18, 566, 250, 18, { fontSize: 13, color: C.muted, autoFit: "shrinkText" });
  });
  addFooter(slide, 7);
  addSpeakerNotes(slide, "这一页展示两个真实工作台。重点是同一类交互形态可以服务不同控制系统，说明项目不是单页演示。");
}

async function slide8Screens() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "仿真与证据界面：时间线、拓扑、面板联动", "Simulation and evidence");
  await imagePlate(slide, liveScreen("04_timeline_simulator"), 72, 150, 540, 262, {
    label: "全流程时间线仿真",
  });
  await imagePlate(slide, liveScreen("07_c919_circuit"), 638, 150, 540, 262, {
    label: "C919 E-TRAS 电路拓扑",
  });
  await imagePlate(slide, liveScreen("08_c919_mfd_panel"), 72, 444, 540, 122, {
    label: "有状态MFD仿真面板",
  });
  await imagePlate(slide, liveScreen("06_fantui_circuit"), 638, 444, 540, 122, {
    label: "FANTUI 反推电路拓扑",
  });
  card(slide, 160, 588, 900, 42, { fill: "#101F25", line: { style: "solid", fill: C.teal, width: 1.2 } });
  addText(slide, "展示面不只是一张静态图：可切换系统、可跑时间线、可看拓扑、可进入有状态仿真。", 196, 600, 828, 18, {
    fontSize: 18,
    color: C.teal2,
    bold: true,
    align: "center",
    autoFit: "shrinkText",
  });
  addFooter(slide, 8);
  addSpeakerNotes(slide, "这一页强调视觉展示面和工程证据面结合。时间线、拓扑图、MFD面板都是真实页面截图。");
}

function slide7() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "技术路线：三层解耦，避免“AI黑箱”", "Technical route");
  const layers = [
    ["01", "确定性真值层", "控制逻辑、门限、状态转移由可测试代码/规格承载；相同输入得到相同输出。", C.green],
    ["02", "适配与仿真层", "不同子系统通过 adapter 接入，统一进入时间线仿真、故障注入、批量回放。", C.teal2],
    ["03", "AI辅助与知识层", "AI用于解释、检索、报告生成和专家知识沉淀；不改写真值结论。", C.amber],
  ];
  layers.forEach((l, i) => {
    const y = 166 + i * 132;
    card(slide, 110, y, 910, 96, { fill: i === 0 ? "#122D27" : i === 1 ? "#0F2630" : "#2B2516", line: { style: "solid", fill: l[3], width: 1.4 } });
    addText(slide, l[0], 142, y + 24, 60, 40, { fontSize: 30, color: l[3], bold: true });
    addText(slide, l[1], 230, y + 22, 210, 30, { fontSize: 24, color: C.white, bold: true });
    addText(slide, l[2], 474, y + 19, 492, 42, { fontSize: 18, color: C.muted, autoFit: "shrinkText" });
  });
  addShape(slide, "rect", 1054, 170, 4, 352, { fill: C.line2 });
  addText(slide, "核心原则", 1084, 220, 90, 24, { fontSize: 18, color: C.teal2, bold: true });
  addText(slide, "先有真值\n再有解释\n最后归档", 1084, 266, 116, 118, { fontSize: 26, color: C.white, bold: true, autoFit: "shrinkText" });
  addText(slide, "这让系统可审计、可降级、可国产化。", 1084, 408, 118, 52, { fontSize: 15, color: C.muted, autoFit: "shrinkText" });
  addFooter(slide, 9);
  addSpeakerNotes(slide, "这一页回应AI风险：AI不是裁判，真值层才是裁判。AI只做解释、检索和报告。");
}

function slide8() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "18个月开发路线图：每3–6个月有可见成果", "Roadmap");
  const phases = [
    ["0–3个月", "立项启动与试点准备", "完成项目章程、数据清单、首个试点系统选择、样机演示基线。"],
    ["3–6个月", "真实子系统PoC", "把甲方一个真实子系统跑通“文档→规格→仿真→诊断”。"],
    ["6–12个月", "生产前硬化", "建设Staging环境、安全基线、批量验证、审计报告模板。"],
    ["12–18个月", "首批生产验证", "接入3–5个子系统，形成可复现验证报告和季度审计包。"],
  ];
  addShape(slide, "rect", 126, 298, 990, 4, { fill: C.line2 });
  phases.forEach((p, i) => {
    const x = 112 + i * 252;
    addShape(slide, "ellipse", x + 52, 270, 60, 60, { fill: i === 0 ? C.teal : i === 1 ? C.green : i === 2 ? C.amber : C.panel3, line: { style: "solid", fill: C.white, width: 1 } });
    addText(slide, `${i + 1}`, x + 66, 283, 32, 30, { fontSize: 24, color: i < 3 ? C.ink : C.white, bold: true, align: "center" });
    card(slide, x, 352, 190, 188, { fill: "#0D2026" });
    addText(slide, p[0], x + 18, 374, 154, 22, { fontSize: 17, color: C.teal2, bold: true, align: "center" });
    addText(slide, p[1], x + 18, 412, 154, 38, { fontSize: 20, color: C.white, bold: true, align: "center", autoFit: "shrinkText" });
    addText(slide, p[2], x + 18, 470, 154, 46, { fontSize: 14, color: C.muted, align: "center", autoFit: "shrinkText" });
  });
  addText(slide, "T0", 104, 240, 42, 20, { fontSize: 14, color: C.dim });
  addText(slide, "T0+18M", 1078, 240, 76, 20, { fontSize: 14, color: C.dim, align: "right" });
  addFooter(slide, 10);
  addSpeakerNotes(slide, "路线图要讲成阶段成果，不讲内部任务编号。重点是每3到6个月都能看到东西，审批风险可控。");
}

function slide9() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "每个阶段可验收成果", "Stage outcomes");
  const rows = [
    ["T0+30天", "立项包+样机演示", "项目章程、数据目录、试点系统清单、当前C919样机演示。", "决定是否进入PoC"],
    ["T0+3个月", "试点系统首版", "真实文档完成规格澄清；控制链路可在工作台上被演示。", "决定是否扩充数据"],
    ["T0+6个月", "端到端PoC", "文档→仿真→故障注入→诊断→报告闭环跑通。", "决定是否进Staging"],
    ["T0+12个月", "生产前验证", "安全基线、批量验证、审计追溯、运维监控可验收。", "决定是否进产线"],
    ["T0+18个月", "首批生产验证", "3–5个子系统验证报告、季度审计包、复现脚本。", "决定平台化扩展"],
  ];
  const x = 82;
  const y = 152;
  const col = [142, 190, 500, 220];
  const headers = ["时间点", "展示成果", "可验收内容", "决策动作"];
  let cx = x;
  headers.forEach((h, i) => {
    addShape(slide, "rect", cx, y, col[i], 46, { fill: i === 2 ? "#17313A" : "#10232B", line: { style: "solid", fill: C.line, width: 1 } });
    addText(slide, h, cx + 10, y + 13, col[i] - 20, 18, { fontSize: 15, color: C.teal2, bold: true, align: "center" });
    cx += col[i];
  });
  rows.forEach((r, ri) => {
    cx = x;
    const yy = y + 46 + ri * 70;
    r.forEach((cell, ci) => {
      addShape(slide, "rect", cx, yy, col[ci], 70, {
        fill: ri % 2 === 0 ? "#0C1B21" : "#0F2027",
        line: { style: "solid", fill: "#1C3A42", width: 1 },
      });
      addText(slide, cell, cx + 12, yy + 12, col[ci] - 24, 42, {
        fontSize: ci === 0 ? 15 : ci === 1 ? 16 : 14,
        color: ci === 0 ? C.amber : C.white,
        bold: ci < 2,
        align: ci === 0 ? "center" : "left",
        autoFit: "shrinkText",
      });
      cx += col[ci];
    });
  });
  addFooter(slide, 11);
  addSpeakerNotes(slide, "这页回答阶段性验收问题：按30天、3个月、6个月、12个月、18个月说明每个阶段的可见成果。");
}

function slide10() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "经费测算：推荐采用“生产验证型”预算", "Budget");
  const tiers = [
    ["精简试点", "800–1200万", "6个月", "1–2个子系统\n2–4张GPU\n适合概念验证"],
    ["推荐方案", "1800–2600万", "18个月", "3–5个子系统\n4–8张GPU\n形成生产验证能力"],
    ["平台化扩展", "3500–5000万", "24个月+", "5–8个子系统\n8–16张GPU\n双中心容灾"],
  ];
  tiers.forEach((t, i) => {
    const x = 86 + i * 372;
    card(slide, x, 152, 326, 220, {
      fill: i === 1 ? "#2D2817" : "#0D2026",
      line: { style: "solid", fill: i === 1 ? C.amber : C.line, width: i === 1 ? 2 : 1 },
    });
    addText(slide, t[0], x + 24, 178, 140, 28, { fontSize: 22, color: i === 1 ? C.amber : C.teal2, bold: true });
    addText(slide, t[1], x + 24, 226, 260, 42, { fontSize: 32, color: C.white, bold: true, autoFit: "shrinkText" });
    addText(slide, t[2], x + 24, 284, 120, 24, { fontSize: 18, color: C.muted, bold: true });
    addText(slide, t[3], x + 24, 318, 260, 44, { fontSize: 15, color: C.muted, autoFit: "shrinkText" });
    if (i === 1) chip(slide, "建议申报", x + 200, 180, 92, C.amber);
  });
  card(slide, 118, 430, 1010, 132, { fill: "#0E1E23" });
  addText(slide, "推荐中值：2200万元（18个月）", 152, 454, 430, 30, { fontSize: 25, color: C.amber, bold: true });
  const alloc = [
    ["研发与工程化", "850万"],
    ["领域专家/数据治理", "300万"],
    ["算力与环境", "450万"],
    ["安全合规与测评", "250万"],
    ["试点集成与培训", "250万"],
    ["预备金", "100万"],
  ];
  alloc.forEach((a, i) => {
    const x = 152 + (i % 3) * 310;
    const y = 500 + Math.floor(i / 3) * 34;
    addShape(slide, "ellipse", x, y + 7, 8, 8, { fill: i === 2 ? C.amber : C.teal2 });
    addText(slide, `${a[0]}：${a[1]}`, x + 18, y, 260, 22, { fontSize: 16, color: C.white, autoFit: "shrinkText" });
  });
  addText(slide, "说明：金额为立项测算口径，硬件采购、云/私有化资源、测评费用以正式询价和集团采购规则为准。", 152, 590, 858, 22, {
    fontSize: 12,
    color: C.dim,
  });
  addFooter(slide, 12);
  addSpeakerNotes(slide, "这里给三档，推荐中间档。重点说预算不是一次性全花，可以随阶段拨付。算力费用不按大模型训练集群报，避免审批压力。");
}

function slide11() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "数据中心与算力：首期不新建，按资源池分阶段扩容", "Compute plan");
  card(slide, 92, 152, 462, 376, { fill: "#0D2026" });
  addText(slide, "数据中心数量建议", 126, 184, 210, 28, { fontSize: 24, color: C.teal2, bold: true });
  const dc = [
    ["立项/PoC期", "1个既有数据中心资源池", "开发、样机、试点数据处理"],
    ["生产验证期", "1主 + 1灾备资源预留", "Staging、审计归档、演示不中断"],
    ["平台化期", "双中心主动/备用", "跨单位复用、长期审计留存"],
  ];
  dc.forEach((d, i) => {
    const y = 246 + i * 86;
    addText(slide, d[0], 128, y, 112, 22, { fontSize: 17, color: i === 0 ? C.green : i === 1 ? C.amber : C.teal2, bold: true });
    addText(slide, d[1], 256, y - 2, 250, 24, { fontSize: 19, color: C.white, bold: true, autoFit: "shrinkText" });
    addText(slide, d[2], 256, y + 30, 250, 22, { fontSize: 14, color: C.muted, autoFit: "shrinkText" });
  });
  card(slide, 610, 152, 532, 376, { fill: "#111F24" });
  addText(slide, "资源规格建议", 644, 184, 180, 28, { fontSize: 24, color: C.amber, bold: true });
  const specs = [
    ["开发/PoC", "2–4张48GB级GPU", "32–64 CPU核 · 256–512GB内存 · 20–50TB存储"],
    ["生产验证", "4–8张数据中心GPU", "128–256 CPU核 · 1–2TB内存 · 100TB+存储"],
    ["平台扩展", "8–16张GPU", "双中心容灾 · 300TB+对象存储 · 统一审计日志"],
  ];
  specs.forEach((s, i) => {
    const y = 244 + i * 86;
    addShape(slide, "rect", 646, y + 6, 16, 16, { fill: i === 1 ? C.amber : C.teal2 });
    addText(slide, s[0], 678, y, 108, 22, { fontSize: 17, color: C.white, bold: true });
    addText(slide, s[1], 800, y - 2, 240, 24, { fontSize: 19, color: i === 1 ? C.amber : C.teal2, bold: true });
    addText(slide, s[2], 678, y + 30, 392, 22, { fontSize: 14, color: C.muted, autoFit: "shrinkText" });
  });
  addText(slide, "依据公开硬件规格测算：L40S为48GB/350W级数据中心GPU；更高端H200为141GB HBM3e级GPU。实际选型以国产化、采购渠道和安全要求为准。", 122, 574, 1000, 24, {
    fontSize: 12,
    color: C.dim,
    autoFit: "shrinkText",
  });
  addFooter(slide, 13);
  addSpeakerNotes(slide, "这一页给明确答案：首期不新建数据中心。用一个既有数据中心资源池即可；生产验证期预留一主一备；平台化才考虑双中心。GPU分阶段上架，避免一次性重资产。");
}

function slide12() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "实施方式：六个交付包，阶段验收", "Delivery model");
  const packs = [
    ["需求与数据治理", "资料清单、脱敏边界、试点系统选择"],
    ["系统适配", "控制逻辑节点、硬件映射、接口元数据"],
    ["仿真与诊断", "时间线、故障注入、批量回放、根因链路"],
    ["展示工作台", "正式演示界面、工程操作界面、报告输出"],
    ["安全与审计", "权限、日志、版本、复现、第三方测评"],
    ["部署运维", "数据中心部署、备份、监控、培训"],
  ];
  packs.forEach((p, i) => {
    const x = 88 + (i % 3) * 368;
    const y = 168 + Math.floor(i / 3) * 178;
    card(slide, x, y, 312, 128, { fill: "#0E2127" });
    addText(slide, `0${i + 1}`, x + 20, y + 18, 42, 28, { fontSize: 22, color: i % 2 ? C.amber : C.teal2, bold: true });
    addText(slide, p[0], x + 72, y + 18, 194, 26, { fontSize: 21, color: C.white, bold: true, autoFit: "shrinkText" });
    addText(slide, p[1], x + 28, y + 66, 244, 38, { fontSize: 15, color: C.muted, autoFit: "shrinkText" });
  });
  card(slide, 188, 558, 860, 50, { fill: "#101F25", line: { style: "solid", fill: C.green, width: 1.2 } });
  addText(slide, "验收机制：每个阶段输出可演示界面 + 可复现测试 + 可归档报告，避免“只交文档”。", 222, 572, 792, 20, {
    fontSize: 19,
    color: C.green,
    bold: true,
    align: "center",
    autoFit: "shrinkText",
  });
  addFooter(slide, 14);
  addSpeakerNotes(slide, "避免讲复杂组织架构。讲六个交付包和阶段验收。每阶段都要有可演示、可测试、可归档的东西。");
}

function slide13() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "风险控制：用工程边界降低不确定性", "Risk control");
  const risks = [
    ["AI幻觉风险", "真值在AI上游，AI只做解释和报告，不直接决定控制逻辑。", C.amber],
    ["数据安全风险", "试点数据在内网/私有化环境处理，敏感资料按最小化授权。", C.green],
    ["范围失控风险", "先1个子系统PoC，再扩展到3–5个；超过范围进入二期评估。", C.teal2],
    ["算力浪费风险", "分阶段采购/分阶段上架，先资源池，后生产验证集群。", C.amber],
    ["审计不可追溯", "每次验证绑定输入、版本、测试、报告、哈希和责任边界。", C.green],
  ];
  risks.forEach((r, i) => {
    const y = 154 + i * 82;
    card(slide, 108, y, 1000, 58, { fill: i % 2 === 0 ? "#0B1C22" : "#10232B" });
    addShape(slide, "ellipse", 136, y + 19, 20, 20, { fill: r[2] });
    addText(slide, r[0], 178, y + 16, 170, 24, { fontSize: 20, color: C.white, bold: true });
    addText(slide, r[1], 390, y + 15, 638, 24, { fontSize: 18, color: C.muted, autoFit: "shrinkText" });
  });
  addFooter(slide, 15);
  addSpeakerNotes(slide, "风险页要讲得稳：AI、数据、范围、算力、审计都有对应控制。不要承诺零风险，承诺风险被工程化管理。");
}

function slide14() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "预期价值：形成可复用的工业软件能力", "Expected value");
  const values = [
    ["专家经验产品化", "把少数专家的诊断路径沉淀为可演示、可复现、可培训的工作台。"],
    ["验证过程标准化", "把文档、仿真、故障注入、诊断报告、审计归档统一成闭环。"],
    ["跨系统复用", "同一套适配器边界可逐步承载反推、起落架、引气等控制系统。"],
    ["国产可控路线", "私有化部署、本地模型辅助解释、数据中心资源可由集团掌控。"],
  ];
  values.forEach((v, i) => {
    const x = 98 + (i % 2) * 536;
    const y = 176 + Math.floor(i / 2) * 170;
    card(slide, x, y, 468, 126, { fill: i === 0 ? "#10272C" : "#0D2026" });
    addText(slide, v[0], x + 28, y + 24, 240, 28, { fontSize: 24, color: i % 2 ? C.amber : C.teal2, bold: true, autoFit: "shrinkText" });
    addText(slide, v[1], x + 28, y + 70, 380, 34, { fontSize: 16, color: C.muted, autoFit: "shrinkText" });
  });
  card(slide, 168, 548, 890, 48, { fill: "#1B2718", line: { style: "solid", fill: C.green, width: 1.2 } });
  addText(slide, "阶段性目标：把“小时级人工分析”逐步压缩为“分钟级可复现验证”，最终以试点实测指标确认。", 202, 562, 822, 20, {
    fontSize: 18,
    color: C.green,
    bold: true,
    align: "center",
    autoFit: "shrinkText",
  });
  addFooter(slide, 16);
  addSpeakerNotes(slide, "价值页强调产品化、标准化、复用、国产可控。注意用'目标'而不是绝对承诺，避免过度承诺。");
}

function slide15() {
  const slide = presentation.slides.add();
  bg(slide);
  addTitle(slide, "立项请求：批准进入18个月生产验证建设", "Approval ask");
  card(slide, 96, 156, 1038, 334, { fill: "#0D2026", line: { style: "solid", fill: C.teal, width: 1.4 } });
  addText(slide, "建议批准", 134, 190, 120, 30, { fontSize: 24, color: C.teal2, bold: true });
  const asks = [
    "按1800–2600万元区间启动生产验证型立项，建议中值2200万元。",
    "授权1个真实子系统作为首个PoC，T0+6个月完成端到端演示。",
    "提供既有数据中心资源池：首期2–4张GPU，生产验证期扩至4–8张GPU。",
    "指定数据、业务、安全、运维接口人，保障资料授权和内网部署。",
  ];
  asks.forEach((a, i) => bullet(slide, a, 148, 246 + i * 52, 860, i === 0 ? C.amber : C.teal2));
  card(slide, 166, 532, 900, 60, { fill: "#2D2817", line: { style: "solid", fill: C.amber, width: 1.4 } });
  addText(slide, "通过立项后30天内交付：项目章程、数据清单、试点方案、当前样机正式演示版。", 204, 550, 824, 24, {
    fontSize: 22,
    color: C.amber,
    bold: true,
    align: "center",
    autoFit: "shrinkText",
  });
  addFooter(slide, 17);
  addSpeakerNotes(slide, "最后直接收口到请求：预算、试点系统、数据中心资源、接口人。不要在最后又回到技术细节。");
}

slide1();
slide2();
slide3();
slide4();
slide5();
await slide6();
await slide7Screens();
await slide8Screens();
slide7();
slide8();
slide9();
slide10();
slide11();
slide12();
slide13();
slide14();
slide15();

const renderedIndexes = Array.from({ length: presentation.slides.count }, (_, idx) => idx);
for (const idx of renderedIndexes) {
  const blob = await presentation.export({
    slide: presentation.slides.getItem(idx),
    format: "png",
    scale: 1,
  });
  await saveBlobLike(blob, path.resolve(scratchDir, `preview_${String(idx + 1).padStart(2, "0")}.png`));
}

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(finalPath);

const inspect = {
  output: finalPath,
  slide_count: presentation.slides.count,
  rendered_previews: renderedIndexes.map((idx) => idx + 1),
  editable_text_note: "Titles, body text, tables, metrics, timelines, and labels are authored as editable PowerPoint text/shapes; only the current UI screenshot is raster.",
};
await fs.writeFile(path.resolve(outDir, "verification.json"), JSON.stringify(inspect, null, 2));

console.log(JSON.stringify(inspect, null, 2));
