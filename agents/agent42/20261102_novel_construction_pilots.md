# Agent42 | 2 November 2026 | complete-candidate reconstruction pilots

**Status:** all tested source-derived hypotheses gave negative controlled results. No authenticated K04 selected payload bit or K08 terminal word recovered; do not update `resources/candidate.json`. This note documents test classes so a successor can test a materially different producer/editor rather than rerun the same classes. These are conditional experimental boundaries, not impossibility proofs.

Original local `h17-archive-dump.zip` was unpacked without modifying sources. Source spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The original `acceptance.json` and routing/mask were never altered. The copied disputed K04 ACK at 18:02 was **excluded** from every producer-model original-control fit. Known six accepted components were used as *candidate producer keys only* and not reverified. 

## Pilot A: source-keyed digest producer

Hypothesis: opaque printer coupons are 16-byte deterministic MD5, SHA-256 head/tail, SHA3, BLAKE2s/BLAKE2b, or HMAC outputs of per-job metadata. Message inputs ranged over named job ID, numeric suffix, date/time/UTC variants, CLASS, DEST, attempt, pair/triple concatenations, and archive-object prefix/suffix. HMAC keys: the six verified components, K04 mask, K08 desk nonce, and archive labels. Three exact intact source controls: ordinary job0303 RECOVER at 07:15, late job0448 RECOVER at 18:24, and same-job job0417 LABEL at 16:45. Total digest constructions **494,802 + 494,340 + 495,264 = 1,484,406**. No exact 16-byte matches. The observed maximum prefix was 2 bytes in each control; not target information. This excludes only the enumerated direct hash/HMAC serialization family.

## Pilot B: source-token CPython MT seeds

Hypothesis: one CPython MT stream seeded from a short, recoverable archive ID/date/signed component/mask/nonce or scan-release token under known seed-to-int/string/bytes/digest transformations. **640 distinct seed representations**, generating **5,000 32-bit tempered words per seed**, checked in little/big-endian four-word concatenation and reverse-four-word orientations against **130 intact ACK payload records**. Exact 16-byte hits: **0**. This does not exclude unrestricted MT states, different seed derivations, skip-stage models, or novel cross-stream indices.

## Pilot C: physical cassette ticket chain to coupon

Distinct source linkage: `print-fleet-retirement-note.txt` and `supplier-reconciliation-L29.csv` give five posted `L-29/S` (ESC-S/job0448) and five `L-29/N` (ESC-N/job0417) ticket identifiers. Hypothesis: printer coupon is a hash/HMAC of the physical return set and its route, job, account, folio and date. Tested prefixes/suffixes, ticket numeric and full identifiers, tab order and reversal, multiple separators, MD5/SHA256/SHA3/BLAKE2 and selected HMACs. Tested **22,275** candidate outputs on same-CLASS late intact ESC-S RECOVER, **26,829** on same-job earlier ESC-N LABEL. Both **0 full matches**. The controls differ from the missing target in route or CLASS respectively, so failure addresses only the frozen common encoder family.

## Pilot D: archive-keyed AES per-event producer

Hypothesis: opaque 16-byte printer buffers are AES-128/ECB encryption/decryption of structured event counters or text padded/hashed to 16 bytes, keyed by previously available WN14, PTW417, RC17, mask, nonce or archive-ID-derived MD5/SHA keys. Original intact controls ordinary RECOVER, ESC-N LABEL, ESC-S RECOVER. Tests per control **2,886 / 2,886 / 2,769** constructions; zero exact. A NIST AES-128 block positive control passed. Other AES modes, unknown keys or ciphertext copy stages remain open.

## Pilot E: K08 scene-level terminal edit program

Explicit speculative rewritten-caption grammar maps N02/N06/N13 and N20/mail11 semantics into clauses for `night`, `sea`, `crew/voices/table` and `lamp/mugs`. It uses 24 night openings, 21 sea clauses, 24 crew clauses, 13 optional lamp clauses, six permutations and seven joiners, with a second four-clause family. It includes synonym/tense/editorial rewrites, unlike the earlier 13m **verbatim three-fragment** K08 pilot, but remains unproven as Emily's actual edit practice. Original HMAC nonce, normalized source and unchanged K08 SHA-256 commitment were used. Control N02 known normalized caption derives the previously published `BF889359B0303F2B2B2FD96AE841210B`. Exactly **3,096,576 assignments**, zero hits. It does not constrain unconstrained prose.

## Pilot F: N22 fax/bit-order source-copy hypothesis

N22's observation that the label printer was “thinking it is a fax machine” could weakly motivate a bit-order/polarity failure model. Direct selected-buffer interpretation tested deterministic 16-byte transformations: reversal of 1/2/4/8/16-byte units; bit mirroring by those units; nibble swaps; 127 rotations in bit position; 15 byte rotations; 2-,4-,8-byte unit permutations and compositional inversion/polarity. Deduplication left **202,223 complete payloads**. XOR with the original 16-byte ESC-N mask and SHA-256 against unchanged K04 slot commitment: **0 matches**. No assertion that N22 actually documented the ESC-N device or that the defect was a bit-order error; this tests only those transformations, distinct from arbitrary 1-4 byte-value correction searches.

## Next direction

Any promising next K04 mechanism should explain the *whole selected payload* through a stage not represented by these hash, seeded-stream, asset-ticket, AES, or bit-order families. MT p955 residual nullspace remains 128 bits under its specific unrestricted-state chronology; a truly restrictive seed law, target-ancestor external carrier or selected-stage copy mechanism could bypass it. For K08, investigate an independently constrained final edit mechanism, an original/version witness, or a genuinely bounded alternate grammar; the N20-themed prose choices by themselves have little predictive power. No new seventh PASS is claimed.

These pilots were run as local Python files against the unpacked user archive; local file names: `work_hmac_fingerprint.py`, `work_k04_known_seeds.py`, `work_k04_cassette_derivation.py`, `work_k04_aes_producer.py`, `work_k08_scene_edit.py`, `work_k04_fax_bitorder.py`. Code remains temporary scratch, not official evidence.
