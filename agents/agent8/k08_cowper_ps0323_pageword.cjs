"use strict";
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("playwright");

const BOOK_ID = "o7P-qis2u9IC";
const PAGES = [121, 229, 118, 211, 56, 125, 50, 148, 110];
const OUT = path.resolve("results/assets/cowper/part2-ps0323");
fs.mkdirSync(OUT, { recursive: true });

function pngDimensions(data) {
  if (data.length < 24 || !data.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) {
    throw new Error("Viewer response is not a PNG");
  }
  return [data.readUInt32BE(16), data.readUInt32BE(20)];
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ["--disable-blink-features=AutomationControlled"] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const manifest = [];
  try {
    for (const printedPage of PAGES) {
      const viewerUrl = "https://books.google.com/books?id=" + BOOK_ID + "&pg=PA" + printedPage;
      await page.goto(viewerUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
      const selector = 'img[src*="books/content"][src*="pg=PA' + printedPage + '"]';
      const locator = page.locator(selector).first();
      await locator.waitFor({ state: "attached", timeout: 30000 });
      await page.waitForFunction((sel) => {
        const el = document.querySelector(sel);
        return el instanceof HTMLImageElement && el.complete && el.naturalWidth > 500 && el.naturalHeight > 700;
      }, selector, { timeout: 30000 });
      const rawUrl = await locator.getAttribute("src");
      if (!rawUrl) throw new Error("No signed image URL for page " + printedPage);
      const signedUrl = new URL(rawUrl, page.url()).toString();
      const response = await page.request.get(signedUrl, { timeout: 30000 });
      if (!response.ok()) throw new Error("Image status " + response.status() + " for page " + printedPage);
      const bytes = await response.body();
      if (bytes.length < 50000) throw new Error("Suspiciously small page image for page " + printedPage + ": " + bytes.length);
      const dimensions = pngDimensions(bytes);
      const filename = "p" + printedPage + ".png";
      fs.writeFileSync(path.join(OUT, filename), bytes);
      const item = {
        printed_page: printedPage,
        viewer_url: viewerUrl,
        signed_image_url: signedUrl,
        status: response.status(),
        content_type: response.headers()["content-type"] || null,
        filename,
        bytes: bytes.length,
        sha256: crypto.createHash("sha256").update(bytes).digest("hex"),
        png_dimensions: dimensions
      };
      manifest.push(item);
      console.log("PS0323_COWPER_PAGE " + JSON.stringify(item));
    }
    fs.writeFileSync(path.join(OUT, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n", "utf8");
    console.log("PS0323_COWPER_CAPTURE_COMPLETE " + manifest.length + "/" + PAGES.length);
  } finally {
    await browser.close();
    if (manifest.length) {
      fs.writeFileSync(path.join(OUT, "manifest.partial.json"), JSON.stringify(manifest, null, 2) + "\n", "utf8");
    }
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});