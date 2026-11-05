// Erzeugt den Flyer (DIN A5, Vorder- und Rückseite).
// Aufruf: node flyer/make_flyer.js && python3 flyer/make_handy_pdf.py
//
// Die PDFs enthalten jede Seite als hochauflösendes Bild (ca. 300 dpi) statt als
// Vektorschrift: So sehen sie auf jedem Handy und in jedem Drucker gleich aus.
//   Flyer-Dr-Schick-A5.pdf                     – zum Ansehen und Selbstdrucken (A5)
//   Flyer-Dr-Schick-A5-Druck-3mm-Beschnitt.pdf – für die Druckerei (154 × 216 mm)
const { chromium } = require("playwright");
const fs = require("fs");
const os = require("os");
const path = require("path");

const dir = __dirname;
const url = (q) => "file://" + path.join(dir, "flyer.html") + q;
const SCALE = 3.2; // 148 mm ≈ 559 CSS-px → × 3,2 ≈ 1790 px ≈ 307 dpi

async function renderPages(browser, query, prefix) {
  const page = await browser.newPage({ viewport: { width: 700, height: 900 }, deviceScaleFactor: SCALE });
  await page.goto(url(query), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  const files = [];
  const pages = await page.$$(".page");
  for (let i = 0; i < pages.length; i++) {
    const f = path.join(os.tmpdir(), `${prefix}-${i}.jpg`);
    await pages[i].screenshot({ path: f, type: "jpeg", quality: 92 });
    files.push(f);
  }
  await page.close();
  return files;
}

async function imagesToPdf(browser, images, widthMm, heightMm, out) {
  const html = `<!doctype html><meta charset="utf-8"><style>
    @page { size: ${widthMm}mm ${heightMm}mm; margin: 0; }
    * { margin: 0; padding: 0; }
    img { display: block; width: ${widthMm}mm; height: ${heightMm}mm; page-break-after: always; }
    img:last-child { page-break-after: auto; }
  </style>${images.map((f) => `<img src="file://${f}">`).join("")}`;
  const tmp = path.join(os.tmpdir(), "flyer-pdf-wrapper.html");
  fs.writeFileSync(tmp, html);
  const page = await browser.newPage();
  await page.goto("file://" + tmp, { waitUntil: "networkidle" });
  await page.pdf({ path: out, width: `${widthMm}mm`, height: `${heightMm}mm`, printBackground: true, preferCSSPageSize: true });
  await page.close();
}

(async () => {
  const browser = await chromium.launch();

  const a5 = await renderPages(browser, "", "flyer-a5");
  await imagesToPdf(browser, a5, 148, 210, path.join(dir, "Flyer-Dr-Schick-A5.pdf"));

  const bleed = await renderPages(browser, "?beschnitt=1", "flyer-bleed");
  await imagesToPdf(browser, bleed, 154, 216, path.join(dir, "Flyer-Dr-Schick-A5-Druck-3mm-Beschnitt.pdf"));

  // Bilder (JPG) zum Teilen und als Grundlage für die Handy-PDF
  fs.copyFileSync(a5[0], path.join(dir, "Flyer-Vorderseite.jpg"));
  fs.copyFileSync(a5[1], path.join(dir, "Flyer-Rueckseite.jpg"));

  // kleine Vorschaubilder
  const prev = await browser.newPage({ viewport: { width: 560, height: 794 }, deviceScaleFactor: 2 });
  await prev.goto(url(""), { waitUntil: "networkidle" });
  await prev.evaluate(() => document.fonts.ready);
  const pages = await prev.$$(".page");
  await pages[0].screenshot({ path: path.join(dir, "Vorschau-Vorderseite.png") });
  await pages[1].screenshot({ path: path.join(dir, "Vorschau-Rueckseite.png") });

  await browser.close();
  console.log("ok");
})();
