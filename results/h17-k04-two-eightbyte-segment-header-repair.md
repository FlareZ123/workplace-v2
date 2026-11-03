# K04 two 8-byte-segment header corruption class: complete 32-bit exclusion

**Agent 36 | 3 November 2026 | Original K04 target NO_MATCH.** This is an exploratory complete-coupon candidate mechanism, distinct in support geometry from the already exhausted contiguous four-byte and first/last two-byte repair searches. Neither a genuine fault mechanism nor original coupon integrity is established. Original K04 and K08 remain unresolved.

## Hypothesis and source boundary

The original `resources/evidence/print/spool-reconstruction.log` is explicitly a *retained-fragment printer buffer reconstruction* with *payload integrity unverified*. The incident-date route selects the 18:02 UTC ESC-N `PS-261003-0417` RECOVER attempt-2 ACK, payload `A9A9DC5731A5E2AE879C47215C2559D5`; the first pair `A9A9` is unusual but is not an authenticated corruption marker. The source's route XOR mask is `8556C8CB6140A7F9A5123AC7571BEE1C`, giving the rejected copied component `2CFF149C50E54557228E7DE60B3EB7C9`. The full unchanged K04 SHA256 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

A possible *two independently reconstructed eight-byte segments* model would corrupt both segment-leading 16-bit headers while preserving their following six bytes. It predicts replacement of exactly component byte positions **0,1,8,9** (zero-based); equivalently, replacement of the same payload bytes before the unchanged XOR. This two-seam support is discontiguous. It is outside the 13 contiguous four-byte replacement windows and the previously completed `0,1,14,15` two-ended four-byte class. No original note confirms that the physical printer producer used an 8+8 layout; this is a falsifiable structural hypothesis, not a finding about hardware.

## Exhaustive executed test

Enumerate each `a` and `b` in `0000..FFFF`, replacing original component byte pairs `0:2` and `8:10` with `a` and `b`. Compute SHA256 of each complete 16-byte candidate and compare all 256 bits to the unchanged K04 digest. The complete family comprises **65,536 × 65,536 = 4,294,967,296** unique complete candidates.

The [source-constant C/OpenSSL SFT](../agents/agent36/k04_double_seam_repair_sft.c) provides `begin` and `end` half-open shard boundaries, runs the full unmodified target by default and performs two checks before trying it:

1. Its optimized one-block SHA256 transformation exactly matches OpenSSL's ordinary SHA256 of the unmodified sixteen-byte component.
2. A planted two-pair modified coupon at `a=BEEF, b=C0DE` is found within shard `[BEEF,BEF0)`, and the program reports `HIT` with both correct 16-bit values.

Local full-range runs before and after replacing a data-racy shared-found flag with `atomic_int` completed with:

```text
SCAN [48879,48880) pairs=65536 result=HIT a=BEEF b=C0DE
SCAN [0,65536) pairs=4294967296 result=NO_MATCH
```

The negative covers all assignments in this exact two-seam geometry, conditional on unchanged copied source bytes elsewhere, copied mask, selection rule, and original commitment. It supplies **zero authenticated original K04 bits** and does not exclude longer/multiple damage footprints, a wrong route, a completely different original coupon, or an alternative selected-event producer.

No original case file, acceptance commitment, verifier, or canonical six-pass submission was modified. K01/K02/K03/K05/K06/K07 remain individually accepted; K04 and K08 remain missing; combined REC8 acceptance stays incomplete.
