import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const inputPptx = "/Users/Zhuanz/Downloads/AI赋能民机控制逻辑智能分析与验证平台_一期_立项汇报.pptx";
const outputDir = "/Users/Zhuanz/Downloads/fantui_logicmvp_ppt_augmented";
const outputPptx = path.join(outputDir, "AI赋能民机控制逻辑智能分析与验证平台_一期_立项汇报_功能Demo增强版.pptx");
const scratchDir = "/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/tmp/slides/fantui_logicmvp_demo_pages";
const previewDir = path.join(scratchDir, "preview", "augmented");
const screensDir = path.join(scratchDir, "screens");
const inspectPath = path.join(scratchDir, "work", "editable_inspect.json");

const W = 1280;
const H = 720;
const C = {
  navy: "#112A49",
  navy2: "#143F72",
  blue: "#2857E5",
  teal: "#0E9B8D",
  cyan: "#06B6D4",
  orange: "#F05A1A",
  yellow: "#FFF4B8",
  paleBlue: "#EEF4FF",
  paleTeal: "#EEFDF9",
  paleOrange: "#FFF2EA",
  paleYellow: "#FFF8D4",
  grayText: "#64748B",
  body: "#334155",
  panel: "#F8FAFC",
  line: "#CBD5E1",
  dark: "#061321",
};
const FONT = {
  title: "Microsoft YaHei",
  body: "Microsoft YaHei",
  mono: "Consolas",
};

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function saveAny(blobLike, target) {
  if (typeof blobLike?.save === "function") {
    await blobLike.save(target);
  } else if (blobLike instanceof Uint8Array || Buffer.isBuffer(blobLike)) {
    await fs.writeFile(target, blobLike);
  } else if (blobLike?.bytes instanceof Uint8Array) {
    await fs.writeFile(target, blobLike.bytes);
  } else if (typeof blobLike?.arrayBuffer === "function") {
    await fs.writeFile(target, Buffer.from(await blobLike.arrayBuffer()));
  } else {
    throw new TypeError(`Unsupported payload: ${blobLike?.constructor?.name || typeof blobLike}`);
  }
}

const inspect = [];

function addShape(slide, { left, top, width, height, fill = "#FFFFFF00", lineFill = "#FFFFFF00", lineWidth = 0, radius = false }) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
    ...(radius ? { adjustmentList: [{ name: "adj", formula: "val 12000" }] } : {}),
  });
}

function addText(slide, text, box, opts = {}) {
  const shape = addShape(slide, {
    ...box,
    fill: opts.fill || "#FFFFFF00",
    lineFill: opts.lineFill || "#FFFFFF00",
    lineWidth: opts.lineWidth || 0,
    radius: opts.radius || false,
  });
  shape.text = text;
  shape.text.typeface = opts.typeface || FONT.body;
  shape.text.fontSize = opts.fontSize || 20;
  shape.text.color = opts.color || C.body;
  shape.text.bold = Boolean(opts.bold);
  shape.text.alignment = opts.alignment || "left";
  shape.text.verticalAlignment = opts.verticalAlignment || "top";
  shape.text.insets = opts.insets || { left: 10, right: 10, top: 6, bottom: 6 };
  if (opts.autoFit) shape.text.autoFit = opts.autoFit;
  inspect.push({
    kind: "textbox",
    slide: opts.slideNo || null,
    role: opts.role || "body",
    text,
    textChars: text.length,
    textLines: String(text).split(/\n/).length,
    bbox: box,
  });
  return shape;
}

