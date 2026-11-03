"""Wandelt 10-Beitraege.md in ein handyfreundliches PDF um.  Aufruf: python3 social-media/make_pdf.py"""
import subprocess
from pathlib import Path

import markdown

d = Path(__file__).resolve().parent
root = d.parent
body = markdown.markdown((d / "10-Beitraege.md").read_text(encoding="utf-8"), extensions=["extra"])
fonts = (root / "src/assets/fonts").as_uri()
html = f"""<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><style>
@font-face {{ font-family: C; font-weight: 600; src: url("{fonts}/cormorant-garamond-latin-600-normal.woff2"); }}
@font-face {{ font-family: J; font-weight: 300; src: url("{fonts}/jost-latin-300-normal.woff2"); }}
@font-face {{ font-family: J; font-weight: 500; src: url("{fonts}/jost-latin-500-normal.woff2"); }}
@page {{ size: A5; margin: 14mm 12mm; }}
body {{ font-family: J, sans-serif; font-weight: 300; font-size: 10.5pt; line-height: 1.5; color: #26292b; }}
h1 {{ font-family: C, serif; font-size: 22pt; color: #5e3f1a; line-height: 1.1; }}
h2 {{ font-family: C, serif; font-size: 16pt; color: #5e3f1a; margin-top: 0; break-before: page; }}
strong {{ font-weight: 500; color: #5e3f1a; }}
blockquote {{ margin: 8px 0; padding: 10px 14px; background: #f3efe8; border-left: 3px solid #b39466; border-radius: 6px; }}
blockquote p {{ margin: 0 0 6px; }} hr {{ display: none; }} li {{ margin-bottom: 4px; }}
</style></head><body>{body}</body></html>"""
tmp = d / "_tmp.html"
tmp.write_text(html, encoding="utf-8")
js = f"""const {{ chromium }} = require("playwright");
(async () => {{ const b = await chromium.launch(); const p = await b.newPage();
await p.goto("{tmp.as_uri()}", {{ waitUntil: "networkidle" }}); await p.evaluate(() => document.fonts.ready);
await p.pdf({{ path: "{(d / '10-Social-Media-Beitraege.pdf').as_posix()}", format: "A5", printBackground: true, margin: {{ top: "14mm", bottom: "14mm", left: "12mm", right: "12mm" }} }});
await b.close(); }})();"""
subprocess.run(["node", "-e", js], check=True)
tmp.unlink()
print("ok")
