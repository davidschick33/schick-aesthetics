"""Vorder- und Rückseite der Bewertungskarte als je eine handyfreundliche Bild-PDF.
Aufruf (nach make_karte.js): python3 bewertungskarte/make_handy_pdf.py"""
from pathlib import Path
from PIL import Image

d = Path(__file__).resolve().parent
for side, name in [("Vorderseite", "Bewertungskarte-Vorderseite-Handy.pdf"), ("Rueckseite", "Bewertungskarte-Rueckseite-Handy.pdf")]:
    img = Image.open(d / f"Bewertungskarte-{side}.png").convert("RGB")
    img.save(d / name, resolution=img.width / (85 / 25.4), quality=90)
print("ok")
