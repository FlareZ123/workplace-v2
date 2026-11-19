// @ts-check
"use strict";

/**
 * Bounded K08 probe for Praeger's 1947 third edition on Google Books.
 * Captures only the eight frozen signed WN-14 page/word pages and evaluates
 * two fixed OCR transcription views: the full scan and a central body crop.
 */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { spawnSync } = require("node:child_process");
const { chromium } = require("playwright");

const VOLUME = "uT5RAQAAIAAJ";
const COORDS = [
  [4, 154], [171, 46], [28, 222], [122, 130],
  [205, 124], [96, 35], [67, 3], [201, 26],
];
const OUT = path.resolve("work/agent22-praeger-1947");
const ROUTE = JSON.parse(fs.readFileSync("resources/evidence/recovery-routing.json", "utf8"));
const ACCEPTANCE = JSON.parse(fs.readFileSync("resources/acceptance.json", "utf8"));
const NONCE = Buffer.from(ROUTE.K08.desk_nonce, "hex");
const TARGET = ACCEPTANCE.slot_sha256.K08;

fs.mkdirSync(OUT, { recursive: true });

/** @param {string} filename @param {Buffer|string} data */
function atomicWrite(filename, data) {
  const finalPath = path.join(OUT, filename);
  const tempPath = finalPath + ".tmp";
  fs.writeFileSync(tempPath, data);
  fs.renameSync(tempPath, finalPath);
}

/** @param {string} text */
function tokens(text) {
  const normalized = text.toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
  return normalized ? normalized.split(" ") : [];
}

/** @param {string} phrase */
function evaluatePhrase(phrase) {
  const component = crypto.createHmac("sha256", NONCE).update(phrase, "utf8").digest().subarray(0, 16);
  const digest = crypto.createHash("sha256").update(component).digest("hex");
  return {
    phrase,
    component_hex: component.toString("hex").toUpperCase(),
    component_sha256: digest,
    K08: digest === TARGET ? "PASS" : "NO_MATCH",
  };
}

/** @param {string} imagePath @param {string} psm */
function ocr(imagePath, psm) {
  const result = spawnSync("tesseract", [imagePath, "stdout", "--psm", psm], {
    encoding: "utf8",
    maxBuffer: 8 * 1024 * 1024,
  });
  if (result.status !== 0) {
    throw new Error("tesseract failed: " + result.stderr);
  }
  return result.stdout;
}