function addHeader(slide, title, subtitle, slideNo) {
  addShape(slide, { left: 0, top: 0, width: W, height: 10, fill: C.blue });
  addText(slide, title, { left: 58, top: 38, width: 1065, height: 44 }, {
    fontSize: 30,
    bold: true,
    color: C.navy,
    typeface: FONT.title,
    slideNo,
    role: "title",
  });
  addText(slide, subtitle, { left: 58, top: 88, width: 1040, height: 30 }, {
    fontSize: 14,
    color: C.grayText,
    slideNo,
    role: "subtitle",
  });
  addText(slide, "建议汇报时长：12-15分钟｜新增 Demo 页建议“先看画面、再讲闭环、最后落到资源与阶段成果”", {
    left: 805,
    top: 682,
    width: 405,
    height: 24,
  }, {
    fontSize: 10,
    color: C.grayText,
    slideNo,
    role: "footer",
  });
}

function addPill(slide, label, box, color, slideNo) {
  addText(slide, label, box, {
    fill: color,
    lineFill: color,
    lineWidth: 1,
    radius: true,
    fontSize: 15,
    bold: true,
    color: "#FFFFFF",
    alignment: "center",
    verticalAlignment: "middle",
    slideNo,
    role: "pill",
  });
}

function addCard(slide, { title, body, box, color, fill, slideNo, role = "card" }) {
  addShape(slide, {
    ...box,
    fill,
    lineFill: color,
    lineWidth: 1.8,
    radius: true,
  });
  addPill(slide, title, { left: box.left + 18, top: box.top + 16, width: 132, height: 38 }, color, slideNo);
  addText(slide, body, { left: box.left + 170, top: box.top + 18, width: box.width - 195, height: box.height - 28 }, {
    fontSize: 16,
    color: C.body,
    slideNo,
    role,
    autoFit: "shrinkText",
  });
}

async function addScreenshot(slide, imageName, box, alt) {
  const frame = addShape(slide, {
    left: box.left - 8,
    top: box.top - 8,
    width: box.width + 16,
    height: box.height + 16,
    fill: "#FFFFFF",
    lineFill: C.line,
    lineWidth: 1,
    radius: true,
  });
  const shadow = addShape(slide, {
    left: box.left - 4,
    top: box.top - 2,
    width: box.width + 16,
    height: box.height + 18,
    fill: "#00000010",
    lineFill: "#FFFFFF00",
    lineWidth: 0,
    radius: true,
  });
  shadow.position = { left: box.left - 4, top: box.top - 2, width: box.width + 16, height: box.height + 18 };
  const image = slide.images.add({
    blob: await readImageBlob(path.join(screensDir, imageName)),
    fit: "cover",
    alt,
  });
  image.position = box;
  image.geometry = "roundRect";
  return { frame, image };
}

function addMetric(slide, value, label, box, color, slideNo) {
  addShape(slide, { ...box, fill: "#FFFFFF", lineFill: color, lineWidth: 1.5, radius: true });
  addText(slide, value, { left: box.left + 10, top: box.top + 10, width: box.width - 20, height: 34 }, {
    fontSize: 27,
    bold: true,
    color,
    alignment: "center",
    verticalAlignment: "middle",
    slideNo,
    role: "metric",
  });
  addText(slide, label, { left: box.left + 12, top: box.top + 48, width: box.width - 24, height: 42 }, {
    fontSize: 12,
    color: C.body,
    alignment: "center",
    verticalAlignment: "top",
    slideNo,
    role: "metric_label",
    autoFit: "shrinkText",
  });
}

async function slideDemoOverview(slide, slideNo) {
  slide.background.fill = "#FFFFFF";
  addHeader(slide, "功能 Demo 总览：一期样板已经能“看见、操作、复验”", "把原方案中的平台能力落到当前可演示页面：不是概念图，而是可交互样板与验证证据", slideNo);

  const stages = [
    ["01", "逻辑演示舱", "拉动反推杆，实时看到 TRA / SW1 / SW2 / L1-L4 / THR_LOCK 状态。", C.blue, C.paleBlue],
    ["02", "C919 工作台", "C919 E-TRAS 通过适配器接入，证明平台不是单系统硬编码。", C.teal, C.paleTeal],
    ["03", "全流程仿真", "用“时间-指令/状态”脚本驱动故障、断言、节点时间线。", C.orange, C.paleOrange],
    ["04", "证据包闭环", "接入 → 回放 → 诊断 → 知识 → 归档，形成可审查资产。", C.navy, C.panel],
  ];

  stages.forEach(([num, title, body, color, fill], idx) => {
    const x = 70 + idx * 292;
    addShape(slide, { left: x, top: 166, width: 250, height: 250, fill, lineFill: color, lineWidth: 2, radius: true });
    addText(slide, num, { left: x + 22, top: 184, width: 58, height: 48 }, {
      fill: color,
      lineFill: color,
      radius: true,
      fontSize: 23,
      bold: true,
      color: "#FFFFFF",
      alignment: "center",
      verticalAlignment: "middle",
      slideNo,
      role: "stage_no",
    });
    addText(slide, title, { left: x + 92, top: 188, width: 135, height: 36 }, {
      fontSize: 19,
      bold: true,
      color: C.navy,
      slideNo,
      role: "stage_title",
    });
    addText(slide, body, { left: x + 28, top: 250, width: 194, height: 95 }, {
      fontSize: 15,
      color: C.body,
      slideNo,
      role: "stage_body",
      autoFit: "shrinkText",
    });
    addText(slide, idx < stages.length - 1 ? "→" : "✓", { left: x + 94, top: 358, width: 64, height: 38 }, {
      fontSize: 28,
      bold: true,
      color,
      alignment: "center",
      verticalAlignment: "middle",
      slideNo,
      role: "stage_arrow",
    });
  });

  addCard(slide, {
    title: "当前证据",
    body: "仓库状态记录：时间线仿真已交付；FANTUI/C919 双执行器；仿真接口已接入；UI 4 个预设；765 项测试通过；0 个严重问题。",
    box: { left: 92, top: 468, width: 1090, height: 84 },
    color: C.teal,
    fill: C.paleTeal,
    slideNo,
    role: "evidence_card",
  });
  addMetric(slide, "2 套", "FANTUI 反推 + C919 E-TRAS", { left: 115, top: 574, width: 160, height: 84 }, C.blue, slideNo);
  addMetric(slide, "4 个", "Timeline 内置演示预设", { left: 315, top: 574, width: 160, height: 84 }, C.teal, slideNo);
  addMetric(slide, "765", "状态记录测试通过", { left: 515, top: 574, width: 160, height: 84 }, C.orange, slideNo);
  addMetric(slide, "0", "严重 / 失败问题", { left: 715, top: 574, width: 160, height: 84 }, C.navy, slideNo);
  addMetric(slide, "可审查", "输出证据能归档和复验", { left: 915, top: 574, width: 160, height: 84 }, C.teal, slideNo);
}

async function slideFantuiCockpit(slide, slideNo) {
  slide.background.fill = "#FFFFFF";
  addHeader(slide, "功能 Demo 01：反推逻辑演示舱，现场可操作的控制链", "领导看到的是“拉杆动作 → 信号变化 → 逻辑结论”，不是只有技术文档或静态流程图", slideNo);
  await addScreenshot(slide, "demo-fantui-cockpit.png", { left: 58, top: 145, width: 755, height: 425 }, "FANTUI reverse thrust cockpit UI");
  addText(slide, "真实功能画面", { left: 80, top: 592, width: 720, height: 28 }, {
    fontSize: 13,
    color: C.grayText,
    slideNo,
    role: "image_caption",
  });
  addCard(slide, {
    title: "怎么演示",
    body: "拖动 TRA 反推拉杆，切换 VDT 反馈、RA、N1K、地面/发动机/抑制等条件，逻辑链路会同步点亮或阻塞。",
    box: { left: 845, top: 150, width: 350, height: 105 },
    color: C.blue,
    fill: C.paleBlue,
    slideNo,
  });
  addCard(slide, {
    title: "能证明什么",
    body: "控制逻辑不再停留在口头解释：SW1/SW2、L1-L4、VDT90、THR_LOCK 能在同一画面形成可读、可复验的因果链。",
    box: { left: 845, top: 282, width: 350, height: 125 },
    color: C.teal,
    fill: C.paleTeal,
    slideNo,
  });
  addCard(slide, {
    title: "边界清楚",
    body: "Demo/UI 只读取 controller 与 adapter 的输出；简化 plant 只用于演示反馈，不替代真实控制逻辑真值。",
    box: { left: 845, top: 434, width: 350, height: 112 },
    color: C.orange,
    fill: C.paleOrange,
    slideNo,
  });
  addShape(slide, { left: 847, top: 584, width: 350, height: 54, fill: C.yellow, lineFill: "#EAB308", lineWidth: 1, radius: true });
  addText(slide, "一句话讲法：这页把“专家脑中的控制链”变成了领导能现场操作、工程师能复验的演示舱。", {
    left: 860,
    top: 596,
    width: 318,
    height: 38,
  }, {
    fontSize: 14,
    bold: true,
    color: C.navy,
    slideNo,
    role: "talk_track",
    autoFit: "shrinkText",
  });
}

