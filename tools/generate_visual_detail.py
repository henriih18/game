#!/usr/bin/env python3
"""Genera detalle procedural para el pase visual de FRECUENCIA MUERTA.

Texturas originales, reproducibles y sin assets externos:
sangre, agua, suciedad, mano ensangrentada, piel de criatura, hueso y tela.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "art" / "fm"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_fm_art as art  # noqa: E402


def clamp8(v: float) -> int:
    return max(0, min(255, int(v)))


def save_rgba(img: Image.Image, name: str) -> None:
    img.save(OUT / name)


def blood_splat() -> None:
    w = h = 512
    rng = random.Random(4411)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 250, 255
    for _ in range(10):
        rx = rng.randint(55, 150)
        ry = rng.randint(35, 115)
        ox = rng.randint(-70, 70)
        oy = rng.randint(-55, 55)
        d.ellipse((cx + ox - rx, cy + oy - ry, cx + ox + rx, cy + oy + ry),
                  fill=(rng.randint(45, 105), rng.randint(2, 14), rng.randint(2, 10), rng.randint(95, 175)))
    for _ in range(120):
        a = rng.random() * math.tau
        dist = rng.uniform(45, 235)
        x = cx + math.cos(a) * dist
        y = cy + math.sin(a) * dist
        r = rng.uniform(1.5, 10.0)
        d.ellipse((x - r, y - r * rng.uniform(0.5, 1.6), x + r, y + r * rng.uniform(0.5, 1.6)),
                  fill=(rng.randint(35, 95), rng.randint(2, 12), rng.randint(2, 8), rng.randint(90, 210)))
    for _ in range(14):
        a = rng.random() * math.tau
        dist = rng.uniform(50, 150)
        x = cx + math.cos(a) * dist
        y = cy + math.sin(a) * dist
        d.line((cx, cy, x, y), fill=(rng.randint(40, 80), 4, 3, 70), width=rng.randint(2, 6))
    img = img.filter(ImageFilter.GaussianBlur(1.1))
    d = ImageDraw.Draw(img)
    for _ in range(28):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        r = rng.randint(2, 5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(70, 4, 3, rng.randint(160, 235)))
    save_rgba(img, "blood_splat.png")


def blood_trail() -> None:
    w, h = 512, 256
    rng = random.Random(5511)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(7):
        x = 55 + i * 65 + rng.randint(-12, 12)
        y = h // 2 + rng.randint(-25, 25)
        rx = rng.randint(30, 65)
        ry = rng.randint(12, 30)
        d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(72, 3, 3, rng.randint(90, 155)))
    for _ in range(140):
        x = rng.randint(10, w - 10)
        y = rng.randint(30, h - 30)
        r = rng.randint(1, 4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(80, 4, 3, rng.randint(100, 220)))
    img = img.filter(ImageFilter.GaussianBlur(1.8))
    save_rgba(img, "blood_trail.png")


def handprint() -> None:
    w = h = 256
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = (82, 4, 3, 205)
    d.ellipse((74, 96, 182, 210), fill=col)
    fingers = [(82, 92, 106, 48, 100), (108, 86, 132, 30, 92), (134, 90, 160, 34, 94),
               (158, 102, 184, 52, 98), (70, 128, 36, 88, 86)]
    for x0, y0, x1, y1, rr in fingers:
        d.line((x0, y0, x1, y1), fill=col, width=rr)
        d.ellipse((x1 - rr // 2, y1 - rr // 2, x1 + rr // 2, y1 + rr // 2), fill=col)
    for _ in range(35):
        x = random.randint(40, 220)
        y = random.randint(50, 230)
        r = random.randint(1, 4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(70, 3, 2, random.randint(100, 200)))
    img = img.filter(ImageFilter.GaussianBlur(1.0))
    save_rgba(img, "handprint.png")


def puddle() -> None:
    w = h = 512
    rng = random.Random(6611)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(28):
        a = i / 28.0 * math.tau
        r = 120 + math.sin(a * 3.0 + 0.7) * 32 + rng.uniform(-18, 18)
        pts.append((256 + math.cos(a) * r, 256 + math.sin(a) * r * 0.62))
    d.polygon(pts, fill=(7, 15, 18, 125))
    d.polygon([(x + 4, y + 3) for x, y in pts], fill=(4, 9, 12, 95))
    for _ in range(22):
        x = rng.randint(110, 400)
        y = rng.randint(160, 350)
        r = rng.randint(4, 22)
        d.ellipse((x - r, y - r // 2, x + r, y + r // 2), fill=(38, 55, 58, rng.randint(18, 40)))
    img = img.filter(ImageFilter.GaussianBlur(3.0))
    save_rgba(img, "puddle.png")


def grime() -> None:
    w = h = 512
    rng = random.Random(7711)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(80):
        x = rng.randint(0, w)
        y = rng.randint(0, h)
        rx = rng.randint(8, 55)
        ry = rng.randint(5, 35)
        d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(18, 16, 12, rng.randint(8, 28)))
    for _ in range(24):
        x = rng.randint(0, w)
        y = rng.randint(0, h)
        d.line((x, y, x + rng.randint(-60, 60), y + rng.randint(20, 110)),
               fill=(11, 9, 7, rng.randint(20, 55)), width=rng.randint(1, 4))
    img = img.filter(ImageFilter.GaussianBlur(4.0))
    save_rgba(img, "grime_decal.png")


def flesh() -> None:
    w = h = 512
    n1 = art.fbm(w, h, 8, 5, 8801)
    n2 = art.fbm(w, h, 32, 4, 8813)
    rng = random.Random(8817)
    albedo = Image.new("RGB", (w, h))
    px = albedo.load()
    rough = [0.0] * (w * h)
    heights = [0.0] * (w * h)
    for y in range(h):
        for x in range(w):
            i = y * w + x
            mott = n1[i] * 0.65 + n2[i] * 0.35
            base = 126 + (mott - 0.5) * 34
            vein = 0.0
            px[x, y] = (clamp8(base + 10), clamp8(base + 3), clamp8(base - 8))
            rough[i] = 0.58 + n2[i] * 0.24
            heights[i] = n1[i] * 0.6 + n2[i] * 0.4
    # venas finas y manchas húmedas
    d = ImageDraw.Draw(albedo)
    for _ in range(48):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        pts = [(x, y)]
        for _step in range(rng.randint(3, 10)):
            x += rng.randint(-22, 22)
            y += rng.randint(-15, 15)
            pts.append((x, y))
        d.line(pts, fill=(58 + rng.randint(0, 18), 42, 42), width=rng.randint(1, 2))
    for _ in range(90):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        r = rng.randint(2, 12)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(92 + rng.randint(0, 24), 54, 50))
    albedo.save(OUT / "flesh_albedo.png")
    art.scalar_image(rough, w, h).save(OUT / "flesh_roughness.png")
    art.normal_map(w, h, heights, 1.4).save(OUT / "flesh_normal.png")


def bone() -> None:
    w = h = 256
    n1 = art.fbm(w, h, 8, 4, 9901)
    n2 = art.fbm(w, h, 32, 3, 9913)
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            i = y * w + x
            v = 158 + (n1[i] - 0.5) * 35 + (n2[i] - 0.5) * 16
            px[x, y] = (clamp8(v + 18), clamp8(v + 12), clamp8(v - 6))
    img.save(OUT / "bone_albedo.png")


def cloth() -> None:
    w = h = 256
    n1 = art.fbm(w, h, 32, 3, 10001)
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            weave = 0.5 + 0.5 * math.sin(x * 1.4) * math.sin(y * 1.4)
            v = 28 + n1[y * w + x] * 18 + weave * 5
            px[x, y] = (clamp8(v + 6), clamp8(v + 2), clamp8(v))
    img.save(OUT / "cloth_albedo.png")


def glass_crack() -> None:
    w = h = 512
    rng = random.Random(11001)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 250, 250
    for _ in range(14):
        a = rng.random() * math.tau
        length = rng.uniform(70, 230)
        pts = [(cx, cy)]
        x, y = cx, cy
        for _s in range(6):
            x += math.cos(a + rng.uniform(-0.28, 0.28)) * length / 6
            y += math.sin(a + rng.uniform(-0.28, 0.28)) * length / 6
            pts.append((x, y))
        d.line(pts, fill=(210, 235, 235, rng.randint(80, 170)), width=rng.randint(1, 3))
    for _ in range(7):
        a = rng.random() * math.tau
        r = rng.uniform(28, 65)
        d.arc((cx - r, cy - r, cx + r, cy + r), a * 180 / math.pi, (a + 1.2) * 180 / math.pi,
              fill=(190, 225, 225, 120), width=2)
    save_rgba(img, "glass_crack.png")


def main() -> None:
    blood_splat()
    blood_trail()
    handprint()
    puddle()
    grime()
    flesh()
    bone()
    cloth()
    glass_crack()
    print("Detalle visual generado en", OUT)


if __name__ == "__main__":
    main()
