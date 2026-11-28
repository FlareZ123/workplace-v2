# K04 complete-coupon candidate from categorical printer records under source-derived AES key

**Agent 18 · 28 November 2026 · bounded complete-output test; no recovered component.**

## Question

Can the previously derived fixed 16-byte source-local AES key decrypt the exact 128-record ordinary printer CLASS/DEST categorical bitstream into the missing physical K04 coupon? This joins two *previously independent* experimental ingredients: the 27 November N09→N13→N23→N20 fixed-size key emitter and the 6 November 128-job Boolean metadata-codebook family. Neither the AES cipher nor the category carrier is attested by a historical printer implementation. The test is exploratory, **not** a source-authenticated printer producer.

## Fixed construction

The source-pinned SFT uses only the original 128 ordinary printer metadata rows, excluding the five exceptional events from candidate construction. Each ordinary row is a pair of one of three CLASS values and one of three DEST values, hence one of nine categories. Enumerate all `2^9=512` Boolean maps to one bit, 128 cyclic origins and four bit-packing/byte-order presentations. These yield exactly **262,144** complete 16-byte ciphertext presentations. Apply the exact source-derived key in its three fixed casing views with AES-128 ECB encryption and decryption, 6 cipher presentations per ciphertext. For every 16-byte output, compare both the output directly and its XOR against the original route-mask field to the **unchanged full SHA-256 K04 commitment**.

The key is reconstructed inside the local program but not printed or committed as source-derived text. The selected copied ACK2 payload is not an input to the categorical construction. The test never reads the quarantined PDF or changes the original records, commitments or canonical candidate.

## Result

| Gate | Result |
| --- | ---: |
| Complete source-category ciphertext presentations | 262,144 |
| Complete original K04 SHA-256 checks | **3,145,728** |
| Original K04 commitment hits | **0** |
| All-printable decrypted 16-byte blocks | 0 |
| Independent planted full-coupon AES/bitmap/XOR recovery control | **PASS** |

This distinguishes the present source-key composition from the prior plain Boolean-category check (no AES) and earlier AES ciphertext scans under other keys (no present source-derived key). It is not a general exclusion of AES, 128-bit hidden data, per-row byte channels, or printer state.

**Reproducer:** [agents/agent18/k04_category_aes_sourcekey_sft.py](../agents/agent18/k04_category_aes_sourcekey_sft.py). It pins original source hashes, constructs the candidate family, verifies the implanted full-coupon control and prints only aggregate statistics. Run locally; **never run the original-source program on public CI**.

## Decision

This *specific* categorical-bitmap + source-key AES hypothesis does not recover K04. Further codebook/cipher-mode expansions need an independently identified carrier, counter or printer producer relation rather than parameter variation alone. K04 and K08 remain missing; the six other original components remain accepted and REC8/1 combined acceptance is incomplete.
