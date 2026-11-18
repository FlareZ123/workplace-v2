// @ts-check
"use strict";

/**
 * Capture the exact signed Google Books page images for the frozen 1889 Falcon
 * K08 coordinate sets. The viewer, rather than an unsigned books/content URL,
 * supplies the page-image signature.
 */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("playwright");

const VOLUME = "fQYN_SZzCFgC";
const PAGES = [4, 28, 30, 31, 67, 96, 122, 143, 151, 171, 180, 201, 205, 215, 229, 239];
const OUT = path.resolve("work/agent7-falcon-signed-dual");
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

/**
 * @param {Buffer} data
 * @returns {string}
 */
function sha256(data) {
  return crypto.createHash("sha256").update(data).digest("hex");
}

(async () => {
  const lockPath = path.join(OUT, ".capture.lock");
  const lockFd = fs.openSync(lockPath, "wx");
  const browser = await chromium.launch({
    headless: true,
    args: ["--disable-blink-features=AutomationControlled"],
  });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  /** @type {Array<Record<string, unknown>>} */
  const manifest = [];
  try {
    for (const printedPage of PAGES) {
      const viewerUrl = `https://books.google.com/books?id=${VOLUME}&pg=PA${printedPage}`;
      /** @type {Record<string, unknown>} */
      const row = { printed_page: printedPage, viewer_url: viewerUrl };
      try {
        await page.goto(viewerUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
        const selector = `img[src*="books/content"][src*="pg=PA${printedPage}"]`;
        const locator = page.locator(selector).first();
        await locator.waitFor({ state: "attached", timeout: 30000 });
        await page.waitForFunction((sel) => {
          const element = document.querySelector(sel);
          return element instanceof HTMLImageElement &&
            element.complete &&
            element.naturalWidth > 500 &&
            element.naturalHeight > 700;
        }, selector, { timeout: 30000 });

        const src = await locator.getAttribute("src");
        if (!src) throw new Error("viewer did not expose a signed image URL");
        const signedUrl = new URL(src, page.url());
        if (signedUrl.searchParams.get("id") !== VOLUME) {
          throw new Error("signed page belongs to the wrong Google Books volume");
        }
        if (signedUrl.searchParams.get("pg") !== `PA${printedPage}`) {
          throw new Error("signed page label differs from the requested printed page");
        }
        if (!signedUrl.searchParams.get("sig")) {
          throw new Error("viewer image URL has no signature");
        }

        const response = await page.request.get(signedUrl.toString(), { timeout: 30000 });
        if (!response.ok()) throw new Error(`signed image status ${response.status()}`);
        const contentType = response.headers()["content-type"] || "";
        if (!contentType.startsWith("image/")) {
          throw new Error(`signed page returned ${contentType}`);
        }
        const data = await response.body();
        if (data.length < 50000) {
          throw new Error(`signed page is unexpectedly small: ${data.length} bytes`);
        }

        const filename = `p${printedPage}.img`;
        atomicWrite(filename, data);
        Object.assign(row, {
          final_viewer_url: page.url(),
          signed_image_url: signedUrl.toString(),
          content_type: contentType,
          bytes: data.length,
          sha256: sha256(data),
          filename,
        });
      } catch (error) {
        row.error = String(error);
      }
      manifest.push(row);
      console.log("FALCON_SIGNED_PAGE " + JSON.stringify(row));
    }

    const failures = manifest.filter((row) => row.error);
    atomicWrite("manifest.json", JSON.stringify({
      volume_id: VOLUME,
      pages: PAGES,
      records: manifest,
      complete: failures.length === 0,
    }, null, 2) + "\n");

    if (failures.length !== 0) {
      throw new Error(`${failures.length} signed page acquisitions failed`);
    }
    const hashes = new Set(manifest.map((row) => row.sha256));
    if (hashes.size !== PAGES.length) {
      throw new Error("two requested pages returned identical source bytes");
    }
    console.log(`FALCON_SIGNED_PAGE_SET_COMPLETE ${PAGES.length}/${PAGES.length}`);
  } finally {
    await browser.close();
    fs.closeSync(lockFd);
    fs.unlinkSync(lockPath);
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
