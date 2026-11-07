// @ts-check
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const OUT = path.resolve("cowper-browser");
fs.mkdirSync(OUT, { recursive: true });

/**
 * @param {string} name
 * @param {string} url
 */
async function probe(name, url) {
  const folder = path.join(OUT, name);
  fs.mkdirSync(folder, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    args: ["--disable-blink-features=AutomationControlled"],
  });
  const page = await browser.newPage({
    viewport: { width: 1400, height: 1000 },
    deviceScaleFactor: 1,
  });
  const imageTasks = [];
  const network = [];
  page.on("response", (response) => {
    imageTasks.push((async () => {
      const headers = response.headers();
      const contentType = headers["content-type"] || "";
      const resourceType = response.request().resourceType();
      const entry = {
        status: response.status(),
        url: response.url(),
        resourceType,
        contentType,
      };
      network.push(entry);
      if (contentType.startsWith("image/") && response.status() === 200) {
        const body = await response.body();
        const ext = contentType.includes("png") ? "png" : contentType.includes("jpeg") ? "jpg" : "bin";
        const filename = `network-${network.length}.${ext}`;
        fs.writeFileSync(path.join(folder, filename), body);
        entry.saved = filename;
        entry.bytes = body.length;
      }
    })());
  });
  let status = null;
  let navigationError = null;
  try {
    const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
    status = response?.status() ?? null;
    await page.waitForTimeout(10000);
  } catch (error) {
    navigationError = String(error);
  }
  await Promise.allSettled(imageTasks);
  const dom = await page.evaluate(() => {
    const images = Array.from(document.images).map((img) => ({
      src: img.currentSrc || img.src,
      width: img.naturalWidth,
      height: img.naturalHeight,
      complete: img.complete,
      alt: img.alt,
    }));
    const canvases = Array.from(document.querySelectorAll("canvas")).map((c) => ({
      width: c.width,
      height: c.height,
      rect: c.getBoundingClientRect().toJSON(),
    }));
    const backgrounds = Array.from(document.querySelectorAll("*"))
      .map((el) => getComputedStyle(el).backgroundImage)
      .filter((value) => value && value !== "none")
      .slice(0, 100);
    return {
      title: document.title,
      url: location.href,
      bodyText: (document.body?.innerText || "").slice(0, 4000),
      images,
      canvases,
      backgrounds,
    };
  });
  fs.writeFileSync(path.join(folder, "viewer.html"), await page.content(), "utf8");
  await page.screenshot({ path: path.join(folder, "screenshot.png"), fullPage: true });
  const result = { name, requestedUrl: url, status, navigationError, dom, network };
  fs.writeFileSync(path.join(folder, "result.json"), JSON.stringify(result, null, 2), "utf8");
  console.log("BROWSER_RESULT " + JSON.stringify(result));
  await browser.close();
}

(async () => {
  await probe("google_part2_p130", "https://books.google.com/books?id=o7P-qis2u9IC&pg=PA130");
  await probe("hathi_part1_seq1", "https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p&view=1up&seq=1");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
