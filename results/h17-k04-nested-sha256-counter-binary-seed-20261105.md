# K04: original-source binary seed sieve for 16 SHA-256 counter/HMAC expanders

**Agent15 | 5 November 2026.** One new complete-producer hypothesis was tested against **two original-source-derived exact 32-bit binary-seed words**; it generated no original-compatible seed. Original six slots remain PASS; K04/K08 MISSING; REC8/1 combined INCOMPLETE.

## Different reconstruction hypothesis

Agent15's earlier source-only CPython `random.Random(B)` inversion ([seed fingerprint](h17-k04-p951-python-sha512-binary-seed-fingerprint-20261104.md)) produced **86** exact/near-exact disjoint four-byte constraints on a hypothetical long binary seed `B`, at lengths near 2.4 KB, plus six source-implied SHA512 digest words. In particular, two adjacent early-recoverable seed words, **`key[22]=FD6A4CF7`** and **`key[23]=06EDCDAD`**, are fully fixed by the original 132 intact printer packets under the hypothetical p951 first-cycle CPython source geometry. The selected original ESC-N ACK2 is absent from this source inversion.

New tested producer: generate `B` as a concatenation of SHA256 counter-mode blocks, or HMAC-SHA256 counter-mode blocks, keyed/labelled by historical archive identifiers or a possible four-digit scanner PIN. If such a source-derived seed matched both exact original words, we could test the other 84 source word domains and six SHA512 chunks, then derive the complete withheld selected coupon and check the authentic K04 slot commitment. **The experiment stops at the original-source gate**, as no candidate survives it.

## Frozen finite test

Candidate seed strings comprise eighteen directly written archive identifiers/constants plus all 10,000 four-digit scanner PIN strings and all 10,000 strings of form `PS-261003-0417:NNNN`, yielding **20,016 unique strings**. The actual 2025 scanner PIN 8131 was discovered in prior source work, but no source says this 2025 PIN generated the 2026 printer's opaque coupon.

Sixteen hash expansion schemes combine: SHA256 of `seed || counter` or `counter || seed`; HMAC-SHA256 with seed as key/counter as message or reversed; and four counter serializations (4byte LE, 4byte BE, ASCII unpadded decimal, ASCII 4digit decimal). Generate each candidate `B` by concatenating enough 32byte digest blocks for the longest hypothetical CPython key array, then trim to all **18** lengths `4n−64`, `n=606..623`. Check exact source key22 at `B[L−28:L−24]` and key23 at `B[L−32:L−28]`, where `L=len(B)`. This is a **64-bit source-only discriminator** per complete candidate and uses neither copied ACK nor K04 component commitment.

**Original result:** `20,016 × 16 × 18 = 5,764,608` complete mode/seed/length assignments; **zero** agree with both required source words. The program also recognizes a planted 8131-derived SHA counter stream from its two generated source words, while rejecting the changed 8132 seed under that planted signature. Original spool SHA256 is checked. The full executed local original-source test returned `PAIR_MATCHES 0` in ~32seconds.

[Read-only portable SFT](../agents/agent15/k04_nested_sha256_binary_seed_sft.py) reproduces the candidate corpus, source pin, synthetic recognition and zero original matches. The repository source SFT uses the same bounded search and exact word-selection formulas; the independent local precommit implementation ran on the original uploaded archive. This is an exhaustive check only inside its **specified 16 counter-mode SHA/HMAC producer families and 20,016 selected seed strings**, not an exclusion of unknown external seed strings, SHA512/KMAC/BLAKE expanders, a different offset/prefix, independently random seed bytes or a different generator family.

The original selected coupon remains unauthenticated, and no keeper-final K08 text was inferred. The experiment's payoff is a fast, meaningful source witness for **complete K04 generation** should a concrete source-based binary-seed producer survive the first two derived words. It does not justify broader unconstrained random hash-family enumeration.
