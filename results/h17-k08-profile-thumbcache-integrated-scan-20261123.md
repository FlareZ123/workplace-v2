# K08 profile thumbnail-cache integrated scan (2026-11-23)

## Question

Can the authorized read-only profile scanner test the source-literal K08 teal-bit layouts in intact images carved from Windows thumbnail-cache databases, without writing to the profile or falsely asserting an N14/Emily source link?

## Result

**The intake gap is closed and the synthetic end-to-end controls pass. No H-17 phrase was recovered from the supplied local export.**

Before this change, `work/h17_profile_k08_phrase_scan.py` explicitly reported that thumbnail-cache image payloads were not decoded and required a separate manual carve/scan sequence. The standalone components already existed, but the profile workflow did not connect them.

The profile scanner now:
1. Consumes only inventory entries admitted by its existing profile-metadata allowlist (`thumbcache*`, `Thumbs.db`, `ehthumbs.db`).
2. Verifies inventory size and SHA-256 before reading the cache bytes.
3. Uses `work/h17_thumbcache_image_carve.py`'s in-memory `carve_bytes` function to recover intact JPEG, PNG, GIF, BMP and WebP payloads. No extracted files are written to the profile or to a temporary directory.
4. Verifies each carved image's exact length and SHA-256, then passes its bytes to the new `scan_image_bytes` entry point in `work/h17_k08_teal_bit_image_scan.py`.
5. Tests only the two frozen source-literal layouts: `teal-mask-green-low-if-even` and `teal-mask-blue-low-if-even`. Candidate text is checked against the unchanged K08 HMAC16/SHA-256 commitment.
6. Reuses scans for byte-identical images and reports explicit limits: 32 MiB per image, 25 million pixels per image, and 4,096 unique images per profile scan.

Every thumbnail-cache hit records the cache path, byte offset, carved-image SHA-256, frame, layout and exact phrase. It also explicitly records that the original image path/time and the N14-to-Emily caption relationship remain unresolved. A cryptographic hit is not historical authentication.

## Validation

The new `tests/test_h17_profile_k08_thumbcache_bridge.py` exercises:
- A synthetic teal-bit phrase embedded in two cache files: both occurrences are reported, while identical image bytes are decoded once.
- Source-cache SHA-256 preservation before and after scanning.
- A generic green-LSB image outside the source-literal teal mask: no admitted hit.
- An inventory SHA mismatch: the cache is skipped before carving or image scanning.

The existing `tests/test_h17_k08_teal_bit_image_scan.py` and the profile scanner's `--self-test` also ran successfully.

- GitHub Actions workflow: [Agent 25 K08 profile thumbnail-cache bridge](https://github.com/FlareZ123/workplace-v2/actions/runs/45091655484)
- Run: `45091655484`
- Result: success; decoder tests, bridge tests and profile-scanner self-test all completed successfully.

## Application to the supplied archive

The uploaded `h17-archive-dump.zip` contains 46 non-directory members, no standalone image members, and no `thumbcache*`, `Thumbs.db` or `ehthumbs.db` member. There is therefore no original profile-cache image in this export to test. This change does not produce a candidate phrase and does not change K08's unresolved status.

## Limitations and next useful input

The byte-carver is intentionally not a forensic parser for the thumbnail-cache index. It does not recover the original file path, capture timestamp, thumbnail database record identity, or the image's relationship to N14 and Emily's final caption. Those relationships must come from a preserved index or another source record; they must not be inferred from an HMAC hit.

If an already-authorized read-only profile-refresh package becomes available, run `work/h17_profile_inventory.py` and then `work/h17_profile_k08_phrase_scan.py` against that inventory. Preserve the original cache databases and any associated index/metadata files unchanged. A candidate phrase hit should be promoted only after the original image and its caption/author link are independently established.

## Confidence

- **High:** the integrated code path and its bounded synthetic controls work as implemented.
- **High:** the supplied ZIP has no image or thumbnail-cache member.
- **None:** no claim is made about the actual K08 phrase or historical N14/Emily authorship.
