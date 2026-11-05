# K08: source-wide exact old-caption known-plaintext transport test

**Agent 5 | 5 November 2026. Original K08 unresolved; complete source-only common-pad calibration negative.**

## Question and distinct mechanism

The route gives K08 as a 16-byte HMAC truncation of exact normalized final Emily desk-caption words. The preserved original notes give two **verbatim older envelope captions**, N17 standby and N18 commissioning; the same method independently yields HMAC16s for Emily's N02 and N06 drafts. If a single archival copier encoded these HMAC16 objects under an unknown but **common 16-byte XOR, 128-bit additive or per-byte additive pad**, any two of the four older known-caption inputs should leave a full 16-byte **difference invariant** across two stored source objects. Detecting such a relationship would support a potentially target-reaching alternative: decipher a preserved terminal codeword without knowing the final prose. No original source currently attests this encoding or identifies any terminal codeword.

This differs from a source-carrier-to-K08-target pair arithmetic sweep: the **unknown K08 commitment is not consulted**, and two independent exact known-caption HMACs must first match complete preserved original-source values. It extends the [earlier printer-only N17/N18 calibration](h17-k08-printer-label-known-plaintext-transport-20261105.md) beyond spool packets to raw/decoded byte windows from all **42 actual evidence files**.

## Frozen corpus and computation

Original uploaded 46-file ZIP SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7` was checked locally. The portable source SFT separately checks the original crew-notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` and printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. It excludes the selected disputed 18:02 ACK2 source line from corpus construction.

Take all overlapping contiguous **16-byte windows** from each unmodified evidence file, and independently all overlapping 16-byte windows decoded from contiguous **32-or-more ASCII hexadecimal characters**. Deduplicate values before matching: **61,102 distinct raw windows**, **370 distinct decoded-hex windows**, and **61,472 combined**. This overincludes incidental plaintext windows, unselected printer records and even encrypted 2025 PDF bytes; it is intentionally a generous source-surface test rather than an assertion that each window is a caption storage object.

For each of six unordered pairs of HMAC16 source controls (N02, N06, N17, N18), four common 16-byte layouts (native, whole reversal, fourword reversal, reverse bytes inside each word), and three unknown common-pad families:

1. **XOR:** the entire 128-bit XOR difference of encrypted objects must exactly equal the two known HMAC16 values' XOR difference.
2. **Addition modulo 2^128:** the entire 128-bit modular difference must match, allowing carries.
3. **Independent byte addition modulo 256:** all sixteen corresponding bytewise differences must match.

Hash the original-window set, then for each candidate first ciphertext compute the **uniquely required second ciphertext** directly. This replaces an otherwise quadratic source-pair enumeration with an exact set-membership test. The combined run performs `61,472 × 6 × 4 × 3 = 4,425,984` exact difference assignments; all **zero complete calibration matches**. Separate raw and decoded corpora, respectively 4,399,344 and 26,640 assignments, also yield zero. Four named original HMAC16 inputs and corresponding source SHA checks pass. Planted synthetic N17/N18 HMAC16 objects under one actual nonzero common XOR pad produce two expected pair matches using the **same membership mechanism**.

Portable, read-only [single-file SFT](../agents/agent5/k08_global_knownplaintext_sft.py) has exact extraction and positive controls. Original K08 nonce and all source evidence were read, with no changed acceptance, original verifier or candidate.

## Evidentiary meaning

The original evidence contains no two full 16-byte windows satisfying the specified global shared-pad relationship for any two of the four known old/draft HMAC captions. This rules out these **particular exact common-pad, common-layout transit mechanisms** as a route from old notes to the retained evidence. It does **not** exclude captions compressed or encrypted with per-object keys, unobserved final-only records, nonlinear keyed encryption, a different input stage, alternate text normalization or a different clipboard/export architecture. Direct raw-window scanning of encrypted PDF bytes cannot decrypt hypothetical relevant material.

No historical terminal caption word, K08 component, original selected K04 physical coupon bit or original seventh/eighth PASS was obtained. The unchanged six individual original slots remain PASS; K04/K08 MISSING and REC8/1 combined INCOMPLETE. Further source experiments should require an independently justified label serialization or at least two complete heldout known objects, rather than blindly adding arbitrary transformation families.
