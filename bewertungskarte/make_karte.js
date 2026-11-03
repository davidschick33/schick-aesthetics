// Erzeugt die Bewertungskarte: Druck-PDF (3 mm Beschnitt), PDF zum Ansehen und Vorschaubilder.
// Aufruf: node bewertungskarte/make_karte.js
const { chromium } = require("playwright");
const path = require("path");

const dir = __dirname;
const url = (q) => "file://" + path.join(dir, "karte.html") + q;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto(url(""), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(dir, "Bewertungskarte-85x55.pdf"), width: "85mm", height: "55mm", printBackground: true });

  await page.goto(url("?beschnitt=1"), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(dir, "Bewertungskarte-Druck-3mm-Beschnitt.pdf"), width: "91mm", height: "61mm", printBackground: true });

  const prev = await browser.newPage({ viewport: { width: 330, height: 220 }, deviceScaleFactor: 4 });
  await prev.goto(url(""), { waitUntil: "networkidle" });
  await prev.evaluate(() => document.fonts.ready);
  const pages = await prev.$$(".page");
  await pages[0].screenshot({ path: path.join(dir, "Bewertungskarte-Vorderseite.png") });
  await pages[1].screenshot({ path: path.join(dir, "Bewertungskarte-Rueckseite.png") });

  await browser.close();
  console.log("ok");
})();
