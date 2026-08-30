#!/usr/bin/env python3
"""Generate the GitHub profile cover banner."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "cover.png"

# Render at 2x then downsample for a sharp GitHub README banner.
SCALE = 2
W, H = 1600 * SCALE, 520 * SCALE

BG = (8, 9, 12)
INK = (244, 245, 247)
LINE = (36, 40, 52)
ACCENT = (91, 140, 255)
MINT = (62, 224, 177)
AMBER = (245, 196, 110)

FONT_DIR = Path("/usr/share/fonts/truetype/macos")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size * SCALE)


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def add_noise(img: Image.Image, amount: int = 10) -> Image.Image:
    rng = random.Random(7)
    px = img.load()
    w, h = img.size
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            n = rng.randint(-amount, amount)
            r, g, b = px[x, y]
            c = (
                max(0, min(255, r + n)),
                max(0, min(255, g + n)),
                max(0, min(255, b + n)),
            )
            px[x, y] = c
            if x + 1 < w:
                px[x + 1, y] = c
            if y + 1 < h:
                px[x, y + 1] = c
            if x + 1 < w and y + 1 < h:
                px[x + 1, y + 1] = c
    return img


def radial_glow(base: Image.Image, cx: float, cy: float, radius: float, color: tuple[int, int, int], strength: float) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    steps = 36
    for i in range(steps, 0, -1):
        t = i / steps
        a = int(255 * strength * (1 - t) ** 2)
        r = radius * t
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, a))
    base.alpha_composite(overlay)


def rounded_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_grid(draw: ImageDraw.ImageDraw) -> None:
    step = 48 * SCALE
    for x in range(0, W, step):
        draw.line((x, 0, x, H), fill=(*LINE, 70), width=1)
    for y in range(0, H, step):
        draw.line((0, y, W, y), fill=(*LINE, 70), width=1)


def draw_graph(layer: Image.Image) -> None:
    nodes = [
        (1140, 118, "PERCEIVE", ACCENT),
        (1410, 88, "PLAN", MINT),
        (1490, 268, "ACT", AMBER),
        (1206, 348, "MEMORY", ACCENT),
        (1314, 208, "AGENT", INK),
    ]
    nodes = [(x * SCALE, y * SCALE, label, color) for x, y, label, color in nodes]
    edges = [(0, 4), (1, 4), (4, 2), (4, 3), (3, 0), (1, 2)]

    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    draw = ImageDraw.Draw(layer)
    mono = font("JetBrainsMono-Bold.ttf", 14)
    mono_b = font("JetBrainsMono-Bold.ttf", 16)

    for a, b in edges:
        x1, y1, _, c1 = nodes[a]
        x2, y2, _, c2 = nodes[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        nx, ny = (y1 - y2) * 0.12, (x2 - x1) * 0.12
        pts = []
        for i in range(24):
            t = i / 23
            omt = 1 - t
            px = omt * omt * x1 + 2 * omt * t * (mx + nx) + t * t * x2
            py = omt * omt * y1 + 2 * omt * t * (my + ny) + t * t * y2
            pts.append((px, py))
        color = lerp(c1, c2, 0.5)
        gdraw.line(pts, fill=(*color, 70), width=8 * SCALE)
        draw.line(pts, fill=(*color, 170), width=3 * SCALE)

    layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6 * SCALE)))

    for x, y, label, color in nodes:
        core = 24 * SCALE if label == "AGENT" else 14 * SCALE
        halo = core * 3.1
        radial_glow(layer, x, y, halo, color, 0.34 if label == "AGENT" else 0.20)
        draw.ellipse((x - core, y - core, x + core, y + core), fill=(*color, 235 if label == "AGENT" else 215))
        if label == "AGENT":
            inner = 11 * SCALE
            draw.ellipse((x - inner, y - inner, x + inner, y + inner), fill=(*BG, 230))
            tw, _ = text_size(draw, label, mono_b)
            draw.text((x - tw / 2, y + core + 12 * SCALE), label, font=mono_b, fill=(*INK, 245))
        else:
            tw, _ = text_size(draw, label, mono)
            draw.text((x - tw / 2, y + core + 10 * SCALE), label, font=mono, fill=(210, 214, 224, 240))


def draw_chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fnt: ImageFont.FreeTypeFont, accent: tuple[int, int, int]) -> int:
    tw, th = text_size(draw, text, fnt)
    w, h = tw + 42 * SCALE, th + 22 * SCALE
    rounded_rect(
        draw,
        (x, y, x + w, y + h),
        radius=999,
        fill=(16, 18, 26, 220),
        outline=(*accent, 120),
        width=2,
    )
    r = 4 * SCALE
    dx = x + 18 * SCALE
    dy = y + h / 2
    draw.ellipse((dx - r, dy - r, dx + r, dy + r), fill=(*accent, 240))
    draw.text((x + 32 * SCALE, y + 11 * SCALE), text, font=fnt, fill=(*INK, 245))
    return w


def main() -> None:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    radial_glow(img, 360 * SCALE, 200 * SCALE, 520 * SCALE, ACCENT, 0.16)
    radial_glow(img, 1280 * SCALE, 160 * SCALE, 420 * SCALE, MINT, 0.10)
    radial_glow(img, 1100 * SCALE, 400 * SCALE, 360 * SCALE, AMBER, 0.07)

    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_grid(ImageDraw.Draw(grid))
    img.alpha_composite(grid)

    fade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(0, 980 * SCALE):
        a = int(90 * (1 - i / (980 * SCALE)) ** 1.4)
        fd.line((i, 0, i, H), fill=(8, 9, 12, a))
    img.alpha_composite(fade)

    draw_graph(img)

    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 2 * SCALE), fill=(*ACCENT, 90))
    draw.rectangle((0, H - 6 * SCALE, W, H), fill=(*ACCENT, 255))
    draw.rectangle((220 * SCALE, H - 6 * SCALE, 520 * SCALE, H), fill=(*MINT, 255))
    draw.rectangle((520 * SCALE, H - 6 * SCALE, 760 * SCALE, H), fill=(*AMBER, 255))

    inter_b = font("Inter-Bold.ttf", 118)
    inter_m = font("Inter-SemiBold.ttf", 34)
    inter_r = font("Inter-Medium.ttf", 24)
    mono = font("JetBrainsMono-Bold.ttf", 15)
    chip_font = font("JetBrainsMono-Bold.ttf", 15)

    x = 80 * SCALE
    y = 68 * SCALE

    draw.text((x, y), "HALYU  ·  BE A PROBLEM SOLVER", font=mono, fill=(*MINT, 245))
    y += 42 * SCALE
    draw.text((x, y), "YUYMF", font=inter_b, fill=(*INK, 255))
    y += 148 * SCALE
    draw.text((x, y), "AI Agent Engineer", font=inter_m, fill=(*INK, 245))
    y += 46 * SCALE
    draw.text((x, y), "AI Application Researcher", font=inter_r, fill=(196, 202, 214, 240))

    chips = [
        ("Agent Runtime", ACCENT),
        ("LLM Workflows", MINT),
        ("Game AI", AMBER),
    ]
    cx, cy = x, 400 * SCALE
    gap = 16 * SCALE
    for label, color in chips:
        w = draw_chip(draw, cx, cy, label, chip_font, color)
        cx += w + gap

    rgb = img.convert("RGB")
    rgb = add_noise(rgb, amount=2)
    rgb = rgb.resize((W // SCALE, H // SCALE), Image.Resampling.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(OUT, "PNG", optimize=True, compress_level=9)
    print(f"wrote {OUT} {rgb.size} {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
