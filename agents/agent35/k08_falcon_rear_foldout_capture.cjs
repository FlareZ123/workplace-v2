// @ts-check
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("playwright");

const VOLUME = "fQYN_SZzCFgC";
const INDICES = Array.from({ length: 56 }, (_, i) => i + 252);
const OUT = path.resolve("work/agent35-falcon-rear-foldout");
fs.mkdirSync(OUT, { recursive: true });

function atomicWrite(filename, data) {
  const finalPath = path.join(OUT, filename);
  const tempPath = finalPath + ".tmp";
  fs.writeFileSync(tempPath, data);
  fs.renameSync(tempPath, finalPath);
}
function sha256(data) {
  return crypto.createHash("sha256").update(data).digest("hex");
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ["--disable-blink-features=AutomationControlled"],
  });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1100 } });
  const records = [];
  try {
    for (const scanIndex of INDICES) {
      const viewerUrl = `https://books.google.com/books?id=${VOLUME}&pg=PA${scanIndex}`;
      const row = { scan_index: scanIndex, viewer_url: viewerUrl };
      try {
        await page.goto(viewerUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
        const selector = `img[src*="books/content"][src*="pg=PA${scanIndex}"]`;
        const locator = page.locator(selector).first();
        await locator.waitFor({ state: "attached", timeout: 30000 });
        await page.waitForFunction((sel) => {
          const element = document.querySelector(sel);
          return element instanceof HTMLImageElement &&
            element.complete && element.naturalWidth > 300 && element.naturalHeight > 300;
        }, selector, { timeout: 30000 });
        const dims = await locator.evaluate((element) => ({
          width: element.naturalWidth,
          height: element.naturalHeight,
        }));
        const src = await locator.getAttribute("src");
        if (!src) throw new Error("viewer exposed no signed image URL");
        const signedUrl = new URL(src, page.url());
        if (signedUrl.searchParams.get("id") !== VOLUME ||
            signedUrl.searchParams.get("pg") !== `PA${scanIndex}` ||
            !signedUrl.searchParams.get("sig")) {
          throw new Error("signed URL identity/signature mismatch");
        }
        const response = await page.request.get(signedUrl.toString(), { timeout: 30000 });
        if (!response.ok()) throw new Error(`signed image status ${response.status()}`);
        const contentType = response.headers()["content-type"] || "";
        if (!contentType.startsWith("image/")) throw new Error(`non-image ${contentType}`);
        const data = await response.body();
        if (data.length < 20000) throw new Error(`small image ${data.length}`);
        const landscape = dims.width > dims.height;
        let filename = null;
        if (landscape) {
          filename = `pa${scanIndex}.img`;
          atomicWrite(filename, data);
        }
        Object.assign(row, {
          final_viewer_url: page.url(),
          signed_image_url: signedUrl.toString(),
          content_type: contentType,
          bytes: data.length,
          sha256: sha256(data),
          natural_width: dims.width,
          natural_height: dims.height,
          landscape,
          filename,
        });
      } catch (error) {
        row.error = String(error);
      }
      records.push(row);
      console.log("FALCON_REAR_SCAN " + JSON.stringify(row));
    }
  } finally {
    await browser.close();
  }
  const landscapes = records.filter((row) => row.landscape);
  atomicWrite("manifest.json", JSON.stringify({
    volume_id: VOLUME,
    scan_indices: INDICES,
    records,
    landscape_records: landscapes,
    landscape_count: landscapes.length,
  }, null, 2) + "\n");
  console.log("FALCON_REAR_LANDSCAPES " + JSON.stringify(landscapes));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
