// @ts-check
"use strict";
/** Capture exactly the signed Google Books pages of the frozen WN-14 hypothesis. */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("playwright");
const PAGES = [121, 4, 171, 28, 122, 205, 96, 67, 201];
const OUT = path.resolve("results/assets/cowper/part2-wn14/captured");
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true, args: ["--disable-blink-features=AutomationControlled"] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  /** @type {Array<Record<string, unknown>>} */
  const manifest = [];
  try {
    for (const pageNumber of PAGES) {
      /** @type {Record<string, unknown>} */
      const item = { printed_page: pageNumber, viewer_url: `https://books.google.com/books?id=o7P-qis2u9IC&pg=PA${pageNumber}` };
      try {
        await page.goto(String(item.viewer_url), { waitUntil: "domcontentloaded", timeout: 60000 });
        const selector = `img[src*="books/content"][src*="pg=PA${pageNumber}"]`;
        const locator = page.locator(selector).first();
        await locator.waitFor({ state: "attached", timeout: 30000 });
        await page.waitForFunction(sel => {
          const el = document.querySelector(sel);
          return el instanceof HTMLImageElement && el.complete && el.naturalWidth > 500 && el.naturalHeight > 700;
        }, selector, { timeout: 30000 });
        const rawUrl = await locator.getAttribute("src");
        if (!rawUrl) throw new Error("No signed image URL");
        const url = new URL(rawUrl, page.url()).toString();
        const response = await page.request.get(url, { timeout: 30000 });
        if (!response.ok()) throw new Error(`Image status ${response.status()}`);
        const data = await response.body();
        const filename = `p${pageNumber}.img`;
        const temp = path.join(OUT, filename + ".tmp");
        fs.writeFileSync(temp, data);
        fs.renameSync(temp, path.join(OUT, filename));
        Object.assign(item, {
          signed_image_url: url, status: response.status(),
          content_type: response.headers()["content-type"] || null,
          filename, bytes: data.length,
          sha256: crypto.createHash("sha256").update(data).digest("hex")
        });
      } catch (error) {
        item.error = String(error);
      }
      manifest.push(item);
      console.log("FROZEN_COWPER_PAGE " + JSON.stringify(item));
    }
  } finally {
    await browser.close();
    const temp = path.join(OUT, "manifest.json.tmp");
    fs.writeFileSync(temp, JSON.stringify(manifest, null, 2) + "\n", "utf8");
    fs.renameSync(temp, path.join(OUT, "manifest.json"));
  }
  console.log("FROZEN_COWPER_PAGE_SET_COMPLETE " + manifest.filter(x => !x.error).length + "/" + PAGES.length);
})().catch(error => { console.error(error); process.exitCode = 1; });
