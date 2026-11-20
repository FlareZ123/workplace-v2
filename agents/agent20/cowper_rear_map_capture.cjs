// @ts-check
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("playwright");

const PAGES = Array.from({ length: 31 }, (_, i) => 360 + i);
const OUT = path.resolve("out/cowper-rear-map");
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true, args: ["--disable-blink-features=AutomationControlled"] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const manifest = [];
  for (const printedPage of PAGES) {
    const url = `https://books.google.com/books?id=o7P-qis2u9IC&pg=PA${printedPage}`;
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
      const selector = `img[src*="books/content"][src*="pg=PA${printedPage}"]`;
      await page.locator(selector).first().waitFor({ state: "attached", timeout: 12000 });
      await page.waitForFunction((sel) => {
        const img = document.querySelector(sel);
        return img && img.complete && img.naturalWidth > 500 && img.naturalHeight > 700;
      }, selector, { timeout: 12000 });
      const src = await page.locator(selector).first().getAttribute("src");
      if (!src) throw new Error("No signed image URL");
      const response = await page.request.get(src, { timeout: 30000 });
      if (!response.ok()) throw new Error(`image HTTP ${response.status()}`);
      const bytes = await response.body();
      if (bytes.length < 30000) throw new Error(`small image: ${bytes.length} bytes`);
      const digest = crypto.createHash("sha256").update(bytes).digest("hex");
      const ext = bytes[0] === 0xff && bytes[1] === 0xd8 ? "jpg" :
        bytes[0] === 0x89 && bytes[1] === 0x50 ? "png" : "bin";
      const file = `p${printedPage}.${ext}`;
      fs.writeFileSync(path.join(OUT, file), bytes);
      const item = { volume: "Cowper Part II", edition: 1893, printedPage, viewerUrl: url, signedImageUrl: src, status: response.status(), bytes: bytes.length, sha256: digest, file };
      manifest.push(item);
      console.log("PAGE_CAPTURE " + JSON.stringify(item));
    } catch (e) {
      const item = { volume: "Cowper Part II", edition: 1893, printedPage, viewerUrl: url, status: "skipped", reason: String(e).slice(0, 240) };
      manifest.push(item);
      console.log("PAGE_SKIP " + JSON.stringify(item));
    }
  }
  fs.writeFileSync(path.join(OUT, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n", "utf8");
  await browser.close();
  console.log(`PAGE_CAPTURE_COMPLETE captured=${manifest.filter(x => x.file).length} attempted=${manifest.length}`);
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
