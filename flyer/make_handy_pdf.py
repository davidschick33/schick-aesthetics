"""Kleine Handy-PDF (ca. 190 dpi) aus Flyer-Vorderseite.jpg und Flyer-Rueckseite.jpg.
Aufruf (nach make_flyer.js): python3 flyer/make_handy_pdf.py"""
from pathlib import Path
from PIL import Image

d = Path(__file__).resolve().parent
w = 1100
imgs = []
for name in ("Flyer-Vorderseite.jpg", "Flyer-Rueckseite.jpg"):
    im = Image.open(d / name).convert("RGB")
    imgs.append(im.resize((w, round(im.height * w / im.width)), Image.LANCZOS))
imgs[0].save(d / "Flyer-Dr-Schick-Handy.pdf", save_all=True, append_images=imgs[1:],
             resolution=w / (148 / 25.4), quality=85)
print("ok")
