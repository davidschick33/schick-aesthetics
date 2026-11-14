"""Erzeugt das Logo-Paket in logo/: SVG, PDF, EPS und PNG in mehreren Farbvarianten.
Aufruf: python3 tools/make_logo_package.py"""
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = root / "src" / "assets" / "img"
out = root / "logo"
out.mkdir(exist_ok=True)

SOURCES = {
    "Logo-komplett": src / "logo-komplett.svg",   # mit Medical Aesthetics, Claim, Linie, Zahnärztin & Heilpraktikerin
    "Wortmarke": src / "logo-dr-schick.svg",      # nur "Dr. Schick" mit Gesichtsprofil
}
COLORS = {
    "gold": None,          # Gold-Verlauf wie im Original
    "braun": "#5e3f1a",    # einfarbig im Goldbraun des Originals (für Druck, Stempel, Stick)
    "schwarz": "#1a1a1a",
    "weiss": "#ffffff",    # für dunkle Hintergründe
}

made = []
for name, path in SOURCES.items():
    svg = path.read_text(encoding="utf-8")
    for cname, color in COLORS.items():
        s = svg
        if color:
            s = re.sub(r"<defs>.*?</defs>\s*", "", s, flags=re.S)
            s = re.sub(r'fill="url\(#[^)]+\)"', f'fill="{color}"', s)
        f = out / f"Dr-Schick-{name}-{cname}.svg"
        f.write_text(s, encoding="utf-8")
        made.append(f)

# PDF (Vektor) und PNG (transparent) über den Browser, EPS aus der PDF
js = r"""
const { chromium } = require("playwright");
const fs = require("fs"); const path = require("path");
(async () => {
  const b = await chromium.launch();
  for (const f of process.argv.slice(1)) {
    const svg = fs.readFileSync(f, "utf8");
    const vb = svg.match(/viewBox="([\d.\- ]+)"/)[1].split(/\s+/).map(Number);
    const ratio = vb[3] / vb[2];
    const wMm = 200, hMm = +(wMm * ratio).toFixed(2);
    const p = await b.newPage();
    const white = f.includes("-weiss");
    await p.setContent(`<style>@page{size:${wMm}mm ${hMm}mm;margin:0}*{margin:0}body{background:${white ? "#5e3f1a" : "transparent"}}img{display:block;width:${wMm}mm;height:${hMm}mm}</style><img src="data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}">`);
    await p.pdf({ path: f.replace(/\.svg$/, ".pdf"), width: wMm + "mm", height: hMm + "mm", printBackground: false });
    const pxW = 4000, pxH = Math.round(pxW * ratio);
    const q = await b.newPage({ viewport: { width: pxW, height: pxH } });
    await q.setContent(`<style>*{margin:0}body{background:transparent}img{display:block;width:${pxW}px;height:${pxH}px}</style><img src="data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}">`);
    await q.screenshot({ path: f.replace(/\.svg$/, ".png"), omitBackground: true });
    await p.close(); await q.close();
  }
  await b.close();
})();
"""
subprocess.run(["node", "-e", js, *[str(f) for f in made]], check=True)
for f in made:
    pdf = f.with_suffix(".pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=eps2write",
                    f"-sOutputFile={f.with_suffix('.eps')}", str(pdf)], check=True)
print("ok", len(made), "Varianten")
