# K04: integer-prime-field 128+5 printer interpolation and original whole-packet holdouts

**Agent 42 | 9 November 2026 | New finite-field arithmetic branch; original K04 NO_MATCH.** The original six established REC8/1 components remain accepted. K04 and K08 remain missing and the combined key INCOMPLETE.

## Why this is a separate attack

The 128 ordinary five-minute original printer ACK packets followed by five exceptional records suggest a speculative shortened systematic parity / erasure architecture. Agent4 already tested 58 byte-lane GF(256) RS/evaluation mappings plus eight whole-packet GF(2^128) evaluation mappings, without genuine historical late-ACK holdout success. **This experiment uses full 128-bit packets as integer residues in conventional large *prime* fields, rather than characteristic-two Galois fields.** Prime-field Shamir-style interpolation has different additive/multiplicative laws and cannot be identified with the earlier GF(2^128) test.

No original document specifies any polynomial code, parity interpretation, prime modulus or interpolation coordinate. This is a bounded exploratory full-coupon mechanism, not evidence that the printer used it.

## Frozen historical source and producer

Original printer SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Take **only 128** original regular attempt-1 ACK packets PS-0300 through PS-0427 in order (or reversed), parse the entire copied sixteen bytes as big-endian or little-endian unsigned 128-bit field integers. Exclude all five exceptional payloads from fitting, including the disputed selected K04 ACK2.

Interpolate the unique degree-at-most-127 polynomial through all 128 authentic packet source values in each of these *three mathematically different prime fields*:

- `p=2^128+51` (least prime above the maximum 128-bit integer);
- `p=2^128-159` (prime just below the 128-bit boundary, with all original 128 source values still canonical);
- `p=2^130-5` (the conventional Poly1305 prime).

Two coordinate hypotheses: regular row indices `0..127` and subsequent exceptional indices `128..132`; or actual elapsed UTC minutes from 07:00 for the regular rows `0,5,...,635` and exceptional coordinates `661,662,663,684,685` (18:01, 18:02, 18:03, 18:24, 18:25).

For each field, coordinate hypothesis, complete-packet endian presentation and regular-source direction, evaluate the polynomial at all five exceptional positions. Test the **two independently copied whole 16-byte ACK records** at positions 3 and 4 (PS-0448 and PS-0420) as unseen controls. A selected prediction at position 1 must fit exactly within sixteen bytes; XOR with original K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`, then compare complete SHA256 to the untouched historical K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Values outside 16 bytes are explicitly noncanonical, never silently truncated.

## Executed outcomes (original unchanged ZIP and extracted original directory)

| Check | Exact result |
|---|---:|
| Unique complete producer models: 3 prime fields × 2 coordinate grids × 2 word endian choices × 2 source directions | **24** |
| Original selected full 16-byte K04 coupons predicted without truncation | **17 / 24** |
| Original K04 full SHA256 commitment matches | **0 / 17** |
| Original complete copied PS-0448/PS-0420 ACK predictions matched | **0 / 48** |
| Genuine independently generated polynomial source-to-withheld synthetic predictions | **30 / 30 PASS** |

The synthetic producers have independent seeded degree-eight polynomials and reproduce each of five completely withheld packet evaluations on both grids under all three moduli. This validates exact field interpolation, original packet widths and coordinate arithmetic. It does **not** authenticate the original producer.

The whole-packet holdouts are post-dispatch copied source evidence, not independently certified paper media. The complete **0/48** source-level failures already reject the specific prime-field issuer family more strongly than a lone target-hash negative; they do not exclude every nonlinear producer, generalized polynomial, unknown source transformation, or actual physical coupon.

## Reproduction and decision

[Original-source-pinned read-only SFT](../agents/agent42/k04_primefield_128_batch_sft.py), Python 3 standard library, checks the exact 46-file ZIP SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7` when supplied, verifies source SHA and actual selected/late event headers, constructs all complete candidates, and prints the full per-model diagnostics. Local executed paths: original ZIP and extracted original contents, identical summary statistics.

**Decision:** This specifically closes integer-prime interpolation of the 128 original ordinary full packets into five exceptional packets for the three standard large primes and two natural coordinate grids. Moving from GF(2^128) to standard prime fields does not expose K04 here. Future experiments require a different source-to-object structure or new actual original media; increasing arbitrary polynomial moduli absent an issuing rule is not a meaningful recovery advance.

No original evidence, commitments, route, candidate or verifier was modified. K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; original combined REC8/1 INCOMPLETE.
