"""Fügt Flyer-Vorderseite.jpg und Flyer-Rueckseite.jpg zu einem einfachen Bild-PDF zusammen,
das auf jedem Handy korrekt angezeigt wird.  Aufruf (nach make_flyer.js): python3 flyer/make_handy_pdf.py"""
from pathlib import Path
from PIL import Image

d = Path(__file__).resolve().parent
front = Image.open(d / "Flyer-Vorderseite.jpg").convert("RGB")
back = Image.open(d / "Flyer-Rueckseite.jpg").convert("RGB")
front.save(d / "Flyer-Dr-Schick-Handy.pdf", save_all=True, append_images=[back],
           resolution=front.width / (148 / 25.4), quality=85)
print("ok")
