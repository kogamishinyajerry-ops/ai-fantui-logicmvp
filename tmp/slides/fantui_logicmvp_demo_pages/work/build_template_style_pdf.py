from __future__ import annotations

import json
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


W, H = 1672, 941
ROOT = Path("/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP")
TEMPLATE_DIR = Path("/Users/Zhuanz/Downloads/AI- FANTUI-Control")
OUT_DIR = TEMPLATE_DIR / "outputs"
WORK_DIR = ROOT / "tmp/slides/fantui_logicmvp_demo_pages/template_style_pdf"
SCREEN_DIR = ROOT / "tmp/slides/fantui_logicmvp_demo_pages/screens"

OUT_DIR.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DIR = WORK_DIR / "generated_raster_assets"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

PDF_OUT = OUT_DIR / "AI-FANTUI-Control_功能Demo补充版.pdf"
MANIFEST = OUT_DIR / "AI-FANTUI-Control_功能Demo补充版_manifest.json"
TEMPLATE_FILES = sorted(TEMPLATE_DIR.glob("*.png"))

FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_REG = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_ARIAL = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


NAVY = "#06183D"
BLUE = "#2368D9"
LIGHT_BLUE = "#DDEBFF"
TEAL = "#16A69D"
LIGHT_TEAL = "#E8FBF7"
ORANGE = "#FF6A00"
LIGHT_ORANGE = "#FFF0E5"
PURPLE = "#6257D9"
LIGHT_PURPLE = "#F0EEFF"
GRAY = "#4C5E7A"
PANEL = "#F8FBFF"
LINE = "#5B8DEE"
YELLOW = "#FFF6D8"
GREEN = "#188F55"


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int):
    lines = []
    for para in str(text).split("\n"):
        if not para:
            lines.append("")
            continue
        line = ""
        for ch in para:
            trial = line + ch
            if text_size(draw, trial, fnt)[0] <= max_width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = ch
        if line:
            lines.append(line)
    return lines


def draw_wrapped(draw, text, xy, max_width, fnt, fill=NAVY, line_gap=8, max_lines=None, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    line_h = text_size(draw, "国", fnt)[1] + line_gap
    for line in lines:
        lw = text_size(draw, line, fnt)[0]
        dx = 0
        if align == "center":
            dx = (max_width - lw) // 2
        elif align == "right":
            dx = max_width - lw
        draw.text((x + dx, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def rounded(draw, box, radius=24, fill="white", outline=BLUE, width=4):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, box, text, fill=TEAL, fnt=None):
    fnt = fnt or font(38, True)
    rounded(draw, box, radius=(box[3] - box[1]) // 2, fill=fill, outline=fill, width=1)
    tw, th = text_size(draw, text, fnt)
    draw.text(((box[0] + box[2] - tw) // 2, (box[1] + box[3] - th) // 2 - 2), text, font=fnt, fill="white")


def title(draw, prefix: str, orange: str, suffix: str = "", y=55, size=76):
    x = 130
    max_width = W - x - 120
    while size > 52:
        f = font(size, True)
        total = text_size(draw, prefix, f)[0] + text_size(draw, orange, f)[0] + text_size(draw, suffix, f)[0] + 16
        if total <= max_width:
            break
        size -= 2
    f = font(size, True)
    draw.text((x, y), prefix, font=f, fill=NAVY)
    x += text_size(draw, prefix, f)[0] + 8
    draw.text((x, y), orange, font=f, fill=ORANGE)
    x += text_size(draw, orange, f)[0] + 8
    if suffix:
        draw.text((x, y), suffix, font=f, fill=NAVY)
    # small decorative marks
    draw.polygon([(68, 72), (96, 48), (112, 66), (82, 92)], fill="#8DC6FF", outline=BLUE)
    draw.polygon([(110, 32), (130, 62), (118, 72)], fill="#8DC6FF", outline=BLUE)
    draw.polygon([(65, 115), (100, 112), (94, 132)], fill="#8DC6FF", outline=BLUE)


def subtitle(draw, text: str, y=175, x=360, w=930):
    f = font(36, True)
    for size in (36, 34, 32, 30, 28):
        f = font(size, True)
        if text_size(draw, text, f)[0] <= w - 54:
            break
    pill(draw, (x, y, x + w, y + 62), text, fill=TEAL, fnt=f)


def base_page():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    # soft sky / cloud bands
    d.ellipse((-170, 670, 480, 1120), fill="#EAF4FF")
    d.ellipse((1270, 120, 1830, 420), fill="#EAF4FF")
    d.ellipse((1210, 690, 1860, 1110), fill="#EAF4FF")
    for cx, cy in [(70, 870), (132, 842), (205, 865), (1435, 180), (1510, 155), (1590, 188)]:
        d.ellipse((cx - 55, cy - 28, cx + 75, cy + 35), fill="#DCEBFF")
    # simple airplane motif
    d.polygon([(1410, 76), (1578, 118), (1410, 135), (1360, 108)], fill="#DBEAFE", outline="#395D9B")
    d.polygon([(1490, 111), (1598, 72), (1585, 102)], fill="#C8DAF7", outline="#395D9B")
    d.arc((1320, 110, 1670, 260), 190, 335, fill="#BBD4FB", width=8)
    return img, d


def fit_image(src_path: Path, size, crop=True):
    im = Image.open(src_path).convert("RGB")
    target_w, target_h = size
    if crop:
        scale = max(target_w / im.width, target_h / im.height)
    else:
        scale = min(target_w / im.width, target_h / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas_img = Image.new("RGB", size, "white")
    canvas_img.paste(im, ((target_w - nw) // 2, (target_h - nh) // 2))
    return canvas_img


def fit_pil_image(im: Image.Image, size, crop=True):
    im = im.convert("RGB")
    target_w, target_h = size
    scale = max(target_w / im.width, target_h / im.height) if crop else min(target_w / im.width, target_h / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas_img = Image.new("RGB", size, "white")
    canvas_img.paste(im, ((target_w - nw) // 2, (target_h - nh) // 2))
    return canvas_img


def paste_rounded(base: Image.Image, src_path: Path, box, radius=32):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    shadow = Image.new("RGBA", (w + 26, h + 26), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((10, 10, w + 10, h + 10), radius=radius, fill=(30, 70, 120, 55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    base.paste(shadow, (x1 - 8, y1 - 8), shadow)
    frame = Image.new("RGBA", (w, h), "white")
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    content = fit_image(src_path, (w, h), crop=True)
    frame.paste(content, (0, 0), mask)
    base.paste(frame, (x1, y1), mask)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, outline=BLUE, width=4)


def paste_pil_rounded(base: Image.Image, content: Image.Image, box, radius=32, outline=BLUE, width=4, shadow=True):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    if shadow:
        sh = Image.new("RGBA", (w + 26, h + 26), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((10, 10, w + 10, h + 10), radius=radius, fill=(30, 70, 120, 45))
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        base.paste(sh, (x1 - 8, y1 - 8), sh)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    frame = fit_pil_image(content, (w, h), crop=True)
    base.paste(frame, (x1, y1), mask)
    if outline:
        d = ImageDraw.Draw(base)
        d.rounded_rectangle(box, radius=radius, outline=outline, width=width)


def numbered_card(draw, num, title_txt, body, box, accent=BLUE, fill="#F7FAFF"):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=26, fill=fill, outline=accent, width=4)
    draw.ellipse((x1 + 24, y1 + 24, x1 + 92, y1 + 92), fill=accent, outline=accent)
    draw.text((x1 + 47, y1 + 33), str(num), font=font(42, True), fill="white", anchor="ma")
    draw_wrapped(draw, title_txt, (x1 + 110, y1 + 28), x2 - x1 - 135, font(34, True), fill=NAVY, line_gap=4, max_lines=2)
    draw_wrapped(draw, body, (x1 + 38, y1 + 118), x2 - x1 - 76, font(25), fill=GRAY, line_gap=8, max_lines=5)


def metric(draw, title_txt, body, box, accent=BLUE):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=24, fill="white", outline=accent, width=3)
    draw.text((x1 + 24, y1 + 22), title_txt, font=font(35, True), fill=accent)
    draw_wrapped(draw, body, (x1 + 24, y1 + 76), x2 - x1 - 48, font(24), fill=NAVY, line_gap=6)


def speech(draw, text, box, fill="white"):
    rounded(draw, box, radius=36, fill=fill, outline=NAVY, width=4)
    x1, y1, x2, y2 = box
    draw.polygon([(x2 - 80, y2 - 8), (x2 - 40, y2 + 50), (x2 - 135, y2 - 15)], fill=fill, outline=NAVY)
    draw_wrapped(draw, text, (x1 + 36, y1 + 28), x2 - x1 - 72, font(27, True), fill=NAVY, line_gap=8, align="center")


def paste_crop(base: Image.Image, src_path: Path, crop, box, radius=0, shadow=False, outline=None, transparent_white=False, flip=False, blur=0, opacity=1.0):
    src = Image.open(src_path).convert("RGBA").crop(crop)
    if flip:
        src = ImageOps.mirror(src)
    if blur:
        src = src.filter(ImageFilter.GaussianBlur(blur))
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    src = src.resize((w, h), Image.LANCZOS)
    if transparent_white:
        px = src.load()
        for yy in range(src.height):
            for xx in range(src.width):
                r, g, b, a = px[xx, yy]
                if r > 244 and g > 244 and b > 244:
                    px[xx, yy] = (r, g, b, 0)
    mask = Image.new("L", (w, h), 255)
    if radius:
        mask = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
        if transparent_white:
            alpha = src.getchannel("A")
            mask = Image.composite(mask, Image.new("L", (w, h), 0), alpha)
    elif transparent_white:
        mask = src.getchannel("A")
    if opacity < 1:
        mask = mask.point(lambda p: int(p * opacity))
    if shadow:
        sh = Image.new("RGBA", (w + 28, h + 28), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((10, 10, w + 10, h + 10), radius=radius or 24, fill=(16, 45, 90, 45))
        sh = sh.filter(ImageFilter.GaussianBlur(9))
        base.paste(sh, (x1 - 10, y1 - 10), sh)
    base.paste(src, (x1, y1), mask)
    if outline:
        d = ImageDraw.Draw(base)
        d.rounded_rectangle(box, radius=radius, outline=outline, width=4)


def paste_template_crop(base: Image.Image, template_idx: int, crop, box, radius=0, shadow=False, outline=None, transparent_white=False, flip=False, blur=0, opacity=1.0):
    if not TEMPLATE_FILES:
        return
    paste_crop(base, TEMPLATE_FILES[template_idx - 1], crop, box, radius=radius, shadow=shadow, outline=outline, transparent_white=transparent_white, flip=flip, blur=blur, opacity=opacity)


def paste_generated_icon(base: Image.Image, kind: str, box, radius=18, outline=None):
    crops = {
        # All of these are raster crops from the supplied AI-generated template pages.
        "logic_mess": (2, (425, 295, 812, 650)),
        "state_card": (3, (972, 360, 1123, 665)),
        "test_card": (3, (1290, 360, 1450, 665)),
        "report_card": (3, (1452, 360, 1620, 665)),
        "folder": (4, (150, 365, 430, 600)),
        "replicate": (4, (1080, 395, 1485, 620)),
        "road": (5, (430, 305, 1255, 465)),
        "benefit_rocket": (6, (190, 245, 606, 420)),
        "benefit_shield": (6, (620, 245, 1020, 420)),
        "benefit_screen": (6, (1030, 245, 1438, 420)),
        "dashboard": (6, (520, 430, 1055, 705)),
    }
    if kind in crops:
        idx, crop = crops[kind]
        paste_template_crop(base, idx, crop, box, radius=radius, shadow=True, outline=outline)


def paste_robot_art(base: Image.Image, side: str, box):
    paste_template_crop(base, 3, (485, 405, 730, 760), box, transparent_white=True)


def paste_cutout(base: Image.Image, template_idx: int, crop, box, flip=False, opacity=1.0):
    paste_template_crop(base, template_idx, crop, box, transparent_white=True, flip=flip, opacity=opacity)


def hex_rgb(color: str):
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def alpha_composite_rgb(base: Image.Image, overlay: Image.Image):
    composed = Image.alpha_composite(base.convert("RGBA"), overlay)
    base.paste(composed.convert("RGB"))


def glow_round_rect(img: Image.Image, box, radius=28, fill=(255, 255, 255, 225), outline=BLUE, width=3, glow=True):
    if glow:
        rgb = hex_rgb(outline)
        aura = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ad = ImageDraw.Draw(aura)
        ad.rounded_rectangle(box, radius=radius, outline=rgb + (145,), width=12)
        aura = aura.filter(ImageFilter.GaussianBlur(10))
        alpha_composite_rgb(img, aura)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=hex_rgb(outline) + (255,), width=width)


def draw_plane_art(d, x, y, scale=1.0):
    pts = [
        (x, y + 38 * scale),
        (x + 250 * scale, y + 80 * scale),
        (x + 268 * scale, y + 100 * scale),
        (x + 60 * scale, y + 104 * scale),
        (x - 40 * scale, y + 76 * scale),
    ]
    d.polygon(pts, fill="#DCEBFF", outline="#5B8DEE")
    d.polygon([(x + 110 * scale, y + 78 * scale), (x + 245 * scale, y + 30 * scale), (x + 220 * scale, y + 74 * scale)], fill="#C9DDF9", outline="#5B8DEE")
    d.polygon([(x + 112 * scale, y + 84 * scale), (x + 232 * scale, y + 142 * scale), (x + 185 * scale, y + 92 * scale)], fill="#C9DDF9", outline="#5B8DEE")
    d.line((x - 35 * scale, y + 130 * scale, x + 275 * scale, y + 160 * scale), fill="#BBD4FB", width=max(3, int(6 * scale)))


def draw_holo_network(img: Image.Image, box, accent=TEAL, variant=0):
    x1, y1, x2, y2 = box
    glow_round_rect(img, box, radius=30, fill=(7, 24, 55, 238), outline=accent, width=4)
    d = ImageDraw.Draw(img, "RGBA")
    nodes = [
        (x1 + 90, y1 + 85),
        (x1 + 245, y1 + 62),
        (x1 + 410, y1 + 112),
        (x1 + 165, y1 + 210),
        (x1 + 355, y1 + 240),
        (x1 + 535, y1 + 180),
    ]
    if variant == 1:
        nodes = [(x + (i % 2) * 22, y + ((i + 1) % 2) * 18) for i, (x, y) in enumerate(nodes)]
    for a, b in [(0, 1), (1, 2), (1, 3), (3, 4), (2, 5), (4, 5)]:
        d.line((nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1]), fill=hex_rgb(accent) + (215,), width=5)
    for i, (x, y) in enumerate(nodes):
        col = [BLUE, TEAL, ORANGE, PURPLE, GREEN, "#27C3FF"][i % 6]
        d.ellipse((x - 24, y - 24, x + 24, y + 24), fill=hex_rgb(col) + (235,), outline=(255, 255, 255, 255), width=4)
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 255, 255, 230))
    for i in range(4):
        yy = y2 - 68 + i * 13
        d.rounded_rectangle((x1 + 42, yy, x1 + 250 + i * 65, yy + 5), radius=3, fill=hex_rgb("#6DE7FF") + (150,))


def draw_lever_art(img: Image.Image, box):
    x1, y1, x2, y2 = box
    d = ImageDraw.Draw(img, "RGBA")
    glow_round_rect(img, (x1, y1 + 160, x2, y2), radius=34, fill=(255, 255, 255, 215), outline=BLUE, width=4)
    cx, cy = x1 + 160, y1 + 230
    d.arc((cx - 115, cy - 115, cx + 115, cy + 115), 190, 345, fill=hex_rgb(BLUE) + (220,), width=16)
    d.line((cx - 48, cy + 55, cx + 78, cy - 90), fill=hex_rgb(BLUE) + (245,), width=22)
    d.line((cx - 38, cy + 48, cx + 72, cy - 80), fill=(255, 255, 255, 70), width=8)
    d.ellipse((cx + 50, cy - 122, cx + 115, cy - 58), fill=hex_rgb(ORANGE) + (255,), outline=hex_rgb("#B84900") + (255,), width=5)
    d.rounded_rectangle((cx - 112, cy + 74, cx + 116, cy + 110), radius=14, fill=hex_rgb("#EAF4FF") + (255,), outline=hex_rgb(BLUE) + (255,), width=5)


def draw_timeline_art(img: Image.Image, box):
    x1, y1, x2, y2 = box
    d = ImageDraw.Draw(img, "RGBA")
    glow_round_rect(img, box, radius=28, fill=(255, 255, 255, 220), outline=ORANGE, width=3)
    pts = [(x1 + 55, y2 - 75), (x1 + 210, y1 + 90), (x1 + 390, y1 + 145), (x2 - 80, y1 + 70)]
    d.line(pts, fill=hex_rgb("#9FB7D8") + (245,), width=34, joint="curve")
    d.line(pts, fill=(255, 255, 255, 245), width=5, joint="curve")
    for i, (x, y) in enumerate(pts, start=1):
        c = [BLUE, TEAL, ORANGE, PURPLE][i - 1]
        d.ellipse((x - 35, y - 35, x + 35, y + 35), fill=hex_rgb(c) + (255,), outline=(255, 255, 255, 255), width=5)
        d.text((x, y - 4), str(i), font=font(34, True), fill="white", anchor="mm")


def draw_scene_background(img: Image.Image):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    for i in range(h):
        r = int(247 - i * 0.018)
        g = int(251 - i * 0.01)
        b = 255
        d.line((0, i, w, i), fill=(r, g, b, 255))
    for cx, cy, rx, ry in [(110, 420, 260, 95), (1110, 95, 300, 120), (760, 450, 280, 80)]:
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(220, 235, 255, 170))
    draw_plane_art(d, 960, 48, 0.85)
    for x in range(40, w, 90):
        d.ellipse((x, 42 + (x % 180) // 4, x + 4, 46 + (x % 180) // 4), fill=(91, 141, 238, 55))


def scene_asset(name: str, template_idx: int, crop, screen_path: Path | None = None, accent=BLUE, mode="overview"):
    out = ASSET_DIR / f"{name}.png"
    if out.exists():
        return out
    w, h = 1320, 500
    plate = Image.new("RGB", (w, h), "#F8FBFF")
    draw_scene_background(plate)
    d = ImageDraw.Draw(plate, "RGBA")
    d.rounded_rectangle((24, 24, w - 24, h - 24), radius=44, outline=hex_rgb("#8CB6E8") + (255,), width=4)
    d.rounded_rectangle((56, 58, w - 56, h - 52), radius=36, fill=(255, 255, 255, 138), outline=hex_rgb("#D7E7FF") + (255,), width=2)

    if mode == "overview":
        paste_cutout(plate, 2, (70, 310, 410, 660), (62, 158, 330, 468))
        paste_cutout(plate, 3, (485, 405, 730, 760), (520, 146, 760, 458))
        draw_holo_network(plate, (805, 112, 1240, 392), TEAL, variant=0)
        draw_timeline_art(plate, (340, 72, 520, 215))
        for x, y, c in [(375, 305, BLUE), (456, 262, TEAL), (768, 255, ORANGE), (792, 330, PURPLE)]:
            d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=hex_rgb(c) + (255,), outline=(255, 255, 255, 255), width=4)
        d.line((395, 302, 515, 294, 805, 260), fill=hex_rgb(BLUE) + (210,), width=7)
    elif mode == "cockpit":
        paste_cutout(plate, 2, (80, 330, 400, 660), (62, 140, 320, 468))
        draw_lever_art(plate, (315, 118, 610, 430))
        draw_holo_network(plate, (620, 105, 1025, 405), BLUE, variant=1)
        paste_pil_rounded(plate, fit_image(SCREEN_DIR / "demo-fantui-cockpit.png", (260, 170)), (1012, 165, 1245, 335), radius=20, outline=TEAL, width=3)
    elif mode == "c919":
        paste_cutout(plate, 4, (115, 360, 455, 595), (55, 128, 340, 366))
        draw_holo_network(plate, (415, 95, 745, 405), TEAL, variant=1)
        paste_cutout(plate, 3, (485, 405, 730, 760), (785, 155, 1010, 455))
        paste_pil_rounded(plate, fit_image(SCREEN_DIR / "demo-c919-workstation.png", (300, 190)), (980, 155, 1248, 350), radius=22, outline=ORANGE, width=3)
        d.line((342, 248, 410, 248), fill=hex_rgb(BLUE) + (230,), width=10)
        d.line((745, 248, 790, 248), fill=hex_rgb(TEAL) + (230,), width=10)
    elif mode == "timeline":
        paste_cutout(plate, 3, (485, 405, 730, 760), (58, 130, 300, 455))
        draw_timeline_art(plate, (330, 85, 770, 335))
        draw_holo_network(plate, (805, 96, 1240, 395), ORANGE, variant=1)
        paste_pil_rounded(plate, fit_image(SCREEN_DIR / "demo-timeline-sim.png", (250, 155)), (930, 225, 1220, 382), radius=18, outline=ORANGE, width=3)
    elif mode == "monitor":
        paste_cutout(plate, 6, (1050, 430, 1465, 800), (54, 142, 340, 438))
        draw_holo_network(plate, (405, 92, 1045, 408), BLUE, variant=1)
        paste_pil_rounded(plate, fit_image(SCREEN_DIR / "demo-monitor-timeline.png", (360, 190)), (650, 178, 1025, 350), radius=20, outline=TEAL, width=3)
        paste_cutout(plate, 3, (485, 405, 730, 760), (1050, 155, 1240, 420))
    elif mode == "closure":
        paste_cutout(plate, 3, (485, 405, 730, 760), (68, 138, 315, 456))
        glow_round_rect(plate, (400, 88, 930, 360), radius=30, fill=(7, 24, 55, 232), outline=BLUE, width=4)
        cd = ImageDraw.Draw(plate, "RGBA")
        # Abstract platform cockpit: charts and logic map without fake numeric claims.
        for i, (x, y, c) in enumerate([(470, 165, GREEN), (555, 230, BLUE), (650, 175, TEAL), (760, 245, ORANGE), (840, 165, PURPLE)]):
            cd.ellipse((x - 24, y - 24, x + 24, y + 24), fill=hex_rgb(c) + (235,), outline=(255, 255, 255, 255), width=4)
        for a, b in [((470, 165), (555, 230)), ((555, 230), (650, 175)), ((650, 175), (760, 245)), ((760, 245), (840, 165))]:
            cd.line((a[0], a[1], b[0], b[1]), fill=hex_rgb(TEAL) + (200,), width=5)
        for i, c in enumerate([BLUE, TEAL, ORANGE, PURPLE]):
            x = 455 + i * 102
            cd.rounded_rectangle((x, 290 - i * 22, x + 54, 320), radius=8, fill=hex_rgb(c) + (220,))
        cd.arc((725, 230, 890, 395), 190, 348, fill=hex_rgb("#6DE7FF") + (210,), width=10)
        cd.ellipse((788, 290, 830, 332), fill=hex_rgb(ORANGE) + (235,), outline=(255, 255, 255, 240), width=4)
        paste_cutout(plate, 3, (485, 405, 730, 760), (1010, 138, 1250, 456))
        for x, c in [(365, BLUE), (662, TEAL), (962, ORANGE)]:
            d.ellipse((x - 36, 405 - 36, x + 36, 405 + 36), fill=hex_rgb(c) + (245,), outline=(255, 255, 255, 255), width=5)
    plate.save(out, quality=95)
    return out


def circle_num(draw, num, xy, accent=BLUE, r=38):
    x, y = xy
    draw.ellipse((x - r, y - r, x + r, y + r), fill=accent, outline="white", width=6)
    draw.text((x, y - 4), str(num), font=font(43, True), fill="white", anchor="mm")


def panel_header(draw, box, num, title_txt, accent=BLUE):
    x1, y1, x2, _ = box
    rounded(draw, box, radius=22, fill="white", outline=accent, width=4)
    draw.rounded_rectangle((x1 + 18, y1 - 2, x2 - 18, y1 + 66), radius=18, fill=accent, outline=accent)
    circle_num(draw, num, (x1 + 62, y1 + 30), accent=accent, r=34)
    draw.text((x1 + 118, y1 + 13), title_txt, font=font(33, True), fill="white")


def icon(draw, kind, box, accent=BLUE):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    if kind == "lever":
        draw.arc((x1 + 16, y1 + 22, x2 - 16, y2 + 18), 190, 350, fill=accent, width=8)
        draw.line((cx - 38, cy + 34, cx + 35, cy - 40), fill=accent, width=13)
        draw.ellipse((cx + 18, cy - 62, cx + 68, cy - 12), fill=ORANGE, outline=accent, width=5)
        draw.rounded_rectangle((cx - 60, cy + 40, cx + 68, cy + 64), radius=10, fill="#DDEBFF", outline=accent, width=4)
    elif kind == "adapter":
        draw.rounded_rectangle((x1 + int(w * 0.12), y1 + int(h * 0.08), x2 - int(w * 0.12), y2 - int(h * 0.12)), radius=14, fill="white", outline=accent, width=5)
        draw.rectangle((x1 + int(w * 0.30), y1 + int(h * 0.28), x2 - int(w * 0.30), y1 + int(h * 0.40)), fill=accent)
        draw.line((cx, y1 + int(h * 0.40), cx, y2 - int(h * 0.36)), fill=accent, width=6)
        for dx in (-int(w * 0.23), int(w * 0.23)):
            draw.rounded_rectangle((cx + dx - int(w * 0.17), y2 - int(h * 0.43), cx + dx + int(w * 0.17), y2 - int(h * 0.13)), radius=10, fill=LIGHT_TEAL, outline=TEAL, width=4)
    elif kind == "timeline":
        draw.line((x1 + 28, cy + 24, x2 - 28, cy + 24), fill=accent, width=8)
        for i, c in enumerate((BLUE, TEAL, ORANGE)):
            px = x1 + 42 + i * ((x2 - x1 - 84) // 2)
            draw.ellipse((px - 22, cy + 2, px + 22, cy + 46), fill=c, outline="white", width=5)
            draw.line((px, cy + 2, px + 18, y1 + 24), fill=c, width=5)
    elif kind == "evidence":
        draw.rounded_rectangle((x1 + 20, y1 + 38, x2 - 18, y2 - 18), radius=18, fill=YELLOW, outline=ORANGE, width=5)
        draw.polygon([(x1 + 42, y1 + 38), (x1 + 85, y1 + 10), (x1 + 128, y1 + 38)], fill="#FFE0B8", outline=ORANGE)
        for yy in (cy - 10, cy + 20, cy + 50):
            draw.line((x1 + 62, yy, x2 - 58, yy), fill=accent, width=5)
    elif kind == "monitor":
        draw.rounded_rectangle((x1 + 16, y1 + 16, x2 - 16, y2 - 34), radius=16, fill="#EEF6FF", outline=accent, width=5)
        draw.line((x1 + 44, y2 - 56, x2 - 44, y2 - 56), fill=TEAL, width=7)
        draw.line((cx, y2 - 34, cx, y2 - 8), fill=accent, width=8)
        draw.rounded_rectangle((cx - 55, y2 - 10, cx + 55, y2 + 4), radius=6, fill=accent)


def comic_caption(draw, text, box, accent=BLUE):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=24, fill="white", outline=accent, width=3)
    draw_wrapped(draw, text, (x1 + 24, y1 + 18), x2 - x1 - 48, font(27, True), fill=NAVY, line_gap=8, align="center")


def big_bottom_line(draw, text, box, accent=ORANGE):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=38, fill="white", outline=BLUE, width=3)
    draw.ellipse((x1 + 28, y1 + 18, x1 + 86, y1 + 76), fill=accent, outline=accent)
    draw.line((x1 + 46, y1 + 50, x1 + 56, y1 + 62, x1 + 76, y1 + 34), fill="white", width=8, joint="curve")
    draw_wrapped(draw, text, (x1 + 118, y1 + 23), x2 - x1 - 155, font(41, True), fill=NAVY, line_gap=8, align="center")


def right_arrow(draw, x1, y, x2, accent=BLUE):
    mid = y
    draw.polygon(
        [(x2, mid), (x2 - 54, mid - 38), (x2 - 54, mid - 16), (x1, mid - 16), (x1, mid + 16), (x2 - 54, mid + 16), (x2 - 54, mid + 38)],
        fill="#66A6FF",
        outline=accent,
    )


def draw_robot(draw, box, facing="right"):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    flip = facing == "left"
    def sx(x):
        return x2 - (x - x1) if flip else x
    # cape
    cape = [(sx(x1 + w * 0.28), y1 + h * 0.42), (sx(x1 + w * 0.03), y1 + h * 0.62), (sx(x1 + w * 0.35), y1 + h * 0.75)]
    draw.polygon(cape, fill="#3BB6B1", outline=TEAL)
    # body
    draw.ellipse((x1 + w * 0.27, y1 + h * 0.40, x1 + w * 0.78, y1 + h * 0.92), fill="white", outline="#8CB6E8", width=4)
    draw.ellipse((x1 + w * 0.42, y1 + h * 0.63, x1 + w * 0.65, y1 + h * 0.84), fill=TEAL)
    draw.text((x1 + w * 0.535, y1 + h * 0.735), "AI", font=font(max(18, int(w * 0.11)), True), fill="white", anchor="mm")
    # head and screen
    draw.rounded_rectangle((x1 + w * 0.20, y1 + h * 0.12, x1 + w * 0.85, y1 + h * 0.55), radius=int(w * 0.16), fill="white", outline="#8CB6E8", width=4)
    draw.rounded_rectangle((x1 + w * 0.30, y1 + h * 0.24, x1 + w * 0.75, y1 + h * 0.47), radius=int(w * 0.09), fill=NAVY)
    for ex in (0.42, 0.62):
        draw.ellipse((x1 + w * ex - 8, y1 + h * 0.32 - 16, x1 + w * ex + 8, y1 + h * 0.32 + 16), fill="#45F3FF")
    # earphones
    draw.ellipse((x1 + w * 0.12, y1 + h * 0.30, x1 + w * 0.27, y1 + h * 0.46), fill="#BFE6FF", outline=BLUE, width=4)
    draw.ellipse((x1 + w * 0.78, y1 + h * 0.30, x1 + w * 0.93, y1 + h * 0.46), fill="#BFE6FF", outline=BLUE, width=4)
    # arm
    if flip:
        draw.line((x1 + w * 0.30, y1 + h * 0.58, x1 + w * 0.12, y1 + h * 0.44), fill="#8CB6E8", width=7)
        draw.ellipse((x1 + w * 0.08, y1 + h * 0.40, x1 + w * 0.16, y1 + h * 0.48), fill="white", outline="#8CB6E8", width=3)
    else:
        draw.line((x1 + w * 0.74, y1 + h * 0.58, x1 + w * 0.92, y1 + h * 0.44), fill="#8CB6E8", width=7)
        draw.ellipse((x1 + w * 0.88, y1 + h * 0.40, x1 + w * 0.96, y1 + h * 0.48), fill="white", outline="#8CB6E8", width=3)


def comic_panel(draw, num, heading, body, box, accent=BLUE):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=20, fill=(248, 251, 255), outline=BLUE, width=3)
    draw.rounded_rectangle((x1 + 1, y1 + 1, x2 - 1, y1 + 75), radius=18, fill="#DDEBFF", outline=BLUE, width=2)
    circle_num(draw, num, (x1 + 52, y1 + 38), accent=accent, r=30)
    draw.text((x1 + 98, y1 + 20), heading, font=font(33, True), fill=NAVY)
    draw_wrapped(draw, body, (x1 + 28, y2 - 70), x2 - x1 - 56, font(26, True), fill=NAVY, line_gap=6, max_lines=2, align="center")


def mini_doc_card(draw, title_txt, body, box, accent=BLUE, kind="doc"):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=18, fill="white", outline="#9DBCF0", width=3)
    if kind == "check":
        draw.ellipse((x1 + 22, y1 + 25, x1 + 72, y1 + 75), fill=LIGHT_TEAL, outline=TEAL, width=3)
        draw.line((x1 + 35, y1 + 52, x1 + 47, y1 + 63, x1 + 64, y1 + 38), fill=TEAL, width=6)
    elif kind == "table":
        draw.rounded_rectangle((x1 + 22, y1 + 22, x1 + 76, y1 + 76), radius=8, fill=LIGHT_ORANGE, outline=ORANGE, width=3)
        for dx in (40, 58):
            draw.line((x1 + dx, y1 + 24, x1 + dx, y1 + 74), fill=ORANGE, width=2)
        for dy in (40, 58):
            draw.line((x1 + 24, y1 + dy, x1 + 74, y1 + dy), fill=ORANGE, width=2)
    elif kind == "timeline":
        draw.line((x1 + 26, y1 + 56, x1 + 82, y1 + 56), fill=accent, width=5)
        for i, c in enumerate((BLUE, TEAL, ORANGE)):
            px = x1 + 32 + i * 23
            draw.ellipse((px - 8, y1 + 48, px + 8, y1 + 64), fill=c, outline="white", width=2)
    else:
        draw.rounded_rectangle((x1 + 25, y1 + 22, x1 + 75, y1 + 78), radius=7, fill=LIGHT_BLUE, outline=BLUE, width=3)
        draw.line((x1 + 36, y1 + 42, x1 + 64, y1 + 42), fill=BLUE, width=3)
        draw.line((x1 + 36, y1 + 56, x1 + 64, y1 + 56), fill=BLUE, width=3)
    draw.text((x1 + 96, y1 + 22), title_txt, font=font(29, True), fill=accent)
    draw_wrapped(draw, body, (x1 + 96, y1 + 64), x2 - x1 - 118, font(20), fill=NAVY, line_gap=5, max_lines=2)


def comic_flow_step(draw, num, title_txt, box, accent=BLUE):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=22, fill="white", outline=accent, width=3)
    circle_num(draw, num, (x1 + 45, y1 + 45), accent=accent, r=32)
    draw.text((x1 + 92, y1 + 20), title_txt, font=font(34, True), fill=accent)


def draw_logic_board(draw, box, accent=BLUE):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    rounded(draw, box, radius=24, fill="#F7FBFF", outline=BLUE, width=4)
    draw.rounded_rectangle((x1 + 18, y1 + 18, x2 - 18, y1 + 70), radius=14, fill=BLUE, outline=BLUE)
    draw.text((x1 + 44, y1 + 30), "反推逻辑演示舱", font=font(26 if w > 420 else 22, True), fill="white")
    if w < 420:
        labels = [("SW1", BLUE), ("L2", TEAL), ("L3", ORANGE), ("L4", PURPLE)]
        y = y1 + h * 0.55
        last_x = None
        for i, (label, col) in enumerate(labels):
            cx = x1 + 55 + i * ((w - 110) / 3)
            if last_x is not None:
                draw.line((last_x + 26, y, cx - 26, y), fill="#8CB6E8", width=5)
            draw.ellipse((cx - 27, y - 27, cx + 27, y + 27), fill="white", outline=col, width=4)
            draw.text((cx, y - 2), label, font=font(17, True), fill=col, anchor="mm")
            last_x = cx
        return
    nodes = [
        ("SW1", x1 + w * 0.14, y1 + h * 0.33, BLUE),
        ("L1", x1 + w * 0.29, y1 + h * 0.33, TEAL),
        ("TLS", x1 + w * 0.44, y1 + h * 0.33, PURPLE),
        ("SW2", x1 + w * 0.59, y1 + h * 0.33, BLUE),
        ("L2", x1 + w * 0.76, y1 + h * 0.33, TEAL),
        ("540V", x1 + w * 0.14, y1 + h * 0.62, ORANGE),
        ("L3", x1 + w * 0.34, y1 + h * 0.62, TEAL),
        ("PDU", x1 + w * 0.54, y1 + h * 0.62, PURPLE),
        ("VDT90", x1 + w * 0.74, y1 + h * 0.62, ORANGE),
        ("L4", x1 + w * 0.91, y1 + h * 0.62, TEAL),
    ]
    for i in range(len(nodes) - 1):
        if i == 4:
            continue
        _, ax, ay, _ = nodes[i]
        _, bx, by, _ = nodes[i + 1]
        draw.line((ax + 38, ay, bx - 38, by), fill="#8CB6E8", width=5)
    draw.line((nodes[4][1], nodes[4][2] + 34, nodes[5][1], nodes[5][2] - 34), fill="#8CB6E8", width=5)
    for label, cx, cy, col in nodes:
        draw.rounded_rectangle((cx - 42, cy - 28, cx + 42, cy + 28), radius=15, fill="white", outline=col, width=4)
        draw.text((cx, cy - 2), label, font=font(19, True), fill=col, anchor="mm")
    draw.rounded_rectangle((x1 + 58, y2 - 70, x2 - 58, y2 - 24), radius=16, fill=LIGHT_TEAL, outline=TEAL, width=3)
    draw.text((x1 + 86, y2 - 58), "结果摘要：Active / Blocked / Evidence 同屏联动", font=font(22, True), fill=NAVY)


def draw_timeline_board(draw, box):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    rounded(draw, box, radius=24, fill="#F7FBFF", outline=ORANGE, width=4)
    draw.rounded_rectangle((x1 + 18, y1 + 18, x2 - 18, y1 + 70), radius=14, fill=ORANGE, outline=ORANGE)
    draw.text((x1 + 44, y1 + 30), "时间—指令 / 状态表", font=font(26, True), fill="white")
    if w < 360 or h < 230:
        y = y1 + 115
        draw.line((x1 + 48, y, x2 - 48, y), fill="#9DBCF0", width=7)
        for i, (t, col) in enumerate((("0s", BLUE), ("1.2s", TEAL), ("5s", ORANGE))):
            cx = x1 + 58 + i * ((w - 116) / 2)
            draw.ellipse((cx - 20, y - 20, cx + 20, y + 20), fill=col, outline="white", width=3)
            draw.text((cx, y + 33), t, font=font(17, True), fill=NAVY, anchor="ma")
        return
    rows = [
        ("0.0s", "start_deploy_sequence", BLUE),
        ("1.2s", "set_input: TRA", TEAL),
        ("2.4s", "inject_fault: SW1", ORANGE),
        ("5.0s", "assert_condition", PURPLE),
    ]
    y = y1 + 88
    row_gap = 50 if h < 280 else 58
    for t, txt, col in rows:
        draw.rounded_rectangle((x1 + 42, y, x1 + 132, y + 38), radius=12, fill="white", outline=col, width=3)
        draw.text((x1 + 87, y + 9), t, font=font(19, True), fill=col, anchor="ma")
        draw.rounded_rectangle((x1 + 155, y, x2 - 42, y + 38), radius=12, fill="white", outline="#BFD3F4", width=2)
        draw.text((x1 + 176, y + 9), txt, font=font(20, True), fill=NAVY)
        y += row_gap
    draw.line((x2 - 315, y1 + 104, x2 - 315, y2 - 46), fill="#9DBCF0", width=5)
    for i, (label, col) in enumerate((("L1", BLUE), ("L2", TEAL), ("L3", ORANGE), ("L4", PURPLE))):
        bx = x2 - 280 + i * 62
        draw.rounded_rectangle((bx, y2 - 115, bx + 46, y2 - 42), radius=16, fill=col, outline=col)
        draw.text((bx + 23, y2 - 78), label, font=font(18, True), fill="white", anchor="mm")


def page_demo_overview():
    img, d = base_page()
    title(d, "第六页：现在样板，", "现场能演示什么？", y=45, size=76)
    subtitle(d, "把前面讲的目标，落到 4 个现场能点开、能复跑、能讲清的 Demo。", y=152, x=285, w=1100)
    panels = [
        (1, "拉杆一动", "TRA / VDT / RA / N1K 条件联动", (25, 232, 410, 705), BLUE),
        (2, "逻辑主板", "SW1 到 L4、THR_LOCK 一屏读懂", (430, 232, 815, 705), TEAL),
        (3, "时间脚本", "正常、阻塞、故障注入可复跑", (835, 232, 1220, 705), ORANGE),
        (4, "证据归档", "诊断 trace 与知识包可留存", (1240, 232, 1647, 705), PURPLE),
    ]
    for num, head, body, box, accent in panels:
        comic_panel(d, num, head, body, box, accent)
    paste_template_crop(img, 2, (70, 305, 405, 665), (55, 352, 282, 625), transparent_white=True)
    draw_logic_board(d, (470, 338, 775, 610), accent=TEAL)
    draw_timeline_board(d, (875, 338, 1180, 610))
    mini_doc_card(d, "归档证据", "Answer / Outcome / Bundle", (1278, 356, 1608, 475), PURPLE, kind="check")
    mini_doc_card(d, "复验入口", "CLI、HTTP smoke、页面测试", (1278, 505, 1608, 624), BLUE, kind="timeline")
    paste_template_crop(img, 3, (485, 405, 730, 760), (150, 710, 310, 920), transparent_white=True)
    big_bottom_line(d, "一句话：不是新增几张页面，而是补上领导能看、工程师能验的现场演示链。", (360, 748, 1320, 908), accent=ORANGE)
    return img


def page_fantui_cockpit():
    img, d = base_page()
    title(d, "第七页：反推逻辑演示舱，", "拉杆一动就讲清", y=45, size=76)
    subtitle(d, "把 C919 反推控制链，做成可拖动、可解释、可复验的第一页演示。", y=152, x=300, w=1080)
    rounded(d, (105, 272, 455, 725), radius=24, fill="#F8FBFF", outline=BLUE, width=4)
    d.rounded_rectangle((135, 250, 425, 318), radius=18, fill=BLUE, outline=BLUE)
    d.text((185, 267), "输入：现场拉杆", font=font(32, True), fill="white")
    mini_doc_card(d, "TRA 反推杆", "支持 -32° 到 0° 拉杆区间", (135, 350, 425, 445), BLUE, kind="timeline")
    mini_doc_card(d, "条件面板", "RA、发动机、地面、抑制、N1K", (135, 470, 425, 565), TEAL, kind="check")
    mini_doc_card(d, "VDT 反馈", "自动/手动反馈边界讲清", (135, 590, 425, 685), ORANGE, kind="table")
    draw_lever_art(img, (480, 255, 780, 650))
    paste_template_crop(img, 3, (485, 405, 730, 760), (675, 405, 900, 710), transparent_white=True)
    right_arrow(d, 820, 540, 900, BLUE)
    draw_logic_board(d, (905, 275, 1555, 655), accent=TEAL)
    comic_caption(d, "拉一下杆，界面同步亮出 SW1 / L1 / L2 / L3 / L4 和 THR_LOCK 的状态。", (900, 680, 1560, 755), TEAL)
    speech(d, "以前要翻控制律和测试记录，现在先看一眼链路，再追证据。", (270, 785, 1410, 920), fill="white")
    return img


def page_c919_workstation():
    img, d = base_page()
    title(d, "第八页：C919 E-TRAS 工作台，", "证明平台可推广", y=45, size=70)
    subtitle(d, "同一套工作台接入 C919 E-TRAS 冻结参考引擎，避免每个系统重做规则。", y=152, x=270, w=1130)
    cols = [
        (1, "选系统", "C919 反推控制逻辑需求文档", (75, 318, 495, 720), BLUE),
        (2, "接样板", "冻结参考引擎 + 12 步 tick 推进", (625, 318, 1045, 720), TEAL),
        (3, "可复制", "同一时间脚本驱动多套控制逻辑", (1175, 318, 1595, 720), ORANGE),
    ]
    for num, head, body, box, accent in cols:
        comic_flow_step(d, num, head, (box[0], 298, box[2], 365), accent)
        rounded(d, box, radius=22, fill="#F8FBFF", outline=BLUE, width=4)
        draw_wrapped(d, body, (box[0] + 36, box[3] - 92), box[2] - box[0] - 72, font(28, True), fill=NAVY, line_gap=8, align="center")
    paste_template_crop(img, 4, (120, 355, 455, 600), (145, 390, 420, 600), transparent_white=True)
    mini_doc_card(d, "冻结参考引擎", "12 步状态推进；不改主控制真值", (675, 380, 995, 472), TEAL, kind="check")
    mini_doc_card(d, "工作台接口", "同一 payload 进入仿真与诊断", (675, 500, 995, 592), BLUE, kind="doc")
    mini_doc_card(d, "双系统预设", "两套场景可切换", (675, 620, 995, 704), ORANGE, kind="timeline")
    paste_template_crop(img, 4, (1080, 385, 1495, 620), (1225, 395, 1538, 590), transparent_white=True)
    d.line((502, 508, 620, 508), fill=BLUE, width=10)
    d.polygon([(620, 508), (575, 478), (575, 538)], fill=BLUE)
    d.line((1050, 508, 1168, 508), fill=TEAL, width=10)
    d.polygon([(1168, 508), (1123, 478), (1123, 538)], fill=TEAL)
    paste_template_crop(img, 3, (485, 405, 730, 760), (1380, 690, 1585, 925), transparent_white=True)
    big_bottom_line(d, "一句话：第一个样板跑通后，第二套控制逻辑能按同一套路接进来。", (315, 765, 1350, 908), accent=TEAL)
    return img


def page_timeline_sim():
    img, d = base_page()
    title(d, "第九页：全流程故障仿真，", "把测试写成脚本", y=45, size=74)
    subtitle(d, "用“时间—指令/状态”表驱动 FANTUI 与 C919，自动生成断言和阻塞证据。", y=152, x=260, w=1160)
    paste_template_crop(img, 5, (0, 330, 360, 740), (0, 360, 290, 775), transparent_white=True)
    d.ellipse((72, 230, 310, 370), fill="white", outline=NAVY, width=3)
    draw_wrapped(d, "测试不再一条条手抄，\n而是写成可复跑脚本。", (110, 270), 170, font(24, True), fill=NAVY, line_gap=7, align="center")
    pts = [(410, 418), (625, 328), (870, 445), (1115, 335), (1360, 430)]
    d.line(pts, fill="#9FB7D8", width=46, joint="curve")
    d.line(pts, fill="white", width=7, joint="curve")
    steps = [
        ("1", "写时间表", BLUE, pts[0]),
        ("2", "跑双系统", TEAL, pts[1]),
        ("3", "注入故障", ORANGE, pts[2]),
        ("4", "查阻塞链", PURPLE, pts[3]),
        ("5", "出证据", BLUE, pts[4]),
    ]
    for n, label, accent, (x, y) in steps:
        d.ellipse((x - 46, y - 70, x + 46, y + 22), fill="white", outline=accent, width=6)
        d.text((x, y - 35), n, font=font(48, True), fill=accent, anchor="mm")
        rounded(d, (x - 120, y + 35, x + 120, y + 100), radius=16, fill="white", outline=accent, width=3)
        d.text((x, y + 52), label, font=font(28, True), fill=accent, anchor="ma")
    draw_timeline_board(d, (450, 535, 1215, 745))
    paste_template_crop(img, 3, (485, 405, 730, 760), (1265, 560, 1510, 830), transparent_white=True)
    speech(d, "同一张脚本表，能跑正常展开、SW1 卡滞、TR inhibited 等场景。", (275, 790, 1420, 920), fill="white")
    return img


def page_monitor_timeline():
    img, d = base_page()
    title(d, "第十页：状态时间线，", "把过程证据讲清楚", y=45, size=76)
    subtitle(d, "关键事件、输入、逻辑、电源、传感器、命令，统一落到同一条时间轴。", y=152, x=300, w=1080)
    rounded(d, (1175, 300, 1540, 710), radius=26, fill="#F8FBFF", outline="#9DBCF0", width=3)
    mini_doc_card(d, "输入层", "TRA / VDT / RA", (1205, 340, 1510, 425), BLUE, kind="timeline")
    mini_doc_card(d, "逻辑层", "SW1 - L4", (1205, 465, 1510, 550), TEAL, kind="check")
    mini_doc_card(d, "命令层", "EEC / PDU / LOCK", (1205, 590, 1510, 675), ORANGE, kind="doc")
    rounded(d, (145, 275, 1110, 710), radius=28, fill="#F8FBFF", outline=BLUE, width=4)
    d.rounded_rectangle((175, 300, 1080, 360), radius=16, fill=BLUE, outline=BLUE)
    d.text((210, 315), "Timeline Outcome：过程不是黑盒", font=font(34, True), fill="white")
    baseline_y = 555
    d.line((225, baseline_y, 1030, baseline_y), fill="#9DBCF0", width=8)
    events = [
        ("0s", "TRA", BLUE, 245, 455),
        ("1.2s", "SW1", TEAL, 390, 500),
        ("2.0s", "L2", ORANGE, 535, 440),
        ("3.6s", "540V", PURPLE, 680, 495),
        ("5.0s", "VDT90", TEAL, 825, 430),
        ("7.0s", "THR_LOCK", ORANGE, 980, 495),
    ]
    for t, label, accent, x, y in events:
        d.line((x, baseline_y, x, y + 52), fill=accent, width=5)
        d.ellipse((x - 26, baseline_y - 26, x + 26, baseline_y + 26), fill=accent, outline="white", width=4)
        rounded(d, (x - 62, y, x + 62, y + 58), radius=15, fill="white", outline=accent, width=3)
        d.text((x, y + 13), label, font=font(21, True), fill=accent, anchor="ma")
        d.text((x, baseline_y + 45), t, font=font(20, True), fill=NAVY, anchor="ma")
    mini_doc_card(d, "怎么读", "看节点何时变绿、何时阻塞", (280, 620, 565, 700), BLUE, kind="timeline")
    mini_doc_card(d, "怎么查", "按输入、逻辑、电源、传感器定位", (600, 620, 1035, 700), TEAL, kind="check")
    paste_template_crop(img, 3, (485, 405, 730, 760), (35, 650, 210, 900), transparent_white=True)
    speech(d, "它不是只告诉你结果，而是把结果怎么来的也摊开。", (315, 790, 1305, 920), fill="white")
    return img


def page_closure():
    img, d = base_page()
    title(d, "第十一页：从样板到平台，", "证据闭环跑通", y=45, size=76)
    subtitle(d, "一期拿到的不是概念页，而是可操作 Demo、可复跑测试和可归档证据。", y=152, x=285, w=1100)
    cards = [
        ("演示可操作", "拉杆 cockpit、条件面板、逻辑主板", (190, 248, 605, 440), TEAL, "timeline"),
        ("能力可复制", "FANTUI + C919 双系统仿真", (625, 248, 1020, 440), BLUE, "adapter"),
        ("证据可归档", "诊断 trace、知识包、bundle/archive", (1040, 248, 1435, 440), PURPLE, "doc"),
    ]
    for title_txt, body, box, accent, kind in cards:
        rounded(d, box, radius=26, fill="white", outline=accent, width=3)
        d.ellipse((box[0] + 35, box[1] + 35, box[0] + 115, box[1] + 115), fill="#EEF6FF", outline=accent, width=3)
        icon_kind = "monitor" if kind == "doc" else kind
        icon(d, icon_kind, (box[0] + 38, box[1] + 38, box[0] + 112, box[1] + 112), accent)
        d.text((box[0] + 145, box[1] + 42), title_txt, font=font(38, True), fill=accent)
        draw_wrapped(d, body, (box[0] + 145, box[1] + 95), box[2] - box[0] - 170, font(25, True), fill=NAVY, line_gap=7, max_lines=2)
    paste_template_crop(img, 6, (310, 450, 1055, 735), (445, 435, 1035, 675), transparent_white=True)
    rounded(d, (330, 710, 1340, 800), radius=28, fill="white", outline="#9DBCF0", width=3)
    flow = [("一期样板", TEAL), ("平台主体", BLUE), ("企业级推广", PURPLE)]
    for i, (txt, accent) in enumerate(flow):
        x = 400 + i * 315
        d.ellipse((x, 724, x + 62, 786), fill=LIGHT_TEAL if accent == TEAL else LIGHT_BLUE, outline=accent, width=4)
        d.text((x + 31, 755), str(i + 1), font=font(29, True), fill=accent, anchor="mm")
        d.text((x + 82, 735), txt, font=font(29, True), fill=accent)
        if i < 2:
            right_arrow(d, x + 245, 754, x + 320, BLUE)
    rounded(d, (190, 812, 1480, 922), radius=42, fill=ORANGE, outline="#FFD2A6", width=5)
    d.ellipse((230, 835, 295, 900), fill="white", outline="white")
    d.line((245, 867, 258, 882, 282, 847), fill=ORANGE, width=9, joint="curve")
    draw_wrapped(d, "本次建议：支持一期立项，先把样板平台做扎实。", (330, 835), 1065, font(42, True), fill="white", align="center", line_gap=8)
    return img


def progress_chip(draw, text, box, accent=BLUE, fill="white", size=25):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=20, fill=fill, outline=accent, width=3)
    draw.ellipse((x1 + 18, y1 + 16, x1 + 58, y1 + 56), fill=accent, outline=accent)
    draw.line((x1 + 30, y1 + 38, x1 + 39, y1 + 47, x1 + 53, y1 + 27), fill="white", width=6, joint="curve")
    draw_wrapped(draw, text, (x1 + 75, y1 + 17), x2 - x1 - 92, font(size, True), fill=NAVY, line_gap=5, max_lines=2)


def big_metric(draw, number, label, box, accent=ORANGE):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=28, fill="white", outline=accent, width=4)
    draw.text((x1 + 34, y1 + 18), number, font=font(58, True), fill=accent)
    draw_wrapped(draw, label, (x1 + 38, y1 + 92), x2 - x1 - 76, font(25, True), fill=NAVY, line_gap=7, max_lines=2)


def screen_shell(draw, box, title_txt, accent=BLUE):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=26, fill="#F8FBFF", outline=accent, width=4)
    draw.rounded_rectangle((x1 + 18, y1 + 18, x2 - 18, y1 + 76), radius=16, fill=accent, outline=accent)
    draw.text((x1 + 48, y1 + 32), title_txt, font=font(30, True), fill="white")


def mini_status(draw, label, value, xy, accent=BLUE):
    x, y = xy
    rounded(draw, (x, y, x + 185, y + 64), radius=18, fill="white", outline=accent, width=3)
    draw.text((x + 18, y + 10), label, font=font(18, True), fill=GRAY)
    draw.text((x + 18, y + 31), value, font=font(27, True), fill=accent)


def metric_stamp(draw, number, label, box, accent=BLUE):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=28, fill="white", outline=accent, width=4)
    draw.text(((x1 + x2) // 2, y1 + 50), number, font=font(56, True), fill=accent, anchor="mm")
    draw_wrapped(draw, label, (x1 + 24, y1 + 105), x2 - x1 - 48, font(24, True), fill=NAVY, line_gap=5, max_lines=2, align="center")


def draw_demo_screen(draw, box):
    screen_shell(draw, box, "反推逻辑演示舱：同屏读状态", BLUE)
    x1, y1, x2, y2 = box
    draw_lever_art_base = (x1 + 45, y1 + 105, x1 + 265, y1 + 305)
    draw.arc((draw_lever_art_base[0] + 25, draw_lever_art_base[1] + 25, draw_lever_art_base[2] - 25, draw_lever_art_base[3] + 15), 190, 340, fill=BLUE, width=13)
    draw.line((x1 + 140, y1 + 265, x1 + 230, y1 + 155), fill=BLUE, width=18)
    draw.ellipse((x1 + 205, y1 + 118, x1 + 260, y1 + 173), fill=ORANGE, outline="#B84900", width=4)
    draw.rounded_rectangle((x1 + 80, y1 + 285, x1 + 255, y1 + 315), radius=12, fill=LIGHT_BLUE, outline=BLUE, width=4)
    board = (x1 + 315, y1 + 105, x2 - 45, y1 + 325)
    draw_logic_board(draw, board, accent=TEAL)
    progress_chip(draw, "DemoAnswer：问题、命中节点、证据片段", (x1 + 50, y2 - 108, x1 + 430, y2 - 36), TEAL, size=21)
    progress_chip(draw, "lever-snapshot：拉杆与反馈快照", (x1 + 465, y2 - 108, x2 - 50, y2 - 36), ORANGE, size=21)


def draw_timeline_module(draw, box):
    screen_shell(draw, box, "Timeline Simulator：时间表驱动双系统", ORANGE)
    x1, y1, x2, y2 = box
    events = [("set_input", BLUE), ("ramp_input", TEAL), ("inject_fault", ORANGE), ("assert", PURPLE)]
    y = y1 + 105
    for i, (name, accent) in enumerate(events):
        draw.rounded_rectangle((x1 + 48, y, x1 + 208, y + 48), radius=14, fill="white", outline=accent, width=3)
        draw.text((x1 + 68, y + 13), name, font=font(20, True), fill=accent)
        draw.line((x1 + 220, y + 24, x2 - 265, y + 24), fill="#9DBCF0", width=5)
        draw.ellipse((x2 - 245, y + 5, x2 - 205, y + 45), fill=accent, outline="white", width=4)
        y += 60
    for j, (sys, accent) in enumerate((("FANTUI", TEAL), ("C919", BLUE))):
        rounded(draw, (x2 - 190, y1 + 105 + j * 95, x2 - 55, y1 + 170 + j * 95), radius=18, fill="white", outline=accent, width=3)
        draw.text((x2 - 122, y1 + 122 + j * 95), sys, font=font(24, True), fill=accent, anchor="ma")
    progress_chip(draw, "4 个预设 + 自定义", (x1 + 58, y2 - 108, x1 + 385, y2 - 36), BLUE, size=21)
    progress_chip(draw, "/api/timeline-simulate 已接入", (x1 + 425, y2 - 108, x2 - 55, y2 - 36), TEAL, size=21)


def draw_pipeline_chain(draw, box):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=30, fill="#F8FBFF", outline=BLUE, width=4)
    steps = [
        ("需求", BLUE),
        ("Adapter Truth", TEAL),
        ("Playback", ORANGE),
        ("Diagnosis", PURPLE),
        ("Knowledge", GREEN),
        ("Bundle", BLUE),
    ]
    available = x2 - x1 - 120
    gap = available / (len(steps) - 1)
    y = y1 + 160
    for i, (txt, accent) in enumerate(steps):
        cx = x1 + 60 + i * gap
        if i:
            draw.line((x1 + 60 + (i - 1) * gap + 48, y, cx - 48, y), fill="#9DBCF0", width=9)
            draw.polygon([(cx - 47, y), (cx - 82, y - 22), (cx - 82, y + 22)], fill="#9DBCF0")
        draw.ellipse((cx - 50, y - 50, cx + 50, y + 50), fill="white", outline=accent, width=6)
        draw.text((cx, y - 8), str(i + 1), font=font(43, True), fill=accent, anchor="mm")
        draw_wrapped(draw, txt, (int(cx - 78), y + 70), 156, font(22, True), fill=NAVY, line_gap=5, align="center")


def page_demo_overview():
    img, d = base_page()
    title(d, "第六页：当前进度，", "已经跑出工程样板", y=45, size=76)
    subtitle(d, "从“想法可讲”推进到“Demo 可点、双系统可跑、证据可复验”。", y=152, x=300, w=1070)
    paste_template_crop(img, 3, (485, 405, 730, 760), (55, 455, 265, 735), transparent_white=True)
    screen_shell(d, (300, 245, 1040, 690), "当前已交付能力看板", BLUE)
    metric_stamp(d, "765", "tests green", (335, 345, 550, 530), TEAL)
    metric_stamp(d, "4 PR", "timeline 交付", (570, 345, 785, 530), ORANGE)
    metric_stamp(d, "2 系统", "同台验证", (805, 345, 1005, 530), BLUE)
    progress_chip(d, "反推逻辑演示舱：拉杆、条件面板、逻辑主板", (335, 570, 660, 645), BLUE, size=21)
    progress_chip(d, "C919 E-TRAS：冻结参考引擎已合入", (690, 570, 1000, 645), TEAL, size=21)
    rounded(d, (1080, 245, 1585, 690), radius=30, fill="#F8FBFF", outline=ORANGE, width=4)
    d.rounded_rectangle((1110, 275, 1555, 335), radius=16, fill=ORANGE, outline=ORANGE)
    d.text((1145, 290), "现在可以现场展示什么？", font=font(31, True), fill="white")
    bullets = [
        ("1", "拉杆触发 L1-L4 / THR_LOCK"),
        ("2", "FANTUI 与 C919 双执行器"),
        ("3", "时间脚本跑正常与故障"),
        ("4", "trace / knowledge / bundle 留证"),
    ]
    for i, (n, text) in enumerate(bullets):
        y = 365 + i * 72
        circle_num(d, n, (1135, y + 22), [BLUE, TEAL, ORANGE, PURPLE][i], r=24)
        d.text((1180, y + 4), text, font=font(25, True), fill=NAVY)
    big_bottom_line(d, "一句话：现在汇报的重点应从“平台设想”转为“已跑通的工程证据”。", (315, 752, 1395, 912), accent=ORANGE)
    return img


def page_fantui_cockpit():
    img, d = base_page()
    title(d, "第七页：反推逻辑演示舱，", "拉杆一动就讲清", y=45, size=76)
    subtitle(d, "现场拖动反推杆，逻辑链、阻塞原因和证据摘要同步变化。", y=152, x=330, w=1010)
    draw_demo_screen(d, (135, 255, 1265, 720))
    rounded(d, (1295, 255, 1585, 720), radius=28, fill="white", outline=TEAL, width=4)
    d.text((1330, 292), "真实进展", font=font(38, True), fill=TEAL)
    progress_chip(d, "demo API", (1325, 365, 1560, 430), BLUE, size=22)
    progress_chip(d, "lever API", (1325, 455, 1560, 520), TEAL, size=22)
    progress_chip(d, "preset 覆盖", (1325, 545, 1560, 610), ORANGE, size=22)
    progress_chip(d, "smoke 覆盖", (1325, 635, 1560, 700), PURPLE, size=22)
    speech(d, "这页要让领导看到：不是静态图，而是输入一变，控制链立即给出可解释结果。", (330, 782, 1435, 918), fill="white")
    return img


def page_c919_workstation():
    img, d = base_page()
    title(d, "第八页：C919 E-TRAS，", "第二套系统已接入", y=45, size=76)
    subtitle(d, "C919 frozen_v1 参考引擎已合入，证明平台不只服务一个反推样板。", y=152, x=290, w=1110)
    rounded(d, (70, 285, 425, 690), radius=28, fill="#F8FBFF", outline=BLUE, width=4)
    paste_template_crop(img, 4, (120, 355, 455, 600), (105, 350, 390, 565), transparent_white=True)
    d.text((248, 585), "C919 控制逻辑\n需求基线", font=font(33, True), fill=NAVY, anchor="ma")
    right_arrow(d, 445, 485, 565, BLUE)
    screen_shell(d, (585, 285, 1085, 690), "冻结参考引擎 + 工作台接口", TEAL)
    progress_chip(d, "C919ReverseThrustSystem", (630, 375, 1038, 445), TEAL, size=22)
    progress_chip(d, "12-step tick 状态推进", (630, 470, 1038, 540), ORANGE, size=22)
    progress_chip(d, "9191 面板 / API 可运行", (630, 565, 1038, 635), BLUE, size=22)
    right_arrow(d, 1110, 485, 1230, TEAL)
    rounded(d, (1245, 285, 1605, 690), radius=28, fill="#F8FBFF", outline=ORANGE, width=4)
    paste_template_crop(img, 4, (1080, 385, 1495, 620), (1290, 365, 1565, 545), transparent_white=True)
    d.text((1425, 595), "同一套脚本\n驱动多系统", font=font(33, True), fill=NAVY, anchor="ma")
    paste_template_crop(img, 3, (485, 405, 730, 760), (1365, 670, 1588, 925), transparent_white=True)
    big_bottom_line(d, "一句话：第二套控制逻辑已经不是规划项，而是能进入同一工作台的工程事实。", (265, 750, 1355, 912), accent=TEAL)
    return img


def page_timeline_sim():
    img, d = base_page()
    title(d, "第九页：全流程故障仿真，", "已按 4 PR 交付", y=45, size=76)
    subtitle(d, "时间表驱动 FANTUI 与 C919，自动产出断言、时间线和故障阻塞证据。", y=152, x=295, w=1100)
    paste_template_crop(img, 3, (485, 405, 730, 760), (40, 440, 260, 735), transparent_white=True)
    draw_timeline_module(d, (315, 245, 1335, 710))
    rounded(d, (1370, 245, 1605, 710), radius=28, fill="white", outline=BLUE, width=4)
    d.text((1400, 285), "交付结构", font=font(34, True), fill=BLUE)
    for i, item in enumerate(["Engine", "FANTUI Exec", "C919 Exec", "UI + presets"]):
        y = 358 + i * 75
        circle_num(d, i + 1, (1412, y + 20), [BLUE, TEAL, ORANGE, PURPLE][i], r=22)
        d.text((1450, y + 5), item, font=font(22, True), fill=NAVY)
    speech(d, "它把测试从人工表格，推进成可复跑、可比较、可留证的仿真模块。", (310, 780, 1420, 918), fill="white")
    return img


def page_monitor_timeline():
    img, d = base_page()
    title(d, "第十页：证据闭环，", "过程结果都能追", y=45, size=76)
    subtitle(d, "从需求、适配器、回放、诊断到知识包，形成可归档的证据链。", y=152, x=330, w=1010)
    draw_pipeline_chain(d, (130, 260, 1545, 645))
    evidence = [
        ("可复跑日志", "timeline / playback", BLUE),
        ("阻塞 trace", "diagnosis / assertion", TEAL),
        ("知识包归档", "knowledge / bundle", ORANGE),
    ]
    for i, (head, body, accent) in enumerate(evidence):
        x = 225 + i * 405
        rounded(d, (x, 552, x + 330, 622), radius=20, fill="white", outline=accent, width=3)
        d.ellipse((x + 22, 572, x + 62, 612), fill=accent)
        d.line((x + 33, 594, x + 43, 604, x + 57, 581), fill="white", width=6, joint="curve")
        d.text((x + 78, 566), head, font=font(25, True), fill=accent)
        d.text((x + 78, 596), body, font=font(18, False), fill=NAVY)
    progress_chip(d, "playback：复跑场景", (260, 690, 560, 765), BLUE, size=21)
    progress_chip(d, "diagnosis：定位阻塞", (605, 690, 945, 765), TEAL, size=21)
    progress_chip(d, "knowledge：归档结论", (990, 690, 1325, 765), ORANGE, size=21)
    paste_template_crop(img, 3, (485, 405, 730, 760), (40, 690, 190, 910), transparent_white=True)
    big_bottom_line(d, "一句话：平台现在不只展示结果，也能解释结果如何产生、证据如何保存。", (300, 792, 1400, 920), accent=ORANGE)
    return img


def page_closure():
    img, d = base_page()
    title(d, "第十一页：一期立项，", "现在有抓手可以验收", y=45, size=76)
    subtitle(d, "建议支持一期：先把样板平台做扎实，再扩大到更多控制逻辑场景。", y=152, x=310, w=1060)
    rounded(d, (160, 250, 1510, 660), radius=34, fill="#F8FBFF", outline=BLUE, width=4)
    outcomes = [
        ("看得懂", "领导能看懂控制链", BLUE),
        ("跑得通", "双系统仿真可复跑", TEAL),
        ("查得到", "阻塞原因有证据", ORANGE),
        ("留得住", "知识包与归档链路", PURPLE),
    ]
    for i, (head, body, accent) in enumerate(outcomes):
        x = 210 + i * 315
        rounded(d, (x, 310, x + 260, 560), radius=26, fill="white", outline=accent, width=4)
        circle_num(d, i + 1, (x + 58, 365), accent, r=34)
        d.text((x + 115, 342), head, font=font(36, True), fill=accent)
        draw_wrapped(d, body, (x + 35, 440), 190, font(28, True), fill=NAVY, line_gap=8, align="center")
    proof = [
        ("765 tests", "回归绿灯", TEAL),
        ("4 PR", "timeline 已交付", ORANGE),
        ("2 系统", "FANTUI + C919", BLUE),
    ]
    for i, (head, body, accent) in enumerate(proof):
        x = 345 + i * 320
        rounded(d, (x, 585, x + 260, 635), radius=20, fill="white", outline=accent, width=3)
        d.text((x + 28, 594), head, font=font(25, True), fill=accent)
        d.text((x + 132, 598), body, font=font(19, True), fill=NAVY)
    rounded(d, (330, 705, 1340, 792), radius=30, fill="white", outline="#9DBCF0", width=3)
    flow = [("一期样板", TEAL), ("平台主体", BLUE), ("多场景推广", PURPLE)]
    for i, (txt, accent) in enumerate(flow):
        x = 405 + i * 310
        circle_num(d, i + 1, (x, 748), accent, r=32)
        d.text((x + 62, 732), txt, font=font(30, True), fill=accent)
        if i < 2:
            right_arrow(d, x + 225, 748, x + 295, BLUE)
    rounded(d, (190, 815, 1480, 925), radius=42, fill=ORANGE, outline="#FFD2A6", width=5)
    d.ellipse((232, 838, 297, 903), fill="white", outline="white")
    d.line((247, 870, 260, 885, 284, 850), fill=ORANGE, width=9, joint="curve")
    draw_wrapped(d, "本次建议：支持一期立项，把已跑通的样板平台产品化。", (335, 838), 1040, font(40, True), fill="white", align="center", line_gap=8)
    return img


def build_pages():
    template_files = sorted(TEMPLATE_DIR.glob("*.png"))
    pages: list[Path] = []
    for idx, src in enumerate(template_files, start=1):
        im = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
        dst = WORK_DIR / f"page-{idx:02d}.png"
        im.save(dst)
        pages.append(dst)
    builders = [
        page_demo_overview,
        page_fantui_cockpit,
        page_c919_workstation,
        page_timeline_sim,
        page_monitor_timeline,
        page_closure,
    ]
    for i, build in enumerate(builders, start=len(pages) + 1):
        im = build()
        dst = WORK_DIR / f"page-{i:02d}.png"
        im.save(dst, quality=95)
        pages.append(dst)
    return pages


def make_pdf(pages: list[Path]):
    c = canvas.Canvas(str(PDF_OUT), pagesize=(W, H))
    for p in pages:
        c.drawImage(ImageReader(str(p)), 0, 0, width=W, height=H, preserveAspectRatio=False, mask="auto")
        c.showPage()
    c.save()


if __name__ == "__main__":
    pages = build_pages()
    make_pdf(pages)
    MANIFEST.write_text(
        json.dumps({"pdf": str(PDF_OUT), "pages": [str(p) for p in pages], "page_count": len(pages)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(PDF_OUT)
    print(f"pages={len(pages)}")
