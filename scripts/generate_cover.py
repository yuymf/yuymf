#!/usr/bin/env python3
"""Generate the Halyu Land–styled GitHub profile cover."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "cover.png"
FONT_DIR = ROOT / "assets" / "fonts"
SYS_SANS = Path("/usr/share/fonts/truetype/macos")

SCALE = 2
W, H = 1600 * SCALE, 520 * SCALE

# Halyu site tokens
DESK = (197, 204, 212)
DEVICE = (232, 224, 208)
DEVICE_DARK = (214, 204, 186)
PAPER = (255, 254, 249)
INK = (44, 40, 36)
MUTED = (138, 128, 120)
ON = (0, 199, 88)
ORANGE = (255, 107, 53)
GOLD = (252, 187, 0)
SKY = (0, 165, 239)
GRASS = (88, 168, 98)
GRASS_DARK = (62, 132, 78)
WATER = (142, 184, 196)
SAND = (232, 210, 168)
PATH = (214, 186, 140)


def sans(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(SYS_SANS / name), size * SCALE)


def serif(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size * SCALE)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def shadow_rect(base: Image.Image, box, radius: int, color=(44, 40, 36, 50), blur: int = 18) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius=radius, fill=color)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur * SCALE)))


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def iso(cx: float, cy: float, x: int, y: int, z: int = 0, tw: int = 22, th: int = 11) -> tuple[float, float]:
    return cx + (x - y) * tw * SCALE, cy + (x + y) * th * SCALE - z * 10 * SCALE


def tile(draw: ImageDraw.ImageDraw, cx, cy, x, y, z, top, left, right, tw=22, th=11, hgt=8) -> None:
    p = iso(cx, cy, x, y, z, tw, th)
    pts = [
        (p[0], p[1] - th * SCALE),
        (p[0] + tw * SCALE, p[1]),
        (p[0], p[1] + th * SCALE),
        (p[0] - tw * SCALE, p[1]),
    ]
    draw.polygon(pts, fill=top)
    if hgt:
        bl = (pts[3][0], pts[3][1] + hgt * SCALE)
        br = (pts[2][0], pts[2][1] + hgt * SCALE)
        bm = (pts[1][0], pts[1][1] + hgt * SCALE)
        draw.polygon([pts[3], pts[2], br, bl], fill=left)
        draw.polygon([pts[2], pts[1], bm, br], fill=right)


def tree(draw: ImageDraw.ImageDraw, px, py) -> None:
    draw.polygon(
        [(px, py - 22 * SCALE), (px + 12 * SCALE, py + 2 * SCALE), (px - 12 * SCALE, py + 2 * SCALE)],
        fill=(46, 120, 64),
    )
    draw.polygon(
        [(px, py - 32 * SCALE), (px + 8 * SCALE, py - 10 * SCALE), (px - 8 * SCALE, py - 10 * SCALE)],
        fill=(72, 150, 82),
    )
    draw.rectangle((px - 2 * SCALE, py + 2 * SCALE, px + 2 * SCALE, py + 10 * SCALE), fill=(110, 78, 48))


def pin(draw: ImageDraw.ImageDraw, px, py, color, label, fnt, dy: int = 6) -> None:
    r = 8 * SCALE
    draw.ellipse((px - r, py - r - 18 * SCALE, px + r, py + r - 18 * SCALE), fill=color)
    draw.polygon(
        [(px, py), (px - 6 * SCALE, py - 12 * SCALE), (px + 6 * SCALE, py - 12 * SCALE)],
        fill=color,
    )
    draw.ellipse(
        (px - 3 * SCALE, py - 21 * SCALE, px + 3 * SCALE, py - 15 * SCALE),
        fill=(255, 254, 249),
    )
    tw, th = text_size(draw, label, fnt)
    tx, ty = px - tw / 2, py + dy * SCALE
    rounded(draw, (tx - 6 * SCALE, ty - 2 * SCALE, tx + tw + 6 * SCALE, ty + th + 4 * SCALE), 8 * SCALE, PAPER)
    draw.text((tx, ty), label, font=fnt, fill=INK)


def draw_land(layer: Image.Image, origin: tuple[int, int]) -> None:
    draw = ImageDraw.Draw(layer)
    cx, cy = origin
    tiles = {
        (0, 0): "g", (1, 0): "g", (2, 0): "s", (3, 0): "w",
        (0, 1): "g", (1, 1): "p", (2, 1): "g", (3, 1): "s",
        (0, 2): "g", (1, 2): "p", (2, 2): "p", (3, 2): "g",
        (1, 3): "s", (2, 3): "g", (3, 3): "g",
        (-1, 1): "w", (-1, 2): "s",
        (2, -1): "w", (1, -1): "s",
    }
    palette = {
        "g": (GRASS, GRASS_DARK, (52, 118, 70)),
        "p": (PATH, (186, 156, 110), (168, 138, 96)),
        "s": (SAND, (196, 174, 128), (180, 158, 112)),
        "w": (WATER, (110, 154, 168), (96, 140, 156)),
    }
    for (x, y), kind in sorted(tiles.items(), key=lambda t: t[0][0] + t[0][1]):
        top, left, right = palette[kind]
        tile(draw, cx, cy, x, y, 0, top, left, right, hgt=7 if kind != "w" else 3)

    tree(draw, *iso(cx, cy, 0, 0, 1))
    tree(draw, *iso(cx, cy, 0, 2, 1))
    tree(draw, *iso(cx, cy, 3, 3, 1))

    # house
    hx, hy = iso(cx, cy, 2, 0, 1)
    draw.rectangle((hx - 10 * SCALE, hy - 18 * SCALE, hx + 10 * SCALE, hy + 2 * SCALE), fill=(196, 92, 64))
    draw.polygon(
        [(hx - 14 * SCALE, hy - 16 * SCALE), (hx, hy - 30 * SCALE), (hx + 14 * SCALE, hy - 16 * SCALE)],
        fill=(168, 64, 48),
    )

    # agent marker
    ax, ay = iso(cx, cy, 2, 2, 1)
    draw.ellipse((ax - 8 * SCALE, ay - 20 * SCALE, ax + 8 * SCALE, ay - 4 * SCALE), fill=INK)
    draw.ellipse((ax - 5 * SCALE, ay - 26 * SCALE, ax + 5 * SCALE, ay - 16 * SCALE), fill=INK)
    draw.ellipse((ax - 2 * SCALE, ay - 23 * SCALE, ax, ay - 21 * SCALE), fill=PAPER)

    label_f = sans("JetBrainsMono-Bold.ttf", 11)
    pin(draw, *iso(cx, cy, 0, 1, 1), SKY, "PERCEIVE", label_f, dy=-46)
    pin(draw, *iso(cx, cy, 3, 0, 1), ON, "PLAN", label_f, dy=-46)
    pin(draw, *iso(cx, cy, 3, 2, 1), ORANGE, "ACT", label_f, dy=10)
    pin(draw, *iso(cx, cy, 1, 3, 1), GOLD, "MEMORY", label_f, dy=10)


def slot(draw: ImageDraw.ImageDraw, x, y, color, glyph, label, glyph_f, label_f) -> int:
    size = 44 * SCALE
    rounded(draw, (x, y, x + size, y + size), 12 * SCALE, color)
    gw, gh = text_size(draw, glyph, glyph_f)
    draw.text((x + (size - gw) / 2, y + (size - gh) / 2 - 2 * SCALE), glyph, font=glyph_f, fill=PAPER)
    tw, _ = text_size(draw, label, label_f)
    draw.text((x + size + 12 * SCALE, y + 12 * SCALE), label, font=label_f, fill=INK)
    return size + 12 * SCALE + tw


def main() -> None:
    img = Image.new("RGBA", (W, H), (*DESK, 255))
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    step = 28 * SCALE
    for x in range(0, W, step):
        gd.line((x, 0, x, H), fill=(255, 255, 255, 35), width=1)
    for y in range(0, H, step):
        gd.line((0, y, W, y), fill=(255, 255, 255, 35), width=1)
    img.alpha_composite(grid)

    # device
    pad = 36 * SCALE
    device_box = (pad, pad, W - pad, H - pad)
    shadow_rect(img, (pad + 8 * SCALE, pad + 14 * SCALE, W - pad + 8 * SCALE, H - pad + 14 * SCALE), 36 * SCALE, (44, 40, 36, 55), 22)
    draw = ImageDraw.Draw(img)
    rounded(draw, device_box, 36 * SCALE, DEVICE)
    # top lip
    rounded(draw, (pad, pad, W - pad, pad + 92 * SCALE), 36 * SCALE, DEVICE_DARK)
    draw.rectangle((pad, pad + 56 * SCALE, W - pad, pad + 92 * SCALE), fill=DEVICE_DARK)

    # paper
    paper_box = (pad + 18 * SCALE, pad + 84 * SCALE, W - pad - 18 * SCALE, H - pad - 16 * SCALE)
    rounded(draw, paper_box, 18 * SCALE, PAPER)
    # printer slot — the paper feeds from the device lip
    draw.rectangle((pad + 40 * SCALE, pad + 74 * SCALE, W - pad - 40 * SCALE, pad + 86 * SCALE), fill=(72, 66, 58))
    draw.rectangle((pad + 40 * SCALE, pad + 74 * SCALE, W - pad - 40 * SCALE, pad + 77 * SCALE), fill=(120, 112, 102))

    # chrome wordmark + toy avatar
    inter_b = sans("Inter-Bold.ttf", 18)
    mono = sans("JetBrainsMono-Bold.ttf", 12)
    av = (pad + 34 * SCALE, pad + 22 * SCALE)
    draw.ellipse((av[0], av[1], av[0] + 36 * SCALE, av[1] + 36 * SCALE), fill=ORANGE)
    draw.ellipse((av[0] + 10 * SCALE, av[1] + 7 * SCALE, av[0] + 26 * SCALE, av[1] + 22 * SCALE), fill=PAPER)
    draw.ellipse((av[0] + 6 * SCALE, av[1] + 22 * SCALE, av[0] + 30 * SCALE, av[1] + 36 * SCALE), fill=PAPER)
    draw.text((pad + 82 * SCALE, pad + 20 * SCALE), "HALYU LAND", font=inter_b, fill=INK)
    draw.text((pad + 82 * SCALE, pad + 44 * SCALE), "BE A PROBLEM SOLVER", font=mono, fill=MUTED)

    # ON lamp
    lamp_x, lamp_y = W - pad - 78 * SCALE, pad + 34 * SCALE
    draw.ellipse((lamp_x - 7 * SCALE, lamp_y - 7 * SCALE, lamp_x + 7 * SCALE, lamp_y + 7 * SCALE), fill=ON)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((lamp_x - 16 * SCALE, lamp_y - 16 * SCALE, lamp_x + 16 * SCALE, lamp_y + 16 * SCALE), fill=(*ON, 70))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6 * SCALE)))
    draw = ImageDraw.Draw(img)
    draw.text((lamp_x + 14 * SCALE, lamp_y - 8 * SCALE), "ON", font=mono, fill=INK)

    # identity
    title = serif("EBGaramond-Bold.ttf", 92)
    italic = serif("EBGaramond-Italic.ttf", 28)
    role = sans("Inter-SemiBold.ttf", 22)
    chip = sans("Inter-Medium.ttf", 15)
    glyph_f = sans("Inter-Bold.ttf", 18)
    lv_f = sans("JetBrainsMono-Bold.ttf", 13)

    x = pad + 56 * SCALE
    y = pad + 118 * SCALE
    draw.text((x, y), "YUYMF", font=title, fill=INK)

    name_w, _ = text_size(draw, "YUYMF", title)
    lv_box = (x + name_w + 20 * SCALE, y + 38 * SCALE, x + name_w + 158 * SCALE, y + 74 * SCALE)
    rounded(draw, lv_box, 10 * SCALE, INK)
    draw.text((x + name_w + 34 * SCALE, y + 46 * SCALE), "LV. AGENT", font=lv_f, fill=PAPER)

    y += 118 * SCALE
    draw.text((x, y), "AI Agent Engineer", font=italic, fill=INK)
    y += 44 * SCALE
    draw.text((x, y), "AI Application Researcher", font=role, fill=MUTED)

    slots = [
        (ORANGE, "R", "Agent Runtime"),
        (ON, "W", "LLM Workflows"),
        (GOLD, "G", "Game AI"),
    ]
    sx, sy = x, pad + 340 * SCALE
    for color, glyph, label in slots:
        w = slot(draw, sx, sy, color, glyph, label, glyph_f, chip)
        sx += w + 36 * SCALE

    draw_land(img, (1180 * SCALE, 250 * SCALE))

    rng = random.Random(3)
    px = img.load()
    for yy in range(0, H, 3):
        for xx in range(0, W, 3):
            n = rng.randint(-4, 4)
            r, g, b, a = px[xx, yy]
            px[xx, yy] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), a)

    rgb = img.convert("RGB").resize((W // SCALE, H // SCALE), Image.Resampling.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(OUT, "PNG", optimize=True, compress_level=9)
    print(f"wrote {OUT} {rgb.size} {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