/** @param {string} imagePath @param {string} cropPath */
function bodyCrop(imagePath, cropPath) {
  const identify = spawnSync("identify", ["-format", "%w %h", imagePath], { encoding: "utf8" });
  if (identify.status !== 0) throw new Error("identify failed: " + identify.stderr);
  const [width, height] = identify.stdout.trim().split(/\s+/).map(Number);
  const top = Math.floor(height * 0.12);
  const bottom = Math.floor(height * 0.05);
  const cropHeight = height - top - bottom;
  const convert = spawnSync("convert", [
    imagePath, "-crop", `${width}x${cropHeight}+0+${top}`, "+repage", cropPath,
  ], { encoding: "utf8" });
  if (convert.status !== 0) throw new Error("convert failed: " + convert.stderr);
  return { width, height, top, bottom, crop_height: cropHeight };
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ["--disable-blink-features=AutomationControlled"],
  });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  /** @type {Array<Record<string, unknown>>} */
  const manifest = [];
  try {
    for (const [printedPage] of COORDS) {
      /** @type {Record<string, unknown>} */
      const row = {
        printed_page: printedPage,
        viewer_url: `https://books.google.com/books?id=${VOLUME}&pg=PA${printedPage}`,
      };
      try {
        await page.goto(String(row.viewer_url), { waitUntil: "domcontentloaded", timeout: 60000 });
        const selector = `img[src*="books/content"][src*="id=${VOLUME}"][src*="pg=PA${printedPage}"]`;
        const locator = page.locator(selector).first();
        await locator.waitFor({ state: "attached", timeout: 30000 });
        await page.waitForFunction((sel) => {
          const element = document.querySelector(sel);
          return element instanceof HTMLImageElement &&
            element.complete &&
            element.naturalWidth > 500 &&
            element.naturalHeight > 700;
        }, selector, { timeout: 30000 });

        const dimensions = await locator.evaluate((element) => ({
          width: /** @type {HTMLImageElement} */ (element).naturalWidth,
          height: /** @type {HTMLImageElement} */ (element).naturalHeight,
        }));
        const rawUrl = await locator.getAttribute("src");
        if (!rawUrl) throw new Error("viewer exposed no signed image URL");
        const signedUrl = new URL(rawUrl, page.url());
        if (signedUrl.searchParams.get("id") !== VOLUME) throw new Error("volume mismatch");
        if (signedUrl.searchParams.get("pg") !== "PA" + printedPage) throw new Error("page mismatch");
        if (!signedUrl.searchParams.has("sig")) throw new Error("missing viewer signature");

        const response = await page.request.get(signedUrl.toString(), { timeout: 30000 });
        if (!response.ok()) throw new Error("image HTTP " + response.status());
        const contentType = response.headers()["content-type"] || "";
        if (!contentType.startsWith("image/")) throw new Error("non-image response " + contentType);
        const data = await response.body();
        if (data.length < 50000) throw new Error("image too small: " + data.length);

        const filename = `p${printedPage}.png`;
        atomicWrite(filename, data);
        Object.assign(row, {
          signed_image_url: signedUrl.toString(),
          response_status: response.status(),
          content_type: contentType,
          bytes: data.length,
          sha256: crypto.createHash("sha256").update(data).digest("hex"),
          natural_width: dimensions.width,
          natural_height: dimensions.height,
          filename,
        });
      } catch (error) {
        row.error = String(error);
      }
      manifest.push(row);
      console.log("PRAEGER_PAGE " + JSON.stringify(row));
    }
  } finally {
    await browser.close();
  }

  atomicWrite("manifest.json", JSON.stringify(manifest, null, 2) + "\n");
  const successes = manifest.filter((row) => !row.error);
  console.log(`PRAEGER_CAPTURE_COMPLETE ${successes.length}/${COORDS.length}`);
  if (successes.length !== COORDS.length) {
    process.exitCode = 2;
    return;
  }

  const hashes = successes.map((row) => String(row.sha256));
  if (new Set(hashes).size !== hashes.length) {
    throw new Error("duplicate target-page image hash");
  }

  /** @type {Record<string, string[]>} */
  const viewTokens = { full: [], body: [] };
  /** @type {Array<Record<string, unknown>>} */
  const ocrTrace = [];
  for (const [printedPage, wordIndex] of COORDS) {
    const imagePath = path.join(OUT, `p${printedPage}.png`);
    const cropPath = path.join(OUT, `p${printedPage}.body.png`);
    const crop = bodyCrop(imagePath, cropPath);
    const fullText = ocr(imagePath, "6");
    const bodyText = ocr(cropPath, "6");
    atomicWrite(`p${printedPage}.full.txt`, fullText);
    atomicWrite(`p${printedPage}.body.txt`, bodyText);

    /** @type {Record<string, unknown>} */
    const trace = { printed_page: printedPage, word_index: wordIndex, crop };
    for (const [name, text] of [["full", fullText], ["body", bodyText]]) {
      const pageTokens = tokens(text);
      trace[name + "_token_count"] = pageTokens.length;
      trace[name + "_word"] = wordIndex <= pageTokens.length ? pageTokens[wordIndex - 1] : null;
      if (wordIndex > pageTokens.length) {
        throw new Error(`${name} OCR page ${printedPage} has ${pageTokens.length} words, needs ${wordIndex}`);
      }
      viewTokens[name].push(pageTokens[wordIndex - 1]);
    }
    ocrTrace.push(trace);
  }

  const evaluations = Object.fromEntries(
    Object.entries(viewTokens).map(([name, selected]) => [name, evaluatePhrase(selected.join(" "))])
  );
  const result = {
    volume_id: VOLUME,
    edition: "Methuen 1947 third edition",
    coordinates: COORDS,
    ocr_trace: ocrTrace,
    evaluations,
    target_sha256: TARGET,
  };
  atomicWrite("result.json", JSON.stringify(result, null, 2) + "\n");
  console.log("PRAEGER_RESULT " + JSON.stringify(result));
  if (Object.values(evaluations).some((value) => value.K08 === "PASS")) {
    console.log("PRAEGER_K08_PASS");
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
