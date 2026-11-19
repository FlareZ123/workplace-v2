// @ts-check
"use strict";

/**
 * Capture every viewer-generated signed image in the frozen 1889 Falcon
 * scan-index union. A scan index is not assumed to equal a printed folio.
 */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("playwright");

const VOLUME = "fQYN_SZzCFgC";
const PAGE_COUNT = 308;
const SCAN_RANGES = [[0, 43], [55, 79], [84, 108], [110, 251]];
const SCAN_INDICES = SCAN_RANGES.flatMap(([first, last]) =>
  Array.from({ length: last - first + 1 }, (_, offset) => first + offset)
);
const TARGET_PRINTED_PAGES = [
  4, 28, 30, 31, 67, 96, 122, 143,
  151, 171, 180, 201, 205, 215, 229, 239
];
const OUT = path.resolve("work/agent7-falcon-signed-dual");
const LOCK = path.resolve("work/.agent7-falcon-signed-dual.capture.lock");
const MIN_IMAGE_BYTES = 50000;
const MIN_WIDTH = 500;
const MIN_HEIGHT = 700;

function atomicWrite(filename, data) {
  const finalPath = path.join(OUT, filename);
  const tempPath = finalPath + ".tmp";
  fs.writeFileSync(tempPath, data);
  fs.renameSync(tempPath, finalPath);
}

function sha256(data) {
  return crypto.createHash("sha256").update(data).digest("hex");
}

function buildManifest(records, permitComplete) {
  const failures = records.filter((row) => row.error);
  const byHash = new Map();
  for (const row of records) {
    if (row.error) continue;
    const prior = byHash.get(row.sha256) || [];
    prior.push(row.scan_index);
    byHash.set(row.sha256, prior);
  }
  const duplicateImageHashes = [...byHash.entries()]
    .filter(([, indices]) => indices.length > 1)
    .map(([sha256Value, indices]) => ({ sha256: sha256Value, scan_indices: indices }));
  const structurallyComplete = failures.length === 0 &&
    duplicateImageHashes.length === 0 &&
    records.length === SCAN_INDICES.length;
  return {
    volume_id: VOLUME,
    published_date: "1889",
    page_count: PAGE_COUNT,
    zoom: 3,
    scan_index_ranges: SCAN_RANGES,
    scan_indices: SCAN_INDICES,
    target_printed_pages: TARGET_PRINTED_PAGES,
    records,
    failed_scan_indices: failures.map((row) => row.scan_index),
    duplicate_image_hashes: duplicateImageHashes,
    complete: permitComplete && structurallyComplete,
    captured_at: new Date().toISOString()
  };
}

