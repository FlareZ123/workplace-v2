// @ts-check
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("playwright");

const PAGES = [121, 130, 135, 142, 151];
const OUT = path.resolve("results/assets/cowper/part2-1893");
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true, args: ["--disable-blink-features=AutomationControlled"] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const manifest = [];
  for (const printedPage of PAGES) {
    const url = `https://books.google.com/books?id=o7P-qis2u9IC&pg=PA${printedPage}`;
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
    const selector = `img[src*="books/content"][src*="pg=PA${printedPage}"]`;
    await page.locator(selector).first().waitFor({ state: "attached", timeout: 30000 });
    await page.waitForFunction((sel) => {
      const img = document.querySelector(sel);
      return img && img.complete && img.naturalWidth > 500 && img.naturalHeight > 700;
    }, selector, { timeout: 30000 });
    const src = await page.locator(selector).first().getAttribute("src");
    if (!src) throw new Error(`No signed image URL for page ${printedPage}`);
    const response = await page.request.get(src, { timeout: 30000 });
    if (!response.ok()) throw new Error(`Image request failed for p.${printedPage}: ${response.status()}`);
    const bytes = await response.body();
    if (bytes.length < 50000) throw new Error(`Suspiciously small page image for p.${printedPage}: ${bytes.length} bytes`);
    const digest = crypto.createHash("sha256").update(bytes).digest("hex");
    const ext = src.includes("img=1") ? "img" : "bin";
    const stem = `p${printedPage}`;
    fs.writeFileSync(path.join(OUT, `${stem}.${ext}`), bytes);
    fs.writeFileSync(path.join(OUT, `${stem}.b64`), bytes.toString("base64") + "\n", "utf8");
    const item = { volume: "Part II", edition: 1893, printedPage, viewerUrl: url, signedImageUrl: src, status: response.status(), bytes: bytes.length, sha256: digest, base64File: `${stem}.b64` };
    manifest.push(item);
    console.log("PAGE_CAPTURE " + JSON.stringify(item));
  }
  fs.writeFileSync(path.join(OUT, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n", "utf8");
  await browser.close();
  console.log(`PAGE_CAPTURE_COMPLETE count=${manifest.length}`);
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