async function slideC919Workstation(slide, slideNo) {
  slide.background.fill = "#FFFFFF";
  addHeader(slide, "功能 Demo 02：C919 E-TRAS 工作台，验证平台可推广", "同一套 workbench 思路接入第二套控制逻辑，说明一期不是只做一个孤立反推页面", slideNo);
  addCard(slide, {
    title: "Adapter 边界",
    body: "C919 E-TRAS 通过显式 adapter 与 frozen_v1 参考引擎接入；新增系统真值不绕开 adapter，不改写 FANTUI controller。",
    box: { left: 65, top: 145, width: 388, height: 112 },
    color: C.blue,
    fill: C.paleBlue,
    slideNo,
  });
  addCard(slide, {
    title: "现场控制",
    body: "页面提供 TRA、N1K、WOW、锁状态、过温故障、定时器等输入，后端返回 truth_evaluation 与 asserted values。",
    box: { left: 65, top: 282, width: 388, height: 116 },
    color: C.teal,
    fill: C.paleTeal,
    slideNo,
  });
  addCard(slide, {
    title: "扩展价值",
    body: "这页支撑二期“多控制逻辑场景扩展”的可信表达：新系统按接口接入，而不是每个场景重做一套规则引擎。",
    box: { left: 65, top: 423, width: 388, height: 120 },
    color: C.orange,
    fill: C.paleOrange,
    slideNo,
  });
  await addScreenshot(slide, "demo-c919-workstation.png", { left: 490, top: 145, width: 700, height: 470 }, "C919 E-TRAS workstation UI");
  addText(slide, "画面重点：左侧输入条件/概率仿真，右侧信号流链路随 adapter 输出实时变色。", {
    left: 506,
    top: 632,
    width: 660,
    height: 26,
  }, {
    fontSize: 13,
    color: C.grayText,
    slideNo,
    role: "image_caption",
  });
}