async function captureScanIndexAttempt(page, scanIndex, attempt) {
  const viewerUrl = "https://books.google.com/books?id=" + VOLUME + "&pg=PA" + scanIndex;
  const row = { scan_index: scanIndex, viewer_url: viewerUrl, zoom: 3, attempt };
  try {
    const responsePromise = page.waitForResponse((response) => {
      try {
        const url = new URL(response.url());
        return url.pathname.includes("/books/content") &&
          url.searchParams.get("id") === VOLUME &&
          url.searchParams.get("pg") === "PA" + scanIndex &&
          url.searchParams.get("zoom") === "3" &&
          url.searchParams.has("sig");
      } catch {
        return false;
      }
    }, { timeout: 60000 }).then(
      (response) => ({ response }),
      (error) => ({ error })
    );
    let navigationError = null;
    try {
      await page.goto(viewerUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
    } catch (error) {
      navigationError = error;
    }
    const responseResult = await responsePromise;
    if (navigationError) {
      throw navigationError;
    }
    if (responseResult.error) {
      throw responseResult.error;
    }
    const imageResponse = responseResult.response;
    row.response_url = imageResponse.url();
    row.response_status = imageResponse.status();
    row.response_content_type = imageResponse.headers()["content-type"] || "";
    if (!imageResponse.ok()) {
      throw new Error("signed viewer image response returned HTTP " + imageResponse.status());
    }
    await page.waitForFunction(({ index, minWidth, minHeight }) => {
      const images = [...document.querySelectorAll('img[src*="/books/content"]')];
      return images.some((element) => {
        if (!(element instanceof HTMLImageElement)) return false;
        const url = new URL(element.src, location.href);
        return url.searchParams.get("pg") === "PA" + index &&
          element.complete &&
          element.naturalWidth > minWidth &&
          element.naturalHeight > minHeight;
      });
    }, { index: scanIndex, minWidth: MIN_WIDTH, minHeight: MIN_HEIGHT }, {
      timeout: 60000,
      polling: 250
    });

    const imageInfo = await page.evaluate((index) => {
      const images = [...document.querySelectorAll('img[src*="/books/content"]')];
      const element = images.find((candidate) => {
        if (!(candidate instanceof HTMLImageElement)) return false;
        const url = new URL(candidate.src, location.href);
        return url.searchParams.get("pg") === "PA" + index;
      });
      if (!(element instanceof HTMLImageElement)) return null;
      return {
        src: element.src,
        naturalWidth: element.naturalWidth,
        naturalHeight: element.naturalHeight,
        complete: element.complete
      };
    }, scanIndex);
    if (!imageInfo || !imageInfo.src || !imageInfo.complete) {
      throw new Error("viewer image element is incomplete or absent");
    }

    const signedUrl = new URL(imageInfo.src, page.url());
    const params = signedUrl.searchParams;
    if (!["books.google.com", "books.google.es"].includes(signedUrl.hostname)) {
      throw new Error("signed image URL has an unexpected host");
    }
    if (!signedUrl.pathname.includes("/books/content")) {
      throw new Error("viewer did not expose a Books content image URL");
    }
    if (params.get("id") !== VOLUME || params.get("pg") !== "PA" + scanIndex) {
      throw new Error("signed image URL volume/page identity mismatch");
    }
    if (!params.get("sig")) {
      throw new Error("viewer image URL has no signature");
    }
    if (params.get("zoom") !== "3") {
      throw new Error("viewer did not expose the required full-resolution zoom=3 image");
    }

    const responseUrl = new URL(imageResponse.url());
    if (responseUrl.hostname !== signedUrl.hostname || responseUrl.pathname !== signedUrl.pathname) {
      throw new Error("captured viewer response host/path differs from the inspected signed URL");
    }
    const responseParameters = [...responseUrl.searchParams.entries()]
      .sort(([leftKey, leftValue], [rightKey, rightValue]) =>
        leftKey.localeCompare(rightKey) || leftValue.localeCompare(rightValue)
      );
    const signedParameters = [...signedUrl.searchParams.entries()]
      .sort(([leftKey, leftValue], [rightKey, rightValue]) =>
        leftKey.localeCompare(rightKey) || leftValue.localeCompare(rightValue)
      );
    if (JSON.stringify(responseParameters) !== JSON.stringify(signedParameters)) {
      throw new Error("captured viewer response query differs from the image element signed URL");
    }
    const contentType = imageResponse.headers()["content-type"] || "";
    if (!contentType.startsWith("image/")) {
      throw new Error("signed viewer response returned " + contentType);
    }
    const data = await imageResponse.body();
    if (data.length < MIN_IMAGE_BYTES) {
      throw new Error("placeholder-sized signed image response: " + data.length + " bytes");
    }

    const filename = "scan-" + String(scanIndex).padStart(3, "0") + ".img";
    atomicWrite(filename, data);
    Object.assign(row, {
      final_viewer_url: page.url(),
      signed_image_url: signedUrl.toString(),
      response_url: imageResponse.url(),
      response_status: imageResponse.status(),
      content_type: contentType,
      bytes: data.length,
      sha256: sha256(data),
      filename,
      natural_width: imageInfo.naturalWidth,
      natural_height: imageInfo.naturalHeight,
      captured_at: new Date().toISOString()
    });
  } catch (error) {
    row.error = String(error);
  }
  return row;
}

function isTransientCaptureError(message) {
  return /\bHTTP (?:429|500|502|503|504)\b/.test(message) ||
    /net::ERR_(?:CONNECTION_RESET|TIMED_OUT|NETWORK_CHANGED|INTERNET_DISCONNECTED|CONNECTION_CLOSED|CONNECTION_ABORTED|NAME_NOT_RESOLVED|ADDRESS_UNREACHABLE|ABORTED)/i.test(message) ||
    /\b(?:ECONNRESET|ECONNREFUSED|EAI_AGAIN|ETIMEDOUT)\b|socket hang up|connection reset|connection closed|Timeout \d+ms exceeded|Navigation timeout of \d+ms exceeded/i.test(message);
}

async function captureScanIndex(page, scanIndex) {
  const first = await captureScanIndexAttempt(page, scanIndex, 1);
  if (!first.error || !isTransientCaptureError(first.error)) {
    first.attempts = 1;
    console.log("FALCON_SIGNED_SCAN " + JSON.stringify(first));
    return first;
  }
  await page.waitForTimeout(1500);
  const retry = await captureScanIndexAttempt(page, scanIndex, 2);
  retry.attempts = 2;
  retry.first_attempt = first;
  retry.first_attempt_error = first.error;
  console.log("FALCON_SIGNED_SCAN " + JSON.stringify(retry));
  return retry;
}

(async () => {
  // Acquire a stable lock outside OUT before deleting or recreating OUT.
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  const lockFd = fs.openSync(LOCK, "wx");
  let browser = null;
  const records = [];
  try {
    fs.rmSync(OUT, { recursive: true, force: true });
    fs.mkdirSync(OUT, { recursive: true });
    atomicWrite("manifest.json", JSON.stringify(buildManifest([], false), null, 2) + "\n");
    browser = await chromium.launch({
      headless: true,
      args: ["--disable-blink-features=AutomationControlled"]
    });
    const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
    for (const scanIndex of SCAN_INDICES) {
      records.push(await captureScanIndex(page, scanIndex));
      atomicWrite("manifest.json", JSON.stringify(buildManifest(records, false), null, 2) + "\n");
    }

    const manifest = buildManifest(records, true);
    const failures = records.filter((row) => row.error);
    const duplicateImageHashes = manifest.duplicate_image_hashes;
    atomicWrite("manifest.json", JSON.stringify(manifest, null, 2) + "\n");
    console.log("FALCON_SIGNED_SCAN_MANIFEST " + JSON.stringify({
      volume_id: VOLUME,
      scan_indices: records.length,
      failed_scan_indices: manifest.failed_scan_indices,
      duplicate_image_hashes: duplicateImageHashes,
      complete: manifest.complete
    }));

    if (!manifest.complete) {
      throw new Error(
        "full-window signed capture incomplete: " +
        failures.length + " failures, " +
        duplicateImageHashes.length + " repeated-image groups"
      );
    }
    console.log("FALCON_SIGNED_SCAN_SET_COMPLETE " + SCAN_INDICES.length);
  } finally {
    try {
      if (browser) await browser.close();
    } finally {
      fs.closeSync(lockFd);
      fs.unlinkSync(LOCK);
    }
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
