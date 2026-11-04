# K04: selected ACK2 five-byte prefix damage with original same-job donor controls

**Agent 5, 4 November 2026. Actual source-pinned original-target computation completed; K04 NO_MATCH.** The official six established components remain individually accepted, K04/K08 missing and combined REC8/1 INCOMPLETE. The source and verifier were read-only.

## New exact candidate construction

The selected logical `ESC-N / PS-261003-0417 / 18:02 UTC / RECOVER / ACK attempt2` has reconstructed but unauthenticated copied payload `A9A9DC5731A5E2AE879C47215C2559D5`; its original mask is `8556C8CB6140A7F9A5123AC7571BEE1C`, original full K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Original printer spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

As of 4 November, Agent 13 has independently reconciled Agent 7's complete exhaustive **all four-whole-byte supports** (all `C(16,4)=1820` choices), so the genuine physical coupon, if the current mask is correct, differs from this suspect copied packet in **at least five byte positions**. Never rerun the four-byte radius. The copied packet has an unusual `A9A9` leading repeated byte; the event is unique among 133 rows, but that motif is **not** physical-error authentication.

A separate, speculative **stale two-byte prefix followed by a three-byte corruption burst** is now tested. Preserve copied packet bytes 5..15. Replace its first two bytes with a contiguous two-byte window from one of the *three intact other records of the same job*:

- 16:45 LABEL ACK `E1E60D5F6B6DD2225FA6D5A2A63AD932`
- 18:01 RECOVER REQUESTED1 `CD3E4F216ADB2FB180DA2AA90B33F7A4`
- 18:03 RECOVER REQUESTED3 `44D53DFC29D7943A95D89371DA58EC64`

Select any source two-byte start `0..14`, optionally reverse those two bytes. Independently replace copied bytes 2,3,4 by **every** 24-bit value. For each complete hypothetical 16-byte physical coupon, XOR the unchanged original 16-byte mask and compare SHA256 against the **full untouched K04 slot commitment**. This family tests the first possible five-byte prefix fault with a two-byte **original same-job fragment**, not a guessed five-byte value or a non-original prefix.

The predecessor `results/h17-k04-four-source-same-job-copy-mosaic.md` chooses *corresponding-position* bytes from four intact/copied same-job buffers; it does not allow an independent shifted two-byte donor plus three unrestricted arbitrary bytes. The predecessor `h17-k04-shifted-four-fragment-original-job-source-20261103.md` constructs the *entire coupon* from four contiguous **4-byte** source fragments; it does not include arbitrary unknown original three-byte fragments. This finite geometry is not covered by those exact models. It remains an exploratory physical-copy proposal with no historical demonstration that five leading bytes were damaged.

## Actual enumeration, controls, outcome

Exactly `3 original same-job donor buffers × 15 two-byte offsets × 2 orientations × 2^24 arbitrary three-byte values` = **1,509,949,440 complete candidate assignments**. Some donor two-byte choices may coincide, so this is an assignment count rather than guaranteed distinct coupons.

A C11/OpenSSL source-pinned SFT checks original spool SHA256 and exact selected ACK line, verifies donor literals, compares `SHA256_Transform` state words against the standard `SHA256` path for each donor prefix, and independently plants a complete five-byte coupon with bytes `5F6B8317E9` at positions 0..4. The synthetic target is the full SHA256 of its **masked component**. The exact original-data local execution printed:

```text
SUMMARY packets=3 donor_offsets=15 directions=2 unknown_bytes=3 checks=1509949440 original_hits=0 planted_hits=1 smoke=0
```

The original slot produced **zero** matches. The synthetic planted *five-byte* complete target was found **exactly once** in the same exhaustive full search. The full locally executed C source SHA256 was `13ee444b6f1fe17faa4c32cb5de88d5c76e179d4db3c1681b16475ac03c1e2b9`; a portable equivalent in-repo source is [Agent5 C single-file test](../agents/agent5/k04_prefix2_source_threebyte_sft.c) (with the same source, geometry, and checksum calculations). The original local source is attached to this session; independent compilation of the in-repo equivalent remains optional and **is not asserted as already executed**.

A smaller distinct **internal contiguous donor overwrite** also tested all lengths 5..16, all aligned/un-aligned source/destination positions, and all 132 nondisputed spool donor packets, replacing only one matching-length selected copied segment and preserving other copied bytes. The original-data local `h17_k04_internal_donor_window_sft.py` reported **85,800 assignments, 85,303 distinct full candidate payloads, zero original K04 matches**, with a planted exact seven-byte source-fragment positive recovered once. This was a low-cost gate, not a verified copying-stage diagnosis.

## Limits and next move

Neither result recovers any original selected coupon bit or demonstrates a real corruption mechanism. These tests exclude *only* the exact finite source-linked copy families, not a five-byte prefix with two unknown source bytes, an independent original print medium, wider faults, arbitrary unknown masks, or authentic final Emily keeper wording.

Any next five-byte search should justify why its new byte positions or donor source are physically preferred; blindly multiplying the now-complete 4-byte radius is unproductive. A more informative breakthrough would recover an independent original print-medium witness or a producer/copy-stage rule predicting complete genuine ACK packets before applying the unchanged K04 commitment. K08 remains separate and unresolved.
