"""Rendert die Wassertropfen-Grafiken (transparente WebP-Overlays) fuer den Seitenhintergrund.

Aufruf:  python3 tools/make_drops.py
Erzeugt: src/assets/img/drops.webp, drops-small.webp, drops-hero.webp
"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "src" / "assets" / "img"

# Licht faellt von oben links ein
LIGHT = np.array([-0.45, -0.6, 0.66])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def over(dst, rgb, alpha):
    """Alpha-Compositing (premultiplied) von Farbe rgb mit Deckkraft alpha auf dst."""
    a = np.clip(alpha, 0, 1)[..., None]
    col = np.array(rgb, dtype=np.float32) / 255.0
    dst[..., :3] = col * a + dst[..., :3] * (1 - a)
    dst[..., 3:4] = a + dst[..., 3:4] * (1 - a)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def draw_drop(canvas, cx, cy, r, rng):
    h, w, _ = canvas.shape
    # leicht unregelmaessige, nach unten gezogene Form
    sx = r * rng.uniform(0.92, 1.06)
    sy = r * rng.uniform(1.0, 1.14)
    pad = int(r * 1.6) + 3
    x0, x1 = int(cx - pad), int(cx + pad)
    y0, y1 = int(cy - pad), int(cy + pad)
    if x1 < 0 or y1 < 0 or x0 >= w or y0 >= h:
        return
    xs0, ys0 = max(x0, 0), max(y0, 0)
    xs1, ys1 = min(x1, w), min(y1, h)
    yy, xx = np.mgrid[ys0:ys1, xs0:xs1].astype(np.float32)
    dx = (xx - cx) / sx
    dy = (yy - cy) / sy
    theta = np.arctan2(dy, dx)
    wobble = 1 + 0.035 * np.sin(3 * theta + rng.uniform(0, 6.28)) + 0.025 * np.sin(5 * theta + rng.uniform(0, 6.28))
    d = np.sqrt(dx * dx + dy * dy) / wobble
    sub = canvas[ys0:ys1, xs0:xs1]
    aa = 1.2 / r  # Kantenglaettung ~1px

    # Schatten ausserhalb, nach unten rechts versetzt
    sdx = (xx - (cx + 0.14 * r)) / (sx * 1.08)
    sdy = (yy - (cy + 0.22 * r)) / (sy * 1.08)
    sd = np.sqrt(sdx * sdx + sdy * sdy)
    shadow = (1 - smoothstep(0.75, 1.08, sd)) * smoothstep(1 - aa, 1 + aa, d) * 0.16
    over(sub, (28, 52, 60), shadow)

    inside = 1 - smoothstep(1 - aa, 1 + aa, d)
    dc = np.clip(d, 0, 1)
    nx, ny = dx / np.maximum(d, 1e-4) * dc, dy / np.maximum(d, 1e-4) * dc

    # Koerper: leichte Toenung, Rand dunkler (Brechung)
    body = (0.05 + 0.42 * dc ** 5) * inside
    over(sub, (34, 70, 80), body)

    # Lichtbuendelung auf der lichtabgewandten Seite (Kaustik)
    lxy = -LIGHT[:2] / np.linalg.norm(LIGHT[:2])
    caustic = np.clip(nx * lxy[0] + ny * lxy[1], 0, 1) ** 2 * smoothstep(0.35, 0.9, dc) * (1 - smoothstep(0.9, 1.0, dc))
    over(sub, (255, 255, 255), caustic * 0.75 * inside)

    # Glanzpunkt oben links
    hx, hy = -0.36, -0.42
    hd = np.sqrt(((dx - hx) / 0.24) ** 2 + ((dy - hy) / 0.17) ** 2)
    spec = np.exp(-hd * hd * 2.2) * inside
    over(sub, (255, 255, 255), spec * 0.95)
    # kleiner zweiter Reflex
    hd2 = np.sqrt(((dx - 0.3) / 0.1) ** 2 + ((dy - 0.48) / 0.07) ** 2)
    over(sub, (255, 255, 255), np.exp(-hd2 * hd2 * 2.5) * inside * 0.45)

    # feine helle Kontur oben
    rim = smoothstep(0.86, 0.98, dc) * inside * np.clip(nx * LIGHT[0] + ny * LIGHT[1], 0, 1) * 0.35
    over(sub, (255, 255, 255), rim)


def place(width, height, sizes, seed, region=None, tile=False):
    rng = np.random.default_rng(seed)
    random.seed(seed)
    placed = []
    for r in sizes:
        for _ in range(60):
            if region:
                x = rng.uniform(region[0], region[2]) * width
                y = rng.uniform(region[1], region[3]) * height
            else:
                x, y = rng.uniform(0, width), rng.uniform(0, height)
            ok = True
            for (px, py, pr) in placed:
                ddx, ddy = abs(px - x), abs(py - y)
                if tile:
                    ddx, ddy = min(ddx, width - ddx), min(ddy, height - ddy)
                if math.hypot(ddx, ddy) < (pr + r) * 1.25 + 2:
                    ok = False
                    break
            if ok:
                placed.append((x, y, r))
                break
    return placed, rng


def render(width, height, drops, rng, tile=False):
    canvas = np.zeros((height, width, 4), dtype=np.float32)
    for (x, y, r) in sorted(drops, key=lambda d: d[2]):
        offs = [(0, 0)]
        if tile:
            offs = [(ox, oy) for ox in (-width, 0, width) for oy in (-height, 0, height)]
        for ox, oy in offs:
            draw_drop(canvas, x + ox, y + oy, r, rng)
    # premultiplied -> straight alpha
    a = canvas[..., 3:4]
    rgb = np.where(a > 1e-4, canvas[..., :3] / np.maximum(a, 1e-4), 0)
    img = np.concatenate([np.clip(rgb, 0, 1), np.clip(a, 0, 1)], axis=-1)
    return Image.fromarray((img * 255).astype(np.uint8), "RGBA")


def sizes(rng, n_small, n_mid, n_large, s=(2.5, 7), m=(8, 18), l=(20, 34)):
    out = list(rng.uniform(*l, n_large)) + list(rng.uniform(*m, n_mid)) + list(rng.uniform(*s, n_small))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)

    # Kachelbarer Hintergrund (dezent, viele kleine Tropfen)
    W = H = 1200
    drops, r2 = place(W, H, sizes(rng, 260, 46, 9), seed=11, tile=True)
    img = render(W, H, drops, r2, tile=True)
    img.save(OUT / "drops.webp", "WEBP", quality=82, method=6)
    img.resize((800, 800), Image.LANCZOS).save(OUT / "drops-small.webp", "WEBP", quality=80, method=6)

    # Hero-Tropfen: groesser, zum rechten Rand dichter
    W, H = 1600, 1000
    hs = sizes(rng, 140, 40, 12, s=(3, 9), m=(10, 26), l=(30, 62))
    drops, r3 = place(W, H, hs, seed=23, region=(0.42, 0.0, 1.0, 1.0))
    small_left, _ = place(W, H, list(rng.uniform(2.5, 8, 60)), seed=31, region=(0.0, 0.0, 0.5, 1.0))
    img = render(W, H, drops + small_left, r3)
    img.save(OUT / "drops-hero.webp", "WEBP", quality=84, method=6)
    print("ok")


if __name__ == "__main__":
    main()
