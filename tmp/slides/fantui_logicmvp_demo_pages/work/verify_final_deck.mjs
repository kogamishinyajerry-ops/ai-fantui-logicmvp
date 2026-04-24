import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const deck = "/Users/Zhuanz/Downloads/fantui_logicmvp_ppt_augmented/AI赋能民机控制逻辑智能分析与验证平台_一期_立项汇报_功能Demo增强版.pptx";
const outDir = "/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/tmp/slides/fantui_logicmvp_demo_pages/preview/final-import";
await fs.mkdir(outDir, { recursive: true });

async function saveAny(blobLike, target) {
  if (typeof blobLike?.save === "function") return blobLike.save(target);
  if (blobLike instanceof Uint8Array || Buffer.isBuffer(blobLike)) return fs.writeFile(target, blobLike);
  if (blobLike?.bytes instanceof Uint8Array) return fs.writeFile(target, blobLike.bytes);
  if (typeof blobLike?.arrayBuffer === "function") return fs.writeFile(target, Buffer.from(await blobLike.arrayBuffer()));
  throw new TypeError(`Unsupported payload: ${blobLike?.constructor?.name || typeof blobLike}`);
}

const presentation = await PresentationFile.importPptx(await FileBlob.load(deck));
const lines = [`slides=${presentation.slides.count}`];
for (let i = 6; i < 12; i += 1) {
  const slide = presentation.slides.getItem(i);
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  const target = path.join(outDir, `final-slide-${String(i + 1).padStart(2, "0")}.png`);
  await saveAny(png, target);
  lines.push(target);
}
await fs.writeFile(path.join(outDir, "verify.txt"), lines.join("\n"), "utf8");
console.log(lines.join("\n"));
