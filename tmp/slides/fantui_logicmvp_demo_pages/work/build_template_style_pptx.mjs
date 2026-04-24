import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const W = 1672;
const H = 941;
const ROOT = "/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP";
const templateDir = "/Users/Zhuanz/Downloads/AI- FANTUI-Control";
const outputDir = path.join(templateDir, "outputs");
const workDir = path.join(ROOT, "tmp/slides/fantui_logicmvp_demo_pages/template_style_pdf");
const previewDir = path.join(ROOT, "tmp/slides/fantui_logicmvp_demo_pages/preview/pptx-visual-v3");
const outputPptx = path.join(outputDir, "AI-FANTUI-Control_功能Demo补充版_视觉优化版.pptx");
const manifestPath = path.join(outputDir, "AI-FANTUI-Control_功能Demo补充版_视觉优化版_manifest.json");

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

const templateFiles = (await fs.readdir(templateDir))
  .filter((name) => name.toLowerCase().endsWith(".png"))
  .sort()
  .map((name) => path.join(templateDir, name));

if (templateFiles.length !== 6) {
  throw new Error(`Expected 6 template PNG files in ${templateDir}, found ${templateFiles.length}`);
}

const pageFiles = [
  ...templateFiles,
  ...Array.from({ length: 6 }, (_, i) => path.join(workDir, `page-${String(i + 7).padStart(2, "0")}.png`)),
];

for (const file of pageFiles) {
  await fs.access(file);
}

const presentation = Presentation.create({ slideSize: { width: W, height: H } });

for (let i = 0; i < pageFiles.length; i += 1) {
  const slide = presentation.slides.add();
  slide.background.fill = "#FFFFFF";
  const image = slide.images.add({
    blob: await readImageBlob(pageFiles[i]),
    fit: "cover",
    alt: `AI FANTUI Control slide ${i + 1}`,
  });
  image.position = { left: 0, top: 0, width: W, height: H };
  slide.speakerNotes.setText(
    i < 6
      ? "参考模板原页，保留视觉风格。"
      : "功能 Demo 补充页：视觉优化版。真实界面仅作证据窗口，主视觉围绕民机反推控制逻辑、C919 接入、故障仿真与证据闭环展开。"
  );
}

for (let i = 6; i < pageFiles.length; i += 1) {
  const rendered = await presentation.export({ slide: presentation.slides.getItem(i), format: "png", scale: 1 });
  await saveAny(rendered, path.join(previewDir, `slide-${String(i + 1).padStart(2, "0")}.png`));
}

const pptx = await PresentationFile.exportPptx(presentation);
await saveAny(pptx, outputPptx);

await fs.writeFile(
  manifestPath,
  JSON.stringify(
    {
      pptx: outputPptx,
      slide_count: pageFiles.length,
      source_pages: pageFiles,
      preview_dir: previewDir,
      visual_policy:
        "Fixed full-slide raster visuals inside PPTX to avoid cross-machine font/shape drift. Back six pages use reduced screenshot evidence windows and larger semantic aviation-control visuals.",
    },
    null,
    2
  ),
  "utf8"
);

console.log(outputPptx);
console.log(`slides=${pageFiles.length}`);