async function slideTimelineSim(slide, slideNo) {
  slide.background.fill = "#FFFFFF";
  addHeader(slide, "功能 Demo 03：全流程故障率仿真，把测试编制变成脚本驱动", "按“时间-指令/状态”表驱动控制系统，自动输出断言、逻辑时间线和故障阻塞证据", slideNo);
  await addScreenshot(slide, "demo-timeline-sim.png", { left: 52, top: 132, width: 805, height: 455 }, "Timeline simulator UI");
  addText(slide, "示例：SW1 卡死脚本触发 L1 阻塞，断言结果自动 PASS。", {
    left: 72,
    top: 604,
    width: 750,
    height: 28,
  }, {
    fontSize: 13,
    color: C.grayText,
    slideNo,
    role: "image_caption",
  });
  addMetric(slide, "7 类", "状态设置 / 斜坡输入 / 故障 / 断言等", { left: 900, top: 138, width: 205, height: 88 }, C.blue, slideNo);
  addMetric(slide, "4 个", "内置预设：FANTUI 与 C919 各 2 个", { left: 900, top: 245, width: 205, height: 88 }, C.teal, slideNo);
  addMetric(slide, "40+", "Timeline 相关新增测试", { left: 900, top: 352, width: 205, height: 88 }, C.orange, slideNo);
  addShape(slide, { left: 880, top: 478, width: 270, height: 118, fill: C.yellow, lineFill: "#EAB308", lineWidth: 1, radius: true });
  addText(slide, "对立项的说服力\n测试不再只是“工程师手工列举”：可以把飞行阶段、拉杆动作、故障注入、验收断言写成可复跑脚本。", {
    left: 900,
    top: 492,
    width: 230,
    height: 92,
  }, {
    fontSize: 15,
    bold: true,
    color: C.navy,
    slideNo,
    role: "persuasion_note",
    autoFit: "shrinkText",
  });
}

async function slideMonitorEvidence(slide, slideNo) {
  slide.background.fill = "#FFFFFF";
  addHeader(slide, "功能 Demo 04：状态 vs 时间监控，支撑审查时的“过程证据”", "把关键事件、输入、逻辑、电源、传感器和命令统一落到时间轴，方便复盘与审查", slideNo);
  await addScreenshot(slide, "demo-monitor-timeline.png", { left: 58, top: 135, width: 735, height: 462 }, "Reverse thrust monitor timeline UI");
  addText(slide, "当前页面读取 GET /api/monitor-timeline 的受控着陆场景快照。", {
    left: 78,
    top: 613,
    width: 705,
    height: 26,
  }, {
    fontSize: 13,
    color: C.grayText,
    slideNo,
    role: "image_caption",
  });
  const bullets = [
    ["事件释义", "TRA=-14° 锁、VDT≥90%、L4 ready、THR_LOCK 等关键节点用时间戳呈现。", C.blue, C.paleBlue],
    ["多行曲线", "INPUT / LOGIC / POWER / SENSOR / CMD 分层显示，便于审查人员沿时间线定位问题。", C.teal, C.paleTeal],
    ["验收价值", "适合放在阶段一 Demo：领导看得见流程，工程师可据此复盘每个状态为何出现。", C.orange, C.paleOrange],
  ];
  bullets.forEach(([title, body, color, fill], idx) => {
    addCard(slide, {
      title,
      body,
      box: { left: 832, top: 145 + idx * 132, width: 350, height: 105 },
      color,
      fill,
      slideNo,
    });
  });
  addShape(slide, { left: 835, top: 552, width: 344, height: 62, fill: C.panel, lineFill: C.navy, lineWidth: 1, radius: true });
  addText(slide, "建议现场讲法：先让领导看一眼“时间线”，再回到资源页说明为什么一期需要工程师工作台和验证环境。", {
    left: 852,
    top: 565,
    width: 310,
    height: 42,
  }, {
    fontSize: 14,
    color: C.navy,
    bold: true,
    slideNo,
    role: "talk_track",
    autoFit: "shrinkText",
  });
}

