// Erzeugt Logo, Favicons und Social-Media-Vorschaubild (og-image) per Headless-Browser.
// Aufruf: node tools/make_brand_assets.js
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");
const os = require("os");
const root = path.resolve(__dirname, "..");
const assets = "file://" + path.join(root, "src/assets");
const out = (f) => path.join(root, "src/assets/img", f);

const fonts = `
@font-face{font-family:C;src:url(${assets}/fonts/cormorant-garamond-latin-500-normal.woff2)}
@font-face{font-family:CI;src:url(${assets}/fonts/cormorant-garamond-latin-500-italic.woff2)}
@font-face{font-family:J;src:url(${assets}/fonts/jost-latin-400-normal.woff2)}
@font-face{font-family:JL;src:url(${assets}/fonts/jost-latin-300-normal.woff2)}
*{margin:0;box-sizing:border-box}
.bronze{background:linear-gradient(120deg,#7d5640,#c9a68b 45%,#a2765a 70%,#7d5640);-webkit-background-clip:text;background-clip:text;color:transparent}`;

const icon = (size) => `<style>${fonts} body{width:${size}px;height:${size}px;display:grid;place-items:center;
background:radial-gradient(circle at 35% 30%,#fff,#eef3f4 60%,#cfdde1)}
span{font-family:C;font-size:${size * 0.72}px;line-height:1;margin-top:-${size * 0.08}px}</style><span class="bronze">S</span>`;

const logo = `<style>${fonts} body{width:1000px;height:400px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:transparent}
.n{font-family:C;font-size:190px;line-height:.9}.s{font-family:J;font-size:30px;letter-spacing:.34em;margin-top:18px;color:#26292b;padding-left:.34em}
.c{font-family:J;font-size:20px;letter-spacing:.3em;color:#a2765a;margin-top:14px}</style>
<div class="n bronze">Schick</div><div class="s">MEDICAL AESTHETICS</div><div class="c">PRÄZISION · ÄSTHETIK · GESUNDHEIT</div>`;

const og = `<style>${fonts} body{width:1200px;height:630px;position:relative;overflow:hidden;
background:linear-gradient(160deg,#f7f6f3,#e6eef0 55%,#dfe9eb)}
.drops{position:absolute;inset:0;background:url(${assets}/img/drops-hero.webp) right center/auto 120% no-repeat}
.txt{position:absolute;left:70px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;width:640px}
.n{font-family:C;font-size:150px;line-height:.9}.s{font-family:J;font-size:24px;letter-spacing:.34em;color:#26292b;margin-top:14px}
.c{font-family:J;font-size:17px;letter-spacing:.28em;color:#a2765a;margin-top:12px}
.h{font-family:CI;font-size:42px;color:#2f5560;margin-top:40px;line-height:1.15}
.p{font-family:JL;font-size:24px;color:#545b5f;margin-top:14px}
.photo{position:absolute;right:70px;top:55px;width:370px;height:520px;border-radius:28px;overflow:hidden;box-shadow:0 30px 60px -30px rgba(31,60,70,.6)}
.photo img{width:100%;height:100%;object-fit:cover}</style>
<div class="drops"></div>
<div class="txt"><div class="n bronze">Schick</div><div class="s">MEDICAL AESTHETICS</div><div class="c">ZAHNÄRZTIN &amp; HEILPRAKTIKERIN</div>
<div class="h">Natürliche Schönheit,<br>medizinisch präzise.</div><div class="p">Dr. Karina Schick · Schloß Westerburg</div></div>
<div class="photo"><img src="${assets}/img/dr-karina-schick.jpg"></div>`;

(async () => {
  const browser = await chromium.launch();
  const shot = async (html, w, h, file, opts = {}) => {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    const tmp = path.join(os.tmpdir(), "brand-" + file + ".html");
    fs.writeFileSync(tmp, "<!doctype html><meta charset=utf-8>" + html);
    await page.goto("file://" + tmp, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(150);
    await page.screenshot({ path: out(file), omitBackground: !!opts.transparent, type: file.endsWith(".jpg") ? "jpeg" : "png", quality: file.endsWith(".jpg") ? 88 : undefined });
    await page.close();
  };
  await shot(icon(32), 32, 32, "favicon-32.png");
  await shot(icon(180), 180, 180, "apple-touch-icon.png");
  await shot(icon(192), 192, 192, "icon-192.png");
  await shot(icon(512), 512, 512, "icon-512.png");
  await shot(logo, 1000, 400, "logo.png", { transparent: true });
  await shot(og, 1200, 630, "og-image.jpg");
  await browser.close();
  console.log("ok");
})();
