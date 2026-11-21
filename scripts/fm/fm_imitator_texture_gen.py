#!/usr/bin/env python3
"""Genera el set de piel de El Imitador a partir de la referencia.
Solo PIL: no requiere numpy. Salida en assets/art/fm/imitador/.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "art" / "fm" / "imitador"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = 1024
random.seed(20261117)


def noise_layer(size: int, cell: int) -> Image.Image:
    small = Image.new("L", (max(1, size // cell), max(1, size // cell)))
    px = small.load()
    for y in range(small.height):
        for x in range(small.width):
            px[x, y] = random.randint(0, 255)
    return small.resize((size, size), Image.Resampling.BICUBIC).filter(
        ImageFilter.GaussianBlur(cell * 0.35)
    )


def blend(a: Image.Image, b: Image.Image, amount: float) -> Image.Image:
    return Image.blend(a, b, amount)


def make_albedo() -> Image.Image:
    base = Image.new("RGB", (SIZE, SIZE), (82, 52, 46))
    # Mottling: three scales of value noise.
    n1 = noise_layer(SIZE, 64)
    n2 = noise_layer(SIZE, 20)
    n3 = noise_layer(SIZE, 6)
    px = base.load()
    p1, p2, p3 = n1.load(), n2.load(), n3.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = (p1[x, y] - 128) * 0.10 + (p2[x, y] - 128) * 0.08 + (p3[x, y] - 128) * 0.05
            r, g, b = 82 + v * 1.15, 52 + v * 0.82, 46 + v * 0.72
            # Subtle reddish muscle mottling.
            if p2[x, y] > 178:
                r += (p2[x, y] - 178) * 0.28
                g += (p2[x, y] - 178) * 0.06
            px[x, y] = (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))

    # Broad bruised/red patches.
    patch = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(patch)
    for _ in range(22):
        cx, cy = random.randint(0, SIZE), random.randint(0, SIZE)
        rx, ry = random.randint(50, 220), random.randint(35, 170)
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=random.randint(35, 110))
    patch = patch.filter(ImageFilter.GaussianBlur(48))
    red = Image.new("RGB", (SIZE, SIZE), (118, 48, 42))
    base = Image.composite(red, base, patch)

    # Pale sinew streaks and veins.
    draw = ImageDraw.Draw(base, "RGBA")
    for _ in range(70):
        x, y = random.randint(0, SIZE), random.randint(0, SIZE)
        angle = random.uniform(-0.5, 0.5)
        length = random.randint(30, 190)
        points = [(x, y)]
        for step in range(1, 7):
            x += math.cos(angle) * length / 6
            y += math.sin(angle) * length / 6 + random.uniform(-6, 6)
            points.append((x, y))
        color = random.choice([
            (128, 99, 86, random.randint(18, 42)),
            (52, 34, 38, random.randint(22, 55)),
            (150, 110, 92, random.randint(10, 28)),
        ])
        draw.line(points, fill=color, width=random.choice([1, 1, 2]))
    # Fine pores / grime.
    for _ in range(3200):
        x, y = random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)
        v = random.randint(-12, 12)
        r, g, b = base.getpixel((x, y))
        base.putpixel((x, y), (
            max(0, min(255, r + v)),
            max(0, min(255, g + v)),
            max(0, min(255, b + v)),
        ))
    return base.filter(ImageFilter.GaussianBlur(0.6))


def make_roughness() -> Image.Image:
    base = Image.new("L", (SIZE, SIZE), 150)
    n = noise_layer(SIZE, 40)
    n2 = noise_layer(SIZE, 10)
    p, q = n.load(), n2.load()
    px = base.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = 148 + (p[x, y] - 128) * 0.20 + (q[x, y] - 128) * 0.10
            px[x, y] = max(80, min(230, int(v)))
    return base.filter(ImageFilter.GaussianBlur(0.8))


def main() -> None:
    albedo = make_albedo()
    rough = make_roughness()
    albedo.save(OUT / "T_Imitador_Skin_Ref_BC.png")
    rough.save(OUT / "T_Imitador_Skin_Ref_R.png")
    print("IMITATOR_SKIN_TEXTURES", OUT / "T_Imitador_Skin_Ref_BC.png", OUT / "T_Imitador_Skin_Ref_R.png")


if __name__ == "__main__":
    main()
