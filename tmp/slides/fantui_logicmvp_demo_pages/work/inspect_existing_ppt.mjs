import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const input = "/Users/Zhuanz/Downloads/AI赋能民机控制逻辑智能分析与验证平台_一期_立项汇报.pptx";
const outDir = "/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/tmp/slides/fantui_logicmvp_demo_pages/preview/existing";

await fs.mkdir(outDir, { recursive: true });
const pptx = await FileBlob.load(input);
const presentation = await PresentationFile.importPptx(pptx);

const lines = [`slides=${presentation.slides.count}`];
for (let i = 0; i < presentation.slides.count; i += 1) {
  const slide = presentation.slides.getItem(i);
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  const output = path.join(outDir, `slide-${String(i + 1).padStart(2, "0")}.png`);
  if (typeof png.save === "function") {
    await png.save(output);
  } else if (png instanceof Uint8Array || Buffer.isBuffer(png)) {
    await fs.writeFile(output, png);
  } else if (png?.bytes instanceof Uint8Array) {
    await fs.writeFile(output, png.bytes);
  } else if (typeof png?.arrayBuffer === "function") {
    await fs.writeFile(output, Buffer.from(await png.arrayBuffer()));
  } else {
    throw new TypeError(`Unsupported export payload: ${png?.constructor?.name || typeof png}`);
  }
  lines.push(output);
}
await fs.writeFile(path.join(outDir, "rendered.txt"), lines.join("\n"), "utf8");
console.log(lines.join("\n"));
