# K04: metadata producer, rolling hash, and future-stream boundary pilots (2 Nov 2026)

**Agent 3; prospective source-only mechanism probes.** Tested three distinct complete-payload construction mechanisms rather than changing individual bytes of the failed selected ACK. Original `resources/` files, candidate, verifier and commitments were not modified. Original source supplied from the 46-file ZIP (already proven byte-identical to repository).

## A. Stateless per-row digest producer

**Hypothesis:** The 16-byte printer `PAYLOAD` is reproducibly derived from a string encoding of that row's known metadata rather than from a secret independent stream. Under this hypothesis, even a damaged selected ACK2 could be reconstructed from its intact `JOB/ATTEMPT/CLASS/DEST/TIME/STATE` metadata.

Before considering the selected K04 hash or payload, use the first ordinary printer row as discovery control, with independent controls at source row numbers 8, 25, 127, 128 and the last retained row. The metadata-string space used 1-, 2-, 3-field ordered selections from 13 parsed representations (`JOB`, job suffix with/without leading zeros, `ATTEMPT`, `CLASS`, `DEST`, `STATE`, full UTC timestamp, epoch seconds, compact timestamp, minute, time-of-day and date); 11 separators; plain, upper-label, lowercase-label and compact JSON styles. Fingerprints were MD5, SHA256 first/last 16 bytes, SHA1 first16, SHA3 first16, 16-byte BLAKE2s/BLAKE2b; HMAC-SHA256 and HMAC-MD5 keyed respectively by the copied mask, desk nonce, WN-14 K01 and recorder K05. **1,244,100 producer templates; zero even matching the first untouched original printer row**, so no survivor advanced to the other controls. This excludes exactly this stateless producer family, not seeded PRNGs or secret personalization.

## B. Per-record CPython re-seeding

**Hypothesis:** Each row reseeds a CPython Random instance with its job, attempt, date/time or metadata combination; printing uses `randbytes(16)`, `getrandbits(128)` big/little endian, 16 draws of 8 bits, or 4 draws of 32 bits in big-endian words.

Source-only gate: 1–3 ordered metadata fields out of `JOB`, job suffix, `ATTEMPT`, UTC timestamp, epoch seconds, CLASS, DEST and STATE, seven separators, integer/text/sum-of-integer styles. **14,690 completely specified templates, zero matches** to the first intact row's 16 bytes. This tests local per-row re-seeding, distinct from v1 global seed-array and spool sequence models. A separate deterministic known-string CPython synthetic positive control passed.

## C. Stateful cryptographic hash chain

**Hypothesis:** Printer output is a 16-byte digest from the preceding row's printed payload (raw, hex uppercase/lowercase or SHA256 of previous payload) with optional current-row metadata, ordered before or after that predecessor, with six separators. Candidate digests: MD5, SHA1/256/3, BLAKE2b-16 and HMAC in the previous-payload-key configuration. Test on six deliberately separated *intact ordinary-to-ordinary row transitions* (indices 0→1, 2→3, 5→6, 16→17, 44→45, 89→90). **6,528 chain templates; zero matches even for the first intact transition**. This excludes only direct one-row hash-chain families, not arbitrary stateful encryption, keyed stages or unobserved intermediate data.

## D. Adjacent future MT stream beacon, original-only

**Hypothesis:** All 128 ordinary 07:00–17:35 printer `PAYLOAD` values were generated as contiguous little-endian 32-bit outputs of a shared CPython MT19937 stream at an original MT state epoch with first ordinary word index0. Withhold every later exceptional record. Untemper the 512 ordinary words and apply the standard MT twist recurrence
`X[i+624] = X[i+397] XOR twist(X[i],X[i+1])` for `i=0..114`; then retemper. This yields 115 specific future 32-bit outputs conditional on the epoch/contiguity model. A seeded synthetic actual CPython 739-word stream reproduced **all 115 predictions** exactly.

Scan the original nonprinter members for aligned big/little-endian 4-byte hex-token interpretations, original 24-byte recorder raw frame 4-byte aligned words, and original transfer contiguous pair high16/low16 checkpoints. **1,176 external oriented word occurrences (1,052 distinct values); zero exact predicted full32 matches, and zero adjacent two-halfword AX CHUNK matches** with original transfer and seq continuity. The assumption that the first printer row is a cycle-aligned, unskipped MT start is unverified and likely much stronger than historical evidence. This is a narrow negative; no K04 coupon bits follow.

## Consequence

These tests are **falsifiers of specified complete-payload producer mechanisms on intact records**. Their failures avoid any need to rehash corrupted K04 candidate bytes. They neither identify the physical selected ACK corruption nor establish an historically correct producer. Prior work overlaps global MT state fitting and mask-keyed sources; the distinguishing unit here is the *single-row metadata producer* and its blind ordinary-row discriminator. No original accepted component changed, K04 actual target bits remain 0/128, and K08 final exact words remain unobserved.

Locally executed Python scripts were `h17_probe_stateless_hash.py`, `h17_probe_rowseed.py`, `h17_probe_hashchain.py`, `h17_probe_mt_future.py` in this invocation's scratch container. Future reproducibility uses the full explicit classes and checkpoints above; no secret or unreported service was consulted.
