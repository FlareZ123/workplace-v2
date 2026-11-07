'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const https = require('node:https');
const path = require('node:path');

const SOURCE_COMMIT = '319919d550a9d5f959907ed8c75ca9509f3a56c1';
const SOURCE_BLOB_SHA1 = 'db9b00a3564514404073964b2da0e7637f8f53ec';
const SOURCE_URL = 'https://raw.githubusercontent.com/GITenberg/The-Riddle-of-the-Sands_2360/' + SOURCE_COMMIT + '/2360.txt';
const ROOT = path.resolve(__dirname, '..', '..');

/**
 * Download the pinned public-domain source.
 * @param {string} url
 * @returns {Promise<Buffer>}
 */
function download(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        response.resume();
        reject(new Error('Source download returned HTTP ' + response.statusCode));
        return;
      }
      const chunks = [];
      response.on('data', (chunk) => chunks.push(chunk));
      response.on('end', () => resolve(Buffer.concat(chunks)));
      response.on('error', reject);
    }).on('error', reject);
  });
}

/**
 * Apply the K08 route's ASCII normalization.
 * @param {string} value
 * @returns {string}
 */
function normalize(value) {
  return value.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').trim().replace(/\s+/g, ' ');
}

/**
 * @param {Buffer} bytes
 * @returns {string}
 */
function gitBlobSha1(bytes) {
  const header = Buffer.from('blob ' + bytes.length + '\0', 'ascii');
  return crypto.createHash('sha1').update(Buffer.concat([header, bytes])).digest('hex');
}

/**
 * @returns {Promise<void>}
 */
async function main() {
  assert.equal(
    crypto.createHash('sha256').update('abc', 'ascii').digest('hex'),
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
  );
  assert.equal(
    crypto.createHmac('sha256', Buffer.alloc(20, 0x0b)).update('Hi There', 'ascii').digest('hex'),
    'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7',
  );

  const acceptance = JSON.parse(fs.readFileSync(path.join(ROOT, 'resources', 'acceptance.json'), 'utf8'));
  const route = JSON.parse(fs.readFileSync(path.join(ROOT, 'resources', 'evidence', 'recovery-routing.json'), 'utf8'));
  const sourceBytes = await download(SOURCE_URL);
  const actualBlobSha1 = gitBlobSha1(sourceBytes);
  assert.equal(actualBlobSha1, SOURCE_BLOB_SHA1, 'Pinned GITenberg source blob changed');

  const words = normalize(sourceBytes.toString('utf8')).split(' ');
  const key = Buffer.from(route.K08.desk_nonce, 'hex');
  const target = acceptance.slot_sha256.K08;

  const water = new Set([
    'sea', 'seas', 'water', 'waters', 'tide', 'tides', 'wave', 'waves', 'ocean',
    'shore', 'surf', 'harbour', 'harbor', 'bay', 'coast', 'coastline', 'channel',
    'sand', 'sands', 'salt', 'brine', 'foam', 'estuary', 'estuarys',
  ]);
  const time = new Set([
    'night', 'tonight', 'evening', 'midnight', 'dawn', 'daybreak', 'dusk',
    'darkness', 'dark', 'late', 'last', 'watch', 'morning', 'after', 'finish',
    'finished', 'end', 'over', 'closing', 'close', 'ending',
  ]);
  const social = new Set([
    'voice', 'voices', 'table', 'supper', 'dinner', 'meal', 'tea', 'coffee',
    'talk', 'talked', 'talking', 'conversation', 'crew', 'hands', 'room',
    'friends', 'friend', 'together', 'welcome', 'warmth', 'company', 'circle',
    'gathered', 'chat', 'chatted', 'speaking', 'speak', 'spoke', 'heard',
    'murmur', 'murmured', 'song', 'sing', 'laughter', 'laugh', 'laughing',
  ]);

  let testedWindows = 0;
  const hits = [];
  for (let start = 0; start < words.length; start += 1) {
    let motifMask = 0;
    const stop = Math.min(words.length, start + 64);
    for (let end = start; end < stop; end += 1) {
      const word = words[end];
      if (water.has(word)) motifMask |= 1;
      if (time.has(word)) motifMask |= 2;
      if (social.has(word)) motifMask |= 4;
      if (end - start + 1 < 3 || motifMask !== 7) continue;

      const phrase = words.slice(start, end + 1).join(' ');
      const tag = crypto.createHmac('sha256', key).update(phrase, 'ascii').digest().subarray(0, 16);
      const componentDigest = crypto.createHash('sha256').update(tag).digest('hex');
      testedWindows += 1;
      if (componentDigest === target) {
        hits.push({ start, end, phrase, tag: tag.toString('hex') });
      }
    }
  }

  process.stdout.write(JSON.stringify({
    source: SOURCE_URL,
    sourceCommit: SOURCE_COMMIT,
    sourceGitBlobSha1: actualBlobSha1,
    sourceBytes: sourceBytes.length,
    sourceSha256: crypto.createHash('sha256').update(sourceBytes).digest('hex'),
    normalizedWords: words.length,
    windowRule: '3-64 contiguous normalized words; at least one water, one night/time, and one social/table/voice term',
    testedWindows,
    targetK08Sha256: target,
    hits,
    controls: { sha256Abc: 'PASS', hmacRfc4231: 'PASS' },
  }, null, 2) + '\n');
}

main().catch((error) => {
  process.stderr.write((error.stack || error) + '\n');
  process.exitCode = 1;
});
