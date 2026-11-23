// Erzeugt logo/Dr-Schick-Logo-Spezifikation.pdf aus tools/logo-spezifikation.html
// Aufruf: node tools/make_logo_spec.js [Ordner für Vorschaubilder]
const { chromium } = require("playwright");
const path = require("path");
const html = "file://" + path.join(__dirname, "logo-spezifikation.html");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto(html, { waitUntil: "networkidle" });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.join(__dirname, "..", "logo", "Dr-Schick-Logo-Spezifikation.pdf"), format: "A4", printBackground: true, preferCSSPageSize: true });
  const prevDir = process.argv[2];
  if (prevDir) {
    const v = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 1.5 });
    await v.goto(html, { waitUntil: "networkidle" });
    await v.evaluate(() => document.fonts.ready);
    const pages = await v.$$(".page");
    for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: path.join(prevDir, `spezifikation-${i + 1}.png`) });
  }
  await b.close();
  console.log("ok");
})();