async function slideEvidenceClosure(slide, slideNo) {
  slide.background.fill = "#FFFFFF";
  addHeader(slide, "功能 Demo 05：从样板到验收，已有可落地的证据闭环", "这一页用在 Demo 段收口：说明平台不是只会展示，还能沉淀、复验、扩展", slideNo);
  const flow = [
    ["需求/文档", "来源材料\n接入包", C.blue],
    ["结构化逻辑", "适配器真值\n系统规格", C.teal],
    ["场景回放", "回放轨迹\n故障注入", C.orange],
    ["诊断知识", "诊断报告\n知识资产", C.navy],
    ["验收归档", "证据包\n归档留存", C.teal],
  ];
  flow.forEach(([title, sub, color], idx) => {
    const x = 60 + idx * 238;
    addShape(slide, { left: x, top: 160, width: 185, height: 112, fill: "#FFFFFF", lineFill: color, lineWidth: 2, radius: true });
    addText(slide, title, { left: x + 14, top: 178, width: 155, height: 30 }, {
      fontSize: 18,
      bold: true,
      color,
      alignment: "center",
      slideNo,
      role: "flow_title",
    });
    addText(slide, sub, { left: x + 16, top: 218, width: 153, height: 42 }, {
      fontSize: 13,
      color: C.body,
      alignment: "center",
      slideNo,
      role: "flow_sub",
      autoFit: "shrinkText",
    });
    if (idx < flow.length - 1) {
      addText(slide, "→", { left: x + 188, top: 194, width: 42, height: 42 }, {
        fontSize: 30,
        bold: true,
        color,
        alignment: "center",
        verticalAlignment: "middle",
        slideNo,
        role: "flow_arrow",
      });
    }
  });

  addShape(slide, { left: 78, top: 330, width: 1080, height: 190, fill: C.panel, lineFill: C.line, lineWidth: 1, radius: true });
  addText(slide, "当前可引用的真实能力", { left: 108, top: 352, width: 240, height: 34 }, {
    fontSize: 21,
    bold: true,
    color: C.navy,
    slideNo,
    role: "section_label",
  });
  const proofItems = [
    "反推参考系统：controller.py 作为控制真值；runner / switch / plant 组合生成可解释 trace。",
    "多系统扩展：C919 E-TRAS、landing-gear 等 adapter 已走过 metadata / spec / runtime 验证路径。",
    "验证面：demo_path_smoke、timeline 页面测试、C919 workstation 测试、timeline executor/API 测试可直接复跑。",
    "当前状态记录：P43-03 DONE；timeline simulator delivered；765 tests green；0 CRITICAL findings。",
  ];
  proofItems.forEach((item, idx) => {
    addText(slide, `• ${item}`, { left: 116, top: 392 + idx * 30, width: 990, height: 28 }, {
      fontSize: 15,
      color: C.body,
      slideNo,
      role: "proof_bullet",
      autoFit: "shrinkText",
    });
  });

  addShape(slide, { left: 112, top: 556, width: 1025, height: 70, fill: C.yellow, lineFill: "#EAB308", lineWidth: 1, radius: true });
  addText(slide, "对领导的收口：一期先批“样板平台 + 工程师工作台 + 验证环境”，3 个月要看到的不是论文或概念页，而是这组可操作 Demo、可复跑测试和可归档证据包。", {
    left: 132,
    top: 573,
    width: 985,
    height: 40,
  }, {
    fontSize: 17,
    bold: true,
    color: C.navy,
    slideNo,
    role: "closing_claim",
    autoFit: "shrinkText",
  });
}

const presentation = await PresentationFile.importPptx(await FileBlob.load(inputPptx));
let anchor = presentation.slides.getItem(5);
const builders = [
  slideDemoOverview,
  slideFantuiCockpit,
  slideC919Workstation,
  slideTimelineSim,
  slideMonitorEvidence,
  slideEvidenceClosure,
];

const inserted = [];
for (let i = 0; i < builders.length; i += 1) {
  const { slide } = presentation.slides.insert({ after: anchor });
  anchor = slide;
  inserted.push(slide);
  await builders[i](slide, `Demo-${String(i + 1).padStart(2, "0")}`);
}

for (let i = 0; i < inserted.length; i += 1) {
  const png = await presentation.export({ slide: inserted[i], format: "png", scale: 1 });
  await saveAny(png, path.join(previewDir, `demo-slide-${String(i + 1).padStart(2, "0")}.png`));
}

await fs.writeFile(inspectPath, JSON.stringify({ outputPptx, insertedSlides: builders.length, inspect }, null, 2), "utf8");
const pptx = await PresentationFile.exportPptx(presentation);
await saveAny(pptx, outputPptx);
console.log(outputPptx);
