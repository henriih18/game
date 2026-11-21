#!/usr/bin/env python3
"""Genera texturas PBR originales para el look dev de FRECUENCIA MUERTA.

No usa assets externos. Todo es procedural y reproducible.
"""
from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "art" / "fm"
OUT.mkdir(parents=True, exist_ok=True)


def clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def smooth(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def fbm(width: int, height: int, cells: int, octaves: int, seed: int,
        persistence: float = 0.5) -> list[float]:
    """Ruido de valor periódico en [0,1]."""
    out = [0.0] * (width * height)
    amp = 1.0
    total = 0.0
    for octave in range(octaves):
        gw = max(2, cells * (1 << octave))
        gh = max(2, cells * (1 << octave))
        rng = random.Random(seed + octave * 7919)
        grid = [rng.random() for _ in range(gw * gh)]
        for y in range(height):
            fy = (y / height) * gh
            yi = int(fy)
            ty = smooth(fy - yi)
            y0 = (yi % gh) * gw
            y1 = ((yi + 1) % gh) * gw
            for x in range(width):
                fx = (x / width) * gw
                xi = int(fx)
                tx = smooth(fx - xi)
                x0 = xi % gw
                x1 = (xi + 1) % gw
                a = grid[y0 + x0] * (1 - tx) + grid[y0 + x1] * tx
                b = grid[y1 + x0] * (1 - tx) + grid[y1 + x1] * tx
                v = a * (1 - ty) + b * ty
                out[y * width + x] += v * amp
        total += amp
        amp *= persistence
    inv = 1.0 / total
    return [min(1.0, max(0.0, v * inv)) for v in out]


def normal_map(width: int, height: int, height_values: list[float],
               strength: float = 2.0) -> Image.Image:
    """Normal map wrap-around desde un heightmap."""
    out = Image.new("RGB", (width, height))
    px = out.load()
    for y in range(height):
        ym = ((y - 1) % height) * width
        yp = ((y + 1) % height) * width
        row = y * width
        for x in range(width):
            xm = (x - 1) % width
            xp = (x + 1) % width
            dx = height_values[row + xp] - height_values[row + xm]
            dy = height_values[yp + x] - height_values[ym + x]
            nx = -dx * strength
            ny = -dy * strength
            nz = 1.0
            ln = math.sqrt(nx * nx + ny * ny + nz * nz)
            px[x, y] = (
                int((nx / ln * 0.5 + 0.5) * 255),
                int((ny / ln * 0.5 + 0.5) * 255),
                int((nz / ln * 0.5 + 0.5) * 255),
            )
    return out


def scalar_image(values: list[float], width: int, height: int, invert: bool = False) -> Image.Image:
    img = Image.new("L", (width, height))
    if invert:
        img.putdata([int((1.0 - v) * 255) for v in values])
    else:
        img.putdata([int(v * 255) for v in values])
    return img


def save_rgb(img: Image.Image, name: str) -> None:
    img.save(OUT / name)


def save_scalar(values: list[float], width: int, height: int, name: str, invert: bool = False) -> None:
    scalar_image(values, width, height, invert).save(OUT / name)


def make_concrete() -> None:
    w = h = 1024
    n1 = fbm(w, h, 5, 5, 1101)
    n2 = fbm(w, h, 18, 4, 2203)
    n3 = fbm(w, h, 64, 3, 3301)
    albedo = Image.new("RGB", (w, h))
    rough = [0.0] * (w * h)
    heightv = [0.0] * (w * h)
    px = albedo.load()
    for y in range(h):
        vertical = y / h
        for x in range(w):
            i = y * w + x
            base = 0.145 + n1[i] * 0.085 + n2[i] * 0.035
            stain = max(0.0, n2[i] - 0.55) * 0.22
            mold = max(0.0, n3[i] - 0.66) * 0.18 * (0.4 + vertical)
            r = base + 0.012 - stain + mold * 0.25
            g = base + 0.022 - stain + mold * 0.95
            b = base + 0.020 - stain + mold * 0.55
            px[x, y] = (int(clamp01(r) * 255), int(clamp01(g) * 255), int(clamp01(b) * 255))
            heightv[i] = 0.55 + n1[i] * 0.25 + n3[i] * 0.20
            rough[i] = clamp01(0.78 + n2[i] * 0.16 - stain * 0.7)
    draw = ImageDraw.Draw(albedo)
    rng = random.Random(42)
    for _ in range(18):
        x0 = rng.randint(0, w)
        y0 = rng.randint(0, h)
        pts = [(x0, y0)]
        for _ in range(rng.randint(2, 5)):
            x0 = (x0 + rng.randint(-40, 40)) % w
            y0 = (y0 + rng.randint(10, 80)) % h
            pts.append((x0, y0))
        draw.line(pts, fill=(35, 38, 34), width=rng.randint(1, 2))
    albedo = albedo.filter(ImageFilter.GaussianBlur(0.25))
    save_rgb(albedo, "concrete_wall_albedo.png")
    save_scalar(rough, w, h, "concrete_wall_roughness.png")
    save_rgb(normal_map(w, h, heightv, 1.4), "concrete_wall_normal.png")


def make_metal() -> None:
    w = h = 1024
    n1 = fbm(w, h, 4, 5, 5101)
    n2 = fbm(w, h, 24, 4, 6203)
    n3 = fbm(w, h, 90, 3, 7307)
    albedo = Image.new("RGB", (w, h))
    heightimg = Image.new("L", (w, h))
    rough = [0.0] * (w * h)
    heightv = [0.0] * (w * h)
    px = albedo.load()
    hp = heightimg.load()
    for y in range(h):
        for x in range(w):
            i = y * w + x
            scratch = max(0.0, n3[i] - 0.77) * 0.35
            base = 0.105 + n1[i] * 0.060 + n2[i] * 0.020
            r = base + 0.012 + scratch * 0.12
            g = base + 0.030 + scratch * 0.12
            b = base + 0.038 + scratch * 0.10
            px[x, y] = (int(clamp01(r) * 255), int(clamp01(g) * 255), int(clamp01(b) * 255))
            hv = 0.62 + n1[i] * 0.12 + n2[i] * 0.07
            hv -= scratch * 0.4
            heightv[i] = hv
            hp[x, y] = int(clamp01(hv) * 255)
            rough[i] = clamp01(0.38 + n2[i] * 0.20 + scratch * 0.25)
    draw = ImageDraw.Draw(albedo)
    hdraw = ImageDraw.Draw(heightimg)
    # Paneles de 256 px: juntas oscuras y remaches.
    for x in range(0, w, 256):
        draw.line([(x, 0), (x, h)], fill=(24, 29, 31), width=5)
        hdraw.line([(x, 0), (x, h)], fill=70, width=5)
        for y in range(32, h, 96):
            for ox in (-16, 16):
                draw.ellipse((x + ox - 5, y - 5, x + ox + 5, y + 5), fill=(55, 65, 67))
                hdraw.ellipse((x + ox - 5, y - 5, x + ox + 5, y + 5), fill=190)
    for y in range(0, h, 256):
        draw.line([(0, y), (w, y)], fill=(28, 34, 36), width=4)
        hdraw.line([(0, y), (w, y)], fill=82, width=4)
    # Manchas de óxido hacia abajo, sutiles.
    for _ in range(10):
        cx = random.randint(0, w)
        cy = random.choice([random.randint(0, 180), random.randint(h - 260, h)])
        rw = random.randint(10, 42)
        rh = random.randint(15, 70)
        draw.ellipse((cx - rw, cy - rh, cx + rw, cy + rh), fill=(55, 38, 28))
    albedo = albedo.filter(ImageFilter.GaussianBlur(0.35))
    heightimg = heightimg.filter(ImageFilter.GaussianBlur(0.5))
    save_rgb(albedo, "metal_panel_albedo.png")
    save_scalar(rough, w, h, "metal_panel_roughness.png")
    save_rgb(normal_map(w, h, heightv, 2.2), "metal_panel_normal.png")


def make_floor() -> None:
    w = h = 1024
    n1 = fbm(w, h, 6, 5, 8101)
    n2 = fbm(w, h, 30, 4, 9203)
    n3 = fbm(w, h, 80, 3, 10301)
    albedo = Image.new("RGB", (w, h))
    rough = [0.0] * (w * h)
    heightv = [0.0] * (w * h)
    px = albedo.load()
    for y in range(h):
        for x in range(w):
            i = y * w + x
            tile = 0.5 + 0.5 * math.sin((x / w) * math.pi * 8.0) * math.sin((y / h) * math.pi * 8.0)
            wet = max(0.0, n2[i] - 0.58) * 1.8
            grime = max(0.0, n3[i] - 0.68) * 0.20
            base = 0.070 + n1[i] * 0.035 + tile * 0.010
            r = base + 0.004 - wet * 0.025 + grime * 0.06
            g = base + 0.008 - wet * 0.020 + grime * 0.05
            b = base + 0.010 - wet * 0.012 + grime * 0.035
            px[x, y] = (int(clamp01(r) * 255), int(clamp01(g) * 255), int(clamp01(b) * 255))
            heightv[i] = 0.48 + n1[i] * 0.10 + tile * 0.06
            rough[i] = clamp01(0.56 + n2[i] * 0.15 - wet * 0.48)
    draw = ImageDraw.Draw(albedo)
    for x in range(0, w, 256):
        draw.line([(x, 0), (x, h)], fill=(20, 24, 25), width=3)
    for y in range(0, h, 256):
        draw.line([(0, y), (w, y)], fill=(20, 24, 25), width=3)
    save_rgb(albedo.filter(ImageFilter.GaussianBlur(0.2)), "floor_wet_albedo.png")
    save_scalar(rough, w, h, "floor_wet_roughness.png")
    save_rgb(normal_map(w, h, heightv, 0.8), "floor_wet_normal.png")


def make_rust() -> None:
    w = h = 512
    n1 = fbm(w, h, 5, 5, 13101)
    n2 = fbm(w, h, 22, 4, 14103)
    n3 = fbm(w, h, 70, 3, 15107)
    albedo = Image.new("RGB", (w, h))
    rough = [0.0] * (w * h)
    heightv = [0.0] * (w * h)
    px = albedo.load()
    for y in range(h):
        for x in range(w):
            i = y * w + x
            pit = max(0.0, n3[i] - 0.72) * 0.7
            r = 0.28 + n1[i] * 0.18 + n2[i] * 0.10 - pit * 0.12
            g = 0.12 + n1[i] * 0.10 + n2[i] * 0.06 - pit * 0.07
            b = 0.045 + n1[i] * 0.04 + n2[i] * 0.02 - pit * 0.02
            px[x, y] = (int(clamp01(r) * 255), int(clamp01(g) * 255), int(clamp01(b) * 255))
            heightv[i] = 0.55 + n1[i] * 0.20 + n2[i] * 0.10 - pit * 0.5
            rough[i] = clamp01(0.82 + n2[i] * 0.12 + pit * 0.08)
    save_rgb(albedo, "rust_albedo.png")
    save_scalar(rough, w, h, "rust_roughness.png")
    save_rgb(normal_map(w, h, heightv, 2.0), "rust_normal.png")


def make_hazard() -> None:
    w = h = 512
    img = Image.new("RGB", (w, h), (32, 30, 24))
    draw = ImageDraw.Draw(img)
    for i in range(-h, w + h, 128):
        draw.polygon([(i, 0), (i + 64, 0), (i + 64 - h, h), (i - h, h)], fill=(176, 112, 24))
    n = fbm(w, h, 24, 4, 16103)
    px = img.load()
    for y in range(h):
        for x in range(w):
            i = y * w + x
            dirt = (n[i] - 0.5) * 0.30
            r, g, b = px[x, y]
            px[x, y] = (
                int(clamp01(r / 255 + dirt) * 255),
                int(clamp01(g / 255 + dirt) * 255),
                int(clamp01(b / 255 + dirt) * 255),
            )
    img.save(OUT / "hazard_stripe.png")


def make_grunge() -> None:
    w = h = 512
    n1 = fbm(w, h, 8, 5, 17101)
    n2 = fbm(w, h, 40, 4, 18103)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y in range(h):
        for x in range(w):
            i = y * w + x
            a = max(0.0, n1[i] * 0.5 + n2[i] * 0.5 - 0.58) * 2.6
            if a > 0.03:
                px[x, y] = (18, 15, 13, int(clamp01(a) * 210))
    img.save(OUT / "grunge_decal.png")


def make_screen() -> None:
    w = h = 256
    img = Image.new("RGB", (w, h), (5, 20, 24))
    draw = ImageDraw.Draw(img)
    for y in range(0, h, 4):
        draw.line([(0, y), (w, y)], fill=(8, 42, 48))
    for y in range(16, h, 32):
        draw.line([(18, y), (w - 18, y)], fill=(30, 145, 148))
    draw.rectangle((16, 16, w - 16, h - 16), outline=(40, 190, 190), width=2)
    draw.text((24, 24), "NEXUS // BIO-LAB", fill=(120, 240, 220))
    draw.text((24, 48), "SECTOR 04  CONTENCION", fill=(80, 190, 180))
    for i in range(5):
        y = 82 + i * 22
        draw.line([(24, y), (w - 32 - i * 12, y)], fill=(42, 170, 168))
    img.save(OUT / "screen_scan.png")


def make_smoke() -> None:
    w = h = 128
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y in range(h):
        for x in range(w):
            dx = (x - w / 2) / (w / 2)
            dy = (y - h / 2) / (h / 2)
            d = math.sqrt(dx * dx + dy * dy)
            a = max(0.0, 1.0 - d)
            a = a * a * 0.55
            px[x, y] = (190, 200, 200, int(a * 255))
    img.save(OUT / "smoke.png")


def write_material(name: str, albedo: str, roughness: str, normal: str,
                   metallic: float = 0.0, tint: tuple[float, float, float] = (1, 1, 1),
                   uv_scale: float = 1.0) -> None:
    text = f"""[gd_resource type="StandardMaterial3D" load_steps=4 format=3]

[ext_resource type="Texture2D" path="res://assets/art/fm/{albedo}" id="1"]
[ext_resource type="Texture2D" path="res://assets/art/fm/{roughness}" id="2"]
[ext_resource type="Texture2D" path="res://assets/art/fm/{normal}" id="3"]

[resource]
albedo_texture = ExtResource("1")
albedo_color = Color({tint[0]}, {tint[1]}, {tint[2]}, 1)
roughness_texture = ExtResource("2")
normal_enabled = true
normal_texture = ExtResource("3")
normal_scale = 1.0
metallic = {metallic}
metallic_specular = 0.5
uv1_scale = Vector3({uv_scale}, {uv_scale}, {uv_scale})
texture_filter = 5
"""
    (OUT / f"{name}.tres").write_text(text, encoding="utf-8")


def write_simple_material(name: str, albedo: str, metallic: float = 0.0,
                          roughness: float = 0.7, emission: tuple[float, float, float] | None = None,
                          emission_energy: float = 0.0, transparency: float = 1.0,
                          emission_texture: bool = False) -> None:
    emission_line = ""
    if emission is not None:
        emission_line = (
            f"emission_enabled = true\n"
            f"emission = Color({emission[0]}, {emission[1]}, {emission[2]}, 1)\n"
        )
        if emission_texture:
            emission_line += 'emission_texture = ExtResource("1")\n'
        emission_line += f"emission_energy_multiplier = {emission_energy}\n"
    text = f"""[gd_resource type="StandardMaterial3D" load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://assets/art/fm/{albedo}" id="1"]

[resource]
albedo_texture = ExtResource("1")
albedo_color = Color(1, 1, 1, {transparency})
metallic = {metallic}
roughness = {roughness}
texture_filter = 5
{emission_line}"""
    (OUT / f"{name}.tres").write_text(text, encoding="utf-8")


def write_plain_material(name: str, color: tuple[float, float, float], metallic: float = 0.0,
                         roughness: float = 0.7, emission: tuple[float, float, float] | None = None,
                         energy: float = 0.0, alpha: float = 1.0) -> None:
    emission_line = ""
    if emission is not None:
        emission_line = (
            f"emission_enabled = true\n"
            f"emission = Color({emission[0]}, {emission[1]}, {emission[2]}, 1)\n"
            f"emission_energy_multiplier = {energy}\n"
        )
    transparency_line = ""
    if alpha < 1.0:
        transparency_line = "transparency = 1\n"
    text = f"""[gd_resource type="StandardMaterial3D" format=3]

[resource]
albedo_color = Color({color[0]}, {color[1]}, {color[2]}, {alpha})
metallic = {metallic}
roughness = {roughness}
{transparency_line}{emission_line}"""
    (OUT / f"{name}.tres").write_text(text, encoding="utf-8")


def main() -> None:
    make_concrete()
    make_metal()
    make_floor()
    make_rust()
    make_hazard()
    make_grunge()
    make_screen()
    make_smoke()

    write_material("concrete_wall", "concrete_wall_albedo.png", "concrete_wall_roughness.png",
                   "concrete_wall_normal.png", 0.0, (0.86, 0.92, 0.90), 1.0)
    write_material("metal_panel", "metal_panel_albedo.png", "metal_panel_roughness.png",
                   "metal_panel_normal.png", 0.55, (0.80, 0.88, 0.92), 1.0)
    write_material("floor_wet", "floor_wet_albedo.png", "floor_wet_roughness.png",
                   "floor_wet_normal.png", 0.12, (0.78, 0.84, 0.82), 1.0)
    write_material("rust", "rust_albedo.png", "rust_roughness.png", "rust_normal.png",
                   0.25, (0.9, 0.72, 0.55), 1.0)
    write_simple_material("hazard", "hazard_stripe.png", 0.0, 0.72)
    write_plain_material("emissive_cyan", (0.02, 0.03, 0.035), 0.0, 0.25,
                         (0.10, 0.95, 1.0), 4.0)
    write_plain_material("emissive_red", (0.04, 0.01, 0.01), 0.0, 0.25,
                         (1.0, 0.04, 0.02), 5.0)
    write_plain_material("emissive_orange", (0.04, 0.025, 0.01), 0.0, 0.3,
                         (1.0, 0.36, 0.06), 3.0)
    write_plain_material("emissive_green", (0.01, 0.035, 0.02), 0.0, 0.25,
                         (0.18, 1.0, 0.30), 3.0)
    write_plain_material("rubber", (0.025, 0.028, 0.027), 0.0, 0.88)
    write_plain_material("dark_metal", (0.045, 0.055, 0.055), 0.7, 0.4)
    write_plain_material("warning_yellow", (0.55, 0.34, 0.045), 0.0, 0.7)
    write_plain_material("glass", (0.25, 0.55, 0.55), 0.2, 0.06, alpha=0.18)
    write_plain_material("goo", (0.02, 0.22, 0.07), 0.0, 0.28,
                         (0.08, 0.8, 0.22), 1.2, alpha=0.82)
    write_simple_material("screen", "screen_scan.png", 0.0, 0.35,
                          (0.18, 0.9, 0.85), 4.0, emission_texture=True)
    (OUT / "smoke.png")
    print(f"Arte generado en {OUT}")


if __name__ == "__main__":
    main()
