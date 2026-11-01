// Erzeugt den Flyer als PDF (ansehen/mailen und druckfertig mit 3 mm Beschnitt) und PNG-Vorschauen.
// Aufruf: node flyer/make_flyer.js
const { chromium } = require("playwright");
const path = require("path");

const dir = __dirname;
const url = (q) => "file://" + path.join(dir, "flyer.html") + q;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Ansicht / E-Mail: Endformat DIN A5
  await page.goto(url(""), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(dir, "Flyer-Dr-Schick-A5.pdf"), width: "148mm", height: "210mm", printBackground: true, preferCSSPageSize: false });

  // Druckerei: 154 × 216 mm (3 mm Beschnitt rundum)
  await page.goto(url("?beschnitt=1"), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(dir, "Flyer-Dr-Schick-A5-Druck-3mm-Beschnitt.pdf"), width: "154mm", height: "216mm", printBackground: true });

  // PNG-Vorschauen
  const prev = await browser.newPage({ viewport: { width: 560, height: 794 }, deviceScaleFactor: 2 });
  await prev.goto(url(""), { waitUntil: "networkidle" });
  await prev.evaluate(() => document.fonts.ready);
  const pages = await prev.$$(".page");
  await pages[0].screenshot({ path: path.join(dir, "Vorschau-Vorderseite.png") });
  await pages[1].screenshot({ path: path.join(dir, "Vorschau-Rueckseite.png") });

  // Handy-/Teilen-Version: hochauflösende Bilder (JPG) – werden zu einem einfachen Bild-PDF zusammengefügt
  const hi = await browser.newPage({ viewport: { width: 560, height: 794 }, deviceScaleFactor: 3 });
  await hi.goto(url(""), { waitUntil: "networkidle" });
  await hi.evaluate(() => document.fonts.ready);
  const hp = await hi.$$(".page");
  await hp[0].screenshot({ path: path.join(dir, "Flyer-Vorderseite.jpg"), type: "jpeg", quality: 88 });
  await hp[1].screenshot({ path: path.join(dir, "Flyer-Rueckseite.jpg"), type: "jpeg", quality: 88 });

  await browser.close();
  console.log("ok");
})();
