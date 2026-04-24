from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path("/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP")
TEMPLATE_DIR = Path("/Users/Zhuanz/Downloads/AI- FANTUI-Control")
SCREENSHOT_DIR = ROOT / "tmp/pdfs/fantui_demo_pdf/screenshots"
OUT = ROOT / "output/pdf/AI-FANTUI-Control_六页模板加Demo截图辅助展示.pdf"
WORK = ROOT / "tmp/pdfs/fantui_demo_pdf/pages"

W, H = 1672, 941
NAVY = "#061840"
BLUE = "#2568D9"
TEAL = "#17A79B"
ORANGE = "#FF6400"
PALE = "#F2F7FF"
INK = "#0B183D"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [("/System/Library/Fonts/STHeiti Medium.ttc", 1), ("/System/Library/Fonts/Supplemental/Songti.ttc", 1)]
        if bold
        else [("/System/Library/Fonts/STHeiti Light.ttc", 1), ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 0)]
    )
    candidates.append(("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0))
    for path, index in candidates:
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except Exception:
            continue
    return ImageFont.load_default()


def fit_cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    iw, ih = im.size
    scale = max(tw / iw, th / ih)
    nw, nh = math.ceil(iw * scale), math.ceil(ih * scale)
    resized = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def rounded(draw: ImageDraw.ImageDraw, box, radius=26, fill="white", outline=BLUE, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def add_demo_page(src: Path, title: str, subtitle: str, tag: str, dst: Path) -> None:
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    # Soft aviation-blue backdrop, intentionally simpler than the generated first six pages.
    d.rectangle((0, 0, W, H), fill="#FFFFFF")
    d.ellipse((-180, 710, 480, 1110), fill="#E9F3FF")
    d.ellipse((1210, 680, 1880, 1080), fill="#E9F3FF")
    d.rounded_rectangle((56, 44, 1616, 132), radius=34, fill=PALE, outline="#BFD4F8", width=2)
    d.text((92, 66), title, font=font(46, True), fill=NAVY)
    d.rounded_rectangle((1195, 62, 1585, 116), radius=23, fill=TEAL, outline=TEAL)
    d.text((1218, 76), tag, font=font(24, True), fill="white")
    d.text((92, 148), subtitle, font=font(27, True), fill=TEAL)

    screen = Image.open(src).convert("RGB")
    shot = fit_cover(screen, (1480, 705))
    shadow = Image.new("RGBA", (1500, 725), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((10, 12, 1490, 718), radius=30, fill=(30, 70, 130, 45))
    img.paste(shadow, (88, 190), shadow)
    rounded(d, (96, 188, 1576, 893), radius=30, fill="white", outline=BLUE, width=4)
    img.paste(shot, (96, 188))
    d.rounded_rectangle((96, 188, 1576, 893), radius=30, outline=BLUE, width=4)

    d.rounded_rectangle((104, 820, 1568, 888), radius=26, fill=(255, 255, 255), outline="#C8D9F8", width=2)
    d.ellipse((132, 834, 180, 882), fill=ORANGE)
    d.line((145, 858, 155, 870, 172, 842), fill="white", width=7, joint="curve")
    d.text((202, 838), "辅助展示素材：来自当前项目本地 demo 页面截图，可用于汇报时补充说明真实进度。", font=font(28, True), fill=INK)
    img.save(dst, quality=95)


def build() -> list[Path]:
    WORK.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []
    template_files = [
        "ChatGPT Image 2026年4月24日 09_34_55 (1).png",
        "ChatGPT Image 2026年4月24日 09_34_56 (2).png",
        "ChatGPT Image 2026年4月24日 09_34_56 (3).png",
        "ChatGPT Image 2026年4月24日 09_34_56 (4).png",
        "ChatGPT Image 2026年4月24日 09_34_56 (5).png",
        "ChatGPT Image 2026年4月24日 09_34_56 (6).png",
    ]
    for idx, name in enumerate(template_files, start=1):
        src = TEMPLATE_DIR / name
        im = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
        dst = WORK / f"page-{idx:02d}.png"
        im.save(dst, quality=95)
        pages.append(dst)

    demos = [
        (
            SCREENSHOT_DIR / "demo-cockpit.png",
            "Demo 截图 1：反推逻辑演示舱",
            "拉杆、VDT、故障条件、逻辑主板与结果摘要在同一屏联动。",
            "FANTUI / lever snapshot",
        ),
        (
            SCREENSHOT_DIR / "c919-workstation.png",
            "Demo 截图 2：C919 E-TRAS 工作台",
            "第二套控制逻辑已经接入同一类可解释工作台。",
            "C919 E-TRAS",
        ),
        (
            SCREENSHOT_DIR / "timeline-sim.png",
            "Demo 截图 3：Timeline Simulator",
            "时间脚本可驱动 FANTUI 与 C919，并输出断言与故障阻塞证据。",
            "timeline simulate",
        ),
        (
            SCREENSHOT_DIR / "c919-panel.png",
            "Demo 截图 4：C919 MFD 控制面板",
            "冻结版 V1.0 的有状态 tick 模型可在本地面板中演示。",
            "port 9191",
        ),
        (
            SCREENSHOT_DIR / "c919-circuit.png",
            "Demo 截图 5：E-TRAS 控制逻辑电路图",
            "把 C919 E-TRAS 的状态机、信号流和输出命令做成可展示的工程图。",
            "state machine / signal flow",
        ),
    ]
    for idx, (src, title, subtitle, tag) in enumerate(demos, start=7):
        dst = WORK / f"page-{idx:02d}.png"
        add_demo_page(src, title, subtitle, tag, dst)
        pages.append(dst)
    return pages


def write_pdf(pages: list[Path]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    for p in pages:
        c.drawImage(ImageReader(str(p)), 0, 0, width=W, height=H, preserveAspectRatio=False, mask="auto")
        c.showPage()
    c.save()


if __name__ == "__main__":
    built_pages = build()
    write_pdf(built_pages)
    print(OUT)
    print(f"pages={len(built_pages)}")
