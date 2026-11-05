# H-17 K04: exhaustive all-printer four-lane fragment reconstruction

**Agent 7, 5 November 2026.** The original K04 component remains unresolved. This experiment checks a complete-source-coupon producer, rather than another arbitrary-byte corruption radius.

## New copier/reassembly hypothesis

The selected 18:02 UTC PS-261003-0417 attempt-2 RECOVER buffer has an ACK dispatch marker but no authenticated media checksum. A different explanation for its failure is an erroneous 16-byte copier that assembles a coupon from wrong 32-bit word fragments in the retained printer buffer. Hypothesize that the actual coupon is assembled by taking word 0 from *any* of the 133 captured 16-byte payloads, independently word 1 from any, word 2 from any, and word 3 from any. Keep each word at its original offset and byte order. The disputed selected row is permitted as a donor but not assumed correct.

This predicts a **complete candidate coupon** at each four-index tuple. It differs from Agent7's earlier three-retry per-byte 3^16 search (restricted to one job) and from source-fitted PRNG/affine emitters, and from the <=4-whole-byte copy-relative neighborhood exhausted on 4 November.

## Source and exact reduction

Original file: resources/evidence/print/spool-reconstruction.log, SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Exactly 133 payload rows; selected ACK2 row index 129 (zero-based), copied payload A9A9DC5731A5E2AE879C47215C2559D5.

For any row indices a,b,c,d in [0,132], the hypothetical physical coupon consists of the four bytes at offsets 0..3 from row a, 4..7 from b, 8..11 from c and 12..15 from d. XOR that 16-byte coupon with the documented mask 8556C8CB6140A7F9A5123AC7571BEE1C and accept only an exact SHA256 match to the untouched original K04 commitment 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

## Executed results

- **Full original search:** all 133^4 = **312,900,721** complete word-source assignments checked, **zero original K04 matches**. A source-reading OpenMP/libcrypto C implementation took 50.54 seconds, and an independent source-embedded C implementation took 65.91 seconds. Both returned the same full count and zero matches.
- **Planted positive:** a synthetic commitment from original row indices (2,3,5,7) is recovered exactly once in a 3*133^3 = 7,057,911-assignment first-lane-prefix test, yielding synthetic component B06710605608C04B19B61EEF76D2F35D. This checks the source slicing, official mask and full SHA256 comparison.
- **Selected-row one-donor byte interleaving:** 132*2^16 = **8,650,752** complete source assignments, zero originals.
- **Selected-row one-donor bytewise XOR overlays:** another **8,650,752**, zero originals.
- **Two-donor four-word mosaics with independent per-lane reversal:** C(132,2)*3^4*2^4 = **11,205,216** full assignments, zero originals. Independent synthetic planted positives for each byte model were recovered at their exact donor/mask. These subfamilies overlap and counts are not additive unique candidates.

[Portable standard-library source-pinned SFT](../agents/agent7/k04_all_spool_word_mosaic_sft.py) reproduces the full original 312.9-million-assignment search and planted positive using only the original repository data. The earlier locally executed C implementations accelerated exhaustive testing. No source, verifier, acceptance inventory or canonical candidate was modified.

## Interpretation

This excludes the precise **four position-preserving, unmodified-endian 32-bit fragment selection** from all captured printer rows. It does not exclude a different source set, shifted fragments, internal-byte reversal for all four independently selected donors, nonlinear generation, or original physical/copy-stage data absent from this export. The byte-level and two-donor negatives exclude their own stated models only.

No authentic selected K04 coupon bit was recovered; no exact K08 author-final word was discovered. The original REC8/1 remains six PASS, K04/K08 unresolved, combined INCOMPLETE. Future copier work should prioritize a source-observed or experimentally discriminable fragment-production rule, rather than equating broad arbitrary-mosaic coverage with authentic recovered bytes.
