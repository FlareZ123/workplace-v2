# K04: metadata-to-payload affine GF(2) emitter test

**Date:** 2026-11-13  
**Identity:** Agent 6  
**Status:** Negative, reproducible model exclusion

## Question

Can each 16-byte printer payload be produced by one affine GF(2) map of the source-visible row metadata, rather than by a sequential PRNG? This is a distinct model from a state-transition recurrence.

## Model and features

Source: `resources/evidence/print/spool-reconstruction.log`.

For each row, construct a 26-bit feature vector containing:
- 10-bit numeric job suffix (0300–0427);
- 11-bit minute-of-day;
- one contrast bit for `CLASS=RECOVER` and one for `CLASS=STORES`, with LABEL as baseline;
- one contrast bit for `DEST=desk` and one for `DEST=store`, with bench as baseline;
- one affine bias bit.

The proposed emitter is an arbitrary affine GF(2) map from those 26 features to the 128 payload bits. The fit uses exact row-echelon elimination, not a selected digest family. The 128 regular records are all attempt-1 ACKs, so ATTEMPT and STATE are constant and cannot identify an attempt-2 effect; they are deliberately not treated as learnable predictors.

Reproduction:

```bash
python agents/agent6/k04_metadata_gf2_linear_emitter_sft.py
```

## Results

| Regular training rows | Feature rank | Inconsistent rows | First inconsistent row index | Target feature observable? |
|---:|---:|---:|---:|---|
| 64 | 18 | 46 | 13 | No |
| 96 | 20 | 76 | 13 | No |
| 128 | 21 | 107 | 13 | No |

The full 128-row training set is inconsistent with the proposed affine emitter. The first contradiction appears at zero-based row index 13 (the 14th regular record). The selected PS-0417 attempt-2 ACK feature vector is also outside the training feature span, so no payload prediction is defined even if the contradictions were ignored.

## Conclusion and limits

This excludes a single affine GF(2) mapping from the encoded job suffix, minute-of-day, class, and destination features to the 128-bit payload. It does not exclude:
- nonlinear hashes or keyed emitters;
- PRNGs seeded by metadata;
- attempt-dependent behavior (attempt is constant in the training block);
- additional metadata absent from the chosen feature vector;
- independent per-class/per-route producers;
- corruption or truncation in the reconstructed spool log.

No K04 candidate is produced. Do not treat an arbitrary solution to the inconsistent equations as a recovery value.
