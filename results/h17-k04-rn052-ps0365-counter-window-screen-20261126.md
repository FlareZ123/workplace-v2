# K04 RN-052 / PS-0365 counter and 52-job window screen (2026-11-26)

## Question

Can the unverified RN-052 → PS-0365 complement-index lead provide a source-side seed, counter, or rolling window that reconstructs the K04 coupon for PS-0417?

## Source basis

- The L-29 docket contains RN-052 as a filed RISK record under FA-17, folio BX25/08.
- The earlier complement-index hypothesis maps a reference suffix (t) to spool job (417-t), so RN-052 points to PS-0365.
- PS-0365 is a RECOVER/bench ACK, attempt 1. The selected PS-0417 record is a RECOVER/bench ACK, attempt 2. Their job suffixes differ by 52.
- This is an exploratory locator only. No source-authenticated RN-to-PS foreign key has been established. The BX25-08 PDF was not opened or used.

## Method

The reproducible screen is `work/h17_k04_rn052_ps0365_counter_window_screen.py`. It reads the docket row, spool records, K04 mask, and original K04 commitment. It emits only counts and candidate labels, never raw payloads, masks, components, or commitments.

It tested 164 candidate constructions:

1. **Seed/counter producer models (125):** PS-0365 payload as a 128-bit seed for AES-128 ECB/CTR/CBC and as the seed for SHA-256, HMAC-SHA256, and keyed BLAKE2s. CTR/CBC counters and IVs used 0, 52, 365, and 417 in both byte orders. ChaCha20 used SHA256(seed) and seed-repeated key expansions with counters 52, 365, and 417 in both byte orders. Exact source-context strings covered RN-052, FA-17, BX25/08, PS-0365, PS-0417, route, class, destination, and attempt.
2. **52-job window models (39):** all 52 acknowledged jobs PS-0365 through PS-0416, in job order; XOR and bytewise sum across the full window and source-class/destination subsets; four index-mod-4 XOR lanes; and SHA-256, MD5, BLAKE2s, and HMAC folds over the concatenated window, with and without the target payload.

Each 16-byte candidate was checked both as a raw selected payload and as a coupon which, XORed with the published K04 mask, must satisfy the original K04 SHA-256 commitment. A synthetic positive control verified the commitment predicate.

## Result

- Candidate constructions: **164**
- Source-window rows: **52**
- Window-specific constructions: **39**
- K04 commitment hits: **0**
- Exact matches to the selected PS-0417 payload: **0**
- Raw recovery values emitted: **no**

The result is a negative for this specific source-seeded counter/window family, not a negative for the complement-index hypothesis as a whole.

## Interpretation and limits

The PS-0365 same-role control does not produce K04 under these tested producer, cipher, hash, MAC, XOR, sum, or 52-job rolling-window constructions. This does not authenticate RN-052 → PS-0365, prove the physical coupon's custody, or rule out a different native queue/driver copy-stage relationship. It does not replace the missing PS-0417 queue manifest, attempt-binding journal, or physical handoff record.

The test did not access protected R:/ or SharePoint and did not open, decrypt, OCR, render, extract, scan, or use any derivative of BX25-08.pdf.

## Reproduction

From the repository root, run:

```bash
python work/h17_k04_rn052_ps0365_counter_window_screen.py
```

The AES/ChaCha subset requires the `cryptography` Python package; without it, the script reports that the optional cipher dependency is unavailable and still runs the standard-library hash/MAC/window checks.
