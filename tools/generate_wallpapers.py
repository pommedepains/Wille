#!/usr/bin/env python3
"""Generate Wille's bundled wallpapers: black, white and cyan, chamfered geometry.

The artwork is procedural and original. Run from the repository root:

    python3 tools/generate_wallpapers.py

Output: assets/wallpapers/Wille1.png (also the Hyprlock fallback) and Wille2-4.png.
Requires Pillow and numpy. Output is deterministic.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 3840, 2160
BLACK = (8, 9, 11)
INK = (232, 232, 232)
GREY = (110, 117, 124)
DIM = (45, 50, 55)
CYAN = (30, 200, 240)
BLUE = (21, 89, 162)

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets/fonts/share-tech-mono/ShareTechMono-Regular.ttf"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT), size)


class Canvas:
    """A black canvas with a separate additive glow layer."""

    def __init__(self) -> None:
        self.base = Image.new("RGB", (W, H), BLACK)
        self.glow = Image.new("RGB", (W, H), (0, 0, 0))
        self.d = ImageDraw.Draw(self.base)
        self.g = ImageDraw.Draw(self.glow)

    def line(self, pts, color, width=2, glow=False):
        self.d.line(pts, fill=color, width=width, joint="curve")
        if glow:
            self.g.line(pts, fill=color, width=width + 2, joint="curve")

    def poly(self, pts, outline=None, fill=None, width=2, glow=False):
        if fill is not None:
            self.d.polygon(pts, fill=fill)
        if outline is not None:
            self.line(list(pts) + [pts[0]], outline, width, glow)

    def text(self, xy, s, size, color, anchor="la", glow=False):
        self.d.text(xy, s, font=font(size), fill=color, anchor=anchor)
        if glow:
            self.g.text(xy, s, font=font(size), fill=color, anchor=anchor)

    def finish(self, path: Path, vignette=0.55, grain=2.0, seed=7) -> None:
        glow = self.glow.filter(ImageFilter.GaussianBlur(14))
        wide = self.glow.filter(ImageFilter.GaussianBlur(42))
        img = np.asarray(self.base, dtype=np.float32)
        img += np.asarray(glow, dtype=np.float32) * 0.9 + np.asarray(wide, dtype=np.float32) * 0.7
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        img *= (1.0 - vignette * np.clip(r - 0.35, 0, 1) ** 1.6)[..., None]
        rng = np.random.default_rng(seed)
        img += rng.normal(0, grain, img.shape[:2])[..., None]
        out = np.clip(img, 0, 255).astype(np.uint8)
        Image.fromarray(out, "RGB").save(path, optimize=True)


def chamfer(x0, y0, x1, y1, c):
    """Rectangle with all four corners cut by c pixels."""
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
            (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def hexagon(cx, cy, r, rot=0.0):
    return [(cx + r * math.cos(rot + i * math.pi / 3), cy + r * math.sin(rot + i * math.pi / 3))
            for i in range(6)]


def frame(cv: Canvas, label_l: str, label_r: str, label_b: str) -> None:
    m = 96
    cv.poly(chamfer(m, m, W - m, H - m, 56), outline=DIM, width=2)
    cv.line([(m + 56, m), (m + 420, m)], CYAN, 4, glow=True)
    cv.line([(W - m - 420, H - m), (W - m - 56, H - m)], CYAN, 4, glow=True)
    cv.text((m + 40, m + 36), label_l, 30, GREY)
    cv.text((W - m - 40, m + 36), label_r, 30, GREY, anchor="ra")
    cv.text((m + 40, H - m - 36), label_b, 30, GREY, anchor="ld")


# 1. A.T. field: hexagonal cells radiating from a core --------------------------
def wille1() -> None:
    cv = Canvas()
    rng = random.Random(1)
    cx, cy = W // 2, H // 2 + 20
    size = 74
    dx, dy = size * 1.5, size * math.sqrt(3)
    for col in range(-30, 31):
        for row in range(-20, 21):
            x = cx + col * dx
            y = cy + row * dy + (dy / 2 if col % 2 else 0)
            dist = math.hypot(x - cx, (y - cy) * 1.15)
            if not (0 <= x < W and 0 <= y < H):
                continue
            fade = max(0.0, 1.0 - dist / 1750)
            if fade <= 0.02:
                continue
            lit = rng.random() < 0.05 * fade + 0.01
            tone = int(40 + 90 * fade)
            col_line = CYAN if lit else (tone, int(tone * 1.08), int(tone * 1.16))
            cv.poly(hexagon(x, y, size - 6), outline=col_line, width=3 if lit else 2, glow=lit)
            if lit:
                cv.poly(hexagon(x, y, size - 6), fill=(10, 60, 76))
                cv.poly(hexagon(x, y, size - 6), outline=CYAN, width=3, glow=True)
    # the core: concentric octagonal rings
    for i, r in enumerate((150, 230, 330)):
        ring = [(cx + r * math.cos(math.pi / 8 + k * math.pi / 4), cy + r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
        cv.poly(ring, outline=CYAN if i == 0 else INK, width=4 if i == 0 else 2, glow=(i == 0))
    cv.line([(cx - 520, cy), (cx - 360, cy)], INK, 2)
    cv.line([(cx + 360, cy), (cx + 520, cy)], INK, 2)
    cv.line([(cx, cy - 520), (cx, cy - 360)], INK, 2)
    cv.line([(cx, cy + 360), (cx, cy + 520)], INK, 2)
    frame(cv, "WILLE // NERV-C3", "PATTERN: BLUE", "AT FIELD // PHASE 3I")
    cv.finish(ROOT / "assets/wallpapers/Wille1.png", seed=11)


# 2. MAGI: three chamfered panels in a triangle ---------------------------------
def wille2() -> None:
    cv = Canvas()
    cx, cy = W // 2, H // 2 + 40
    pw, ph, c = 840, 420, 64
    spots = [(cx - 620, cy - 330, "MELCHIOR", "01"), (cx + 620, cy - 330, "BALTHASAR", "02"), (cx, cy + 330, "CASPER", "03")]
    for sx, sy, name, num in spots:
        cv.poly(chamfer(sx - pw // 2, sy - ph // 2, sx + pw // 2, sy + ph // 2, c), fill=(12, 16, 20), outline=CYAN, width=4, glow=True)
        inner = chamfer(sx - pw // 2 + 28, sy - ph // 2 + 28, sx + pw // 2 - 28, sy + ph // 2 - 28, c - 24)
        cv.poly(inner, outline=DIM, width=2)
        cv.text((sx - pw // 2 + 60, sy - ph // 2 + 64), f"MAGI-{num}", 40, INK)
        cv.text((sx - pw // 2 + 60, sy - ph // 2 + 118), name, 30, GREY)
        for i in range(7):
            y = sy - 10 + i * 28
            width = [0.85, 0.55, 0.7, 0.35, 0.9, 0.45, 0.6][i] * (pw - 130)
            cv.line([(sx - pw // 2 + 60, y), (sx - pw // 2 + 60 + width, y)], CYAN if i == 2 else DIM, 3 if i == 2 else 2, glow=(i == 2))
        cv.text((sx + pw // 2 - 60, sy - ph // 2 + 64), "APPROVED" if num != "03" else "STANDBY", 26, CYAN if num != "03" else GREY, anchor="ra")
    # links between panels
    a, b, d = (spots[0][0] + pw // 2, spots[0][1]), (spots[1][0] - pw // 2, spots[1][1]), spots[2]
    cv.line([a, b], INK, 2)
    cv.line([(spots[0][0], spots[0][1] + ph // 2), (spots[0][0], d[1]), (d[0] - pw // 2, d[1])], INK, 2)
    cv.line([(spots[1][0], spots[1][1] + ph // 2), (spots[1][0], d[1]), (d[0] + pw // 2, d[1])], INK, 2)
    for p in ((cx, spots[0][1]), (spots[0][0], d[1]), (spots[1][0], d[1])):
        cv.poly(hexagon(p[0], p[1], 14), fill=CYAN, glow=True)
    frame(cv, "WILLE // NERV-C3", "MAGI LINK", "DELIBERATION 2 OF 3")
    cv.finish(ROOT / "assets/wallpapers/Wille2.png", seed=21)


# 3. Strata: vertical halftone bars with a cyan cut ------------------------------
def wille3() -> None:
    cv = Canvas()
    rng = random.Random(3)
    base_y = int(H * 0.72)
    x = 160
    while x < W - 160:
        bw = rng.choice((18, 26, 40, 64, 96))
        top = base_y - rng.randint(120, 1150) * (1 - abs(x - W / 2) / (W / 2) * 0.6)
        shade = rng.choice((DIM, GREY, INK, DIM, DIM))
        cv.d.rectangle([x, top, x + bw, base_y], fill=tuple(int(v * 0.42) for v in shade))
        cv.line([(x, top), (x + bw, top)], shade, 2)
        x += bw + rng.choice((10, 14, 22))
    cv.line([(0, base_y), (W, base_y)], CYAN, 4, glow=True)
    # slanted cyan cut with chamfered ends
    cut = [(W // 2 - 760, base_y + 40), (W // 2 + 760, base_y + 40), (W // 2 + 700, base_y + 100), (W // 2 - 700, base_y + 100)]
    cv.poly(cut, fill=CYAN, glow=True)
    for i in range(5):
        y = base_y + 170 + i * 46
        w = [1500, 1100, 1300, 700, 960][i]
        cv.line([(W // 2 - w // 2, y), (W // 2 + w // 2, y)], DIM, 2)
    frame(cv, "WILLE // NERV-C3", "TERMINAL 3I", "DEPTH 0xA0 // SEALED")
    cv.finish(ROOT / "assets/wallpapers/Wille3.png", vignette=0.5, seed=31)


# 4. Minimal: horizon and chamfered window -------------------------------------
def wille4() -> None:
    cv = Canvas()
    cx, cy = W // 2, H // 2
    cv.poly(chamfer(cx - 900, cy - 420, cx + 900, cy + 420, 110), outline=INK, width=2)
    cv.poly(chamfer(cx - 860, cy - 380, cx + 860, cy + 380, 92), outline=DIM, width=2)
    cv.line([(cx - 900 + 110, cy - 420), (cx - 300, cy - 420)], CYAN, 6, glow=True)
    cv.line([(cx + 300, cy + 420), (cx + 900 - 110, cy + 420)], CYAN, 6, glow=True)
    cv.line([(0, cy), (cx - 960, cy)], DIM, 2)
    cv.line([(cx + 960, cy), (W, cy)], DIM, 2)
    for i in range(-6, 7):
        h = 28 if i % 3 == 0 else 14
        cv.line([(cx + i * 70, cy - h), (cx + i * 70, cy + h)], GREY if i % 3 else CYAN, 2)
    cv.text((cx, cy + 120), "WILLE", 120, INK, anchor="mm")
    cv.text((cx, cy + 210), "NERV CONTINGENCY SHELL", 34, GREY, anchor="mm")
    frame(cv, "REV 3I", "SYNC 000.0", "STANDBY")
    cv.finish(ROOT / "assets/wallpapers/Wille4.png", vignette=0.6, seed=41)


if __name__ == "__main__":
    (ROOT / "assets/wallpapers").mkdir(parents=True, exist_ok=True)
    for build in (wille1, wille2, wille3, wille4):
        build()
        print("wrote", build.__name__)
