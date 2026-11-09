# K08: full-caption decoder from 128 original printer CLASS/DEST symbols

**Agent 4 | 9 November 2026 | Complete bounded source-to-caption test; no original hit.**

## Why test this alternate source architecture?

The preserved printer log has exactly 128 regular five-minute ACK jobs PS-261003-0300 through PS-261003-0427. Each has a CLASS in three categories and a DEST in three categories. The joint metadata stream therefore provides exactly 128 base-nine digits, or 256 trits, enough raw capacity for approximately 50 ASCII bytes of a terminal caption. This motivates a *different* route to an exact K08 phrase: source text carried by a complete metadata stream, independent of the formerly suggested N23→PS-0323 packet pairing. There is no source-authenticated claim that Emily or her desk nonce was ever used to encode this printer metadata. This is a speculative alternative, tested rather than asserted.

## Frozen complete-candidate model

Parse only the **original, pre-18:00, attempt-1 ACK** records of the 128 consecutive PS jobs. Exclude all five exceptional late lines, especially the disputed K04 selected attempt-2 record. For each of six CLASS permutations × six DEST permutations × two source record directions × four trit layouts (CLASS then DEST interleaved, reverse interleaved, all CLASS followed by all DEST, or reverse), decode the 256 trits into:

- a single base-three whole integer packed as 51 big-endian or reversed bytes;
- all seven 7-bit ASCII bit-packing offsets, both byte directions;
- all five offsets of a fixed five-trit character code, with direct byte values or +32 offset.

Apply three *predeclared* transport variants to each decoded object: literal bytes; XOR with the recorded 16-byte K08 desk nonce repeated; or XOR with SHA256(nonce || big-endian u32 counter) blocks. Strip optional leading, trailing or both NUL paddings. Only a wholly printable ASCII string can be a complete literal author-caption object under this proposed encoding. Normalize it using the exact K08 route and test HMAC-SHA256[:16] → original SHA256 commitment.

**No imputation of target words, output fitting, arbitrary decryption-key guessing or K08 commitment-guided parameter enlargement.** This channel is independent of the unvalidated note→spool metadata join.

## Original result

The original archive is source-pinned by SHA256 for the spool file, route and acceptance JSON. The portable [single-file reproducer](../agents/agent4/k08_metadata_ternary_carrier_sft.py) reports:

```text
source_layouts                    288
decoded_binary_objects         22464
printable_exact_strings            0
unique_normalized_candidates       0
complete_hmac_commitment_checks    0
original_or_plant_hits             0
original_status              NO_MATCH
```

Thus none of the frozen decoded objects even qualifies as a literal ASCII phrase. There are zero new original K08 candidate components; no final-author wording was recovered. The count of 22,464 refers to **decoded binary objects**, never to original full-commitment tests.

### Planted whole-caption positive

Encode the complete **50-byte-or-shorter** synthetic phrase `we leave a place beside the window for each other` directly into 128 base-nine digits, map each digit into one synthetic CLASS/DEST pair, with the real desk nonce and a separately computed synthetic K08 commitment. The same decoder recovers the **entire original synthetic wording**, derives 16-byte HMAC component `E10C435691AC0B96F183AE7BD482F164` and passes the synthetic SHA256 commitment. Counts: 288 layouts, 22,464 binary objects, four printable strings, two distinct normalized candidates, two genuine full synthetic HMAC-commitment checks, one hit. The untouched historical verifier is **never** modified.

## Interpretation and next work

The result excludes this exact **plaintext or nonce-masked fixed-radix metadata-carrier family**, not an arbitrary cipher or hidden message, a producer feeding the printer, or the physically absent final caption. Unlike an arbitrary word-grammar search, this mechanism could have carried a complete sentence without selecting words ourselves; the original source says it did not do so under the frozen encodings.

The decisive missing advantage remains a source-specific author-final version/quoted wording path, or a genuinely different cross-record carrier that actually produces a complete original target. K01/K02/K03/K05/K06/K07 remain PASS, K04 and K08 unresolved, combined original REC8/1 INCOMPLETE.
