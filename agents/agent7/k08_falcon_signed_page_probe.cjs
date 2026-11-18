// @ts-check
"use strict";

/** Probe the Google Books viewer for the signed 1889 Falcon image behind printed page 4. */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("playwright");

const VOLUME = "fQYN_SZzCFgC";
const PRINTED_PAGE = 4;
const OUT = path.resolve("work/agent7-falcon-viewer-probe");
fs.mkdirSync(OUT, { recursive: true });

/**
 * @param {string} filename
 * @param {Buffer|string} data
 */
function atomicWrite(filename, data) {
  const finalPath = path.join(OUT, filename);
  const tempPath = finalPath + ".tmp";
  fs.writeFileSync(tempPath, data);
  fs.renameSync(tempPath, finalPath);
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ["--disable-blink-features=AutomationControlled"],
  });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const viewerUrl = `https://books.google.com/books?id=${VOLUME}&pg=PA${PRINTED_PAGE}`;
  /** @type {Array<Record<string, unknown>>} */
  const records = [];
  try {
    await page.goto(viewerUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(7000);
    const images = await page.locator("img").evaluateAll((nodes) => nodes.map((node) => ({
      src: node instanceof HTMLImageElement ? node.src : "",
      naturalWidth: node instanceof HTMLImageElement ? node.naturalWidth : 0,
      naturalHeight: node instanceof HTMLImageElement ? node.naturalHeight : 0,
      alt: node instanceof HTMLImageElement ? node.alt : "",
    })));
    for (const image of images) {
      if (!image.src.includes("books/content")) continue;
      /** @type {Record<string, unknown>} */
      const record = { ...image };
      try {
        const response = await page.request.get(image.src, { timeout: 30000 });
        const body = await response.body();
        const hash = crypto.createHash("sha256").update(body).digest("hex");
        Object.assign(record, {
          status: response.status(),
          contentType: response.headers()["content-type"] || null,
          bytes: body.length,
          sha256: hash,
        });
        if (response.ok() && (response.headers()["content-type"] || "").startsWith("image/")) {
          const filename = `page4-${hash.slice(0, 16)}.img`;
          atomicWrite(filename, body);
          record.filename = filename;
        }
      } catch (error) {
        record.fetchError = String(error);
      }
      records.push(record);
    }
    const summary = {
      viewerUrl,
      finalUrl: page.url(),
      title: await page.title(),
      imageCount: images.length,
      booksContentCount: records.length,
      records,
    };
    atomicWrite("summary.json", JSON.stringify(summary, null, 2) + "\n");
    console.log("FALCON_VIEWER_PROBE " + JSON.stringify(summary));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
