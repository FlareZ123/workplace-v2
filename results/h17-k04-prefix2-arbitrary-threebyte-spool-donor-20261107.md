# K04: free two-byte copied prefix plus independent three-byte spool splice

**Agent 7, 7 November 2026.** Original-data complete-coupon attempt: zero matches. K04 and K08 remain unresolved; original six slot checks retain their accepted status. Original official resources and commitments were not modified.

## Different complete recovery mechanism

The selected PS-261003-0417 18:02 UTC RECOVER ACK2 copied printer buffer starts with A9A9. Its historical physical-paper integrity is disputed. The completed full arbitrary four-byte repair campaign proves any authentic coupon differs from that suspect copied packet in at least five byte positions, conditional on the recorded mask.

A speculative two-stage copier model permits **all 65,536 values of the first two bytes** independently of a **three-byte run copied from another retained printer packet**. The donor run may start at offset 0..13 in any of 132 other original packet payloads and overwrite positions 2..13 of the selected packet. All remaining eleven bytes are copied unchanged. The generated whole 16-byte coupon is reduced using the original XOR mask.

The prior same-job prefix2-plus-threebyte pilot chose two prefix bytes from a source record and freely replaced the next three bytes. This test **reverses the source/free roles**: two *free* leading bytes, and a separate *source-donor* three-byte run anywhere else in the coupon. The source donor may be shifted and originate in any other ordinary or late printer packet, rather than a same-job record.

The A9A9 repeat is not proof of a fault. Ordinary spool records contain other adjacent equal-byte pairs. This is a finite complete candidate construction under a new copier hypothesis.

## Executed original-data test

- Original printer source SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
- Selected copied ACK2: A9A9DC5731A5E2AE879C47215C2559D5, excluded from the 132 donors.
- Original routing XOR mask: 8556C8CB6140A7F9A5123AC7571BEE1C.
- Original K04 component SHA256: 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

| Reproduced property | Original source result |
| --- | ---: |
| Other printer donor packets | 132 |
| Donor three-byte starts | 14 |
| Target three-byte starts | 12 |
| Free two-byte prefix possibilities | 65,536 |
| Full target hash comparisons | **1,453,326,336** |
| Original SHA256 first-eight-byte coincidences | **0** |
| Full original K04 hits | **0** |
| Controlled complete planted five-byte coupon | **PASS** |

Actual local output:

    ORIGINAL_SOURCE_SHA_PASS selected_ACK2_excluded donors=132
    SYNTHETIC_POSITIVE=1/1 recovered_full_coupon_with_unknown_prefix2_and_donor3
    SUMMARY donor_packets=132 donor_starts=14 dest_starts=12 arbitrary_prefix16=65536 checks=1453326336 first64=0 original_hits=0

The synthetic positive uses a historical three-byte source donor and plants the leading bytes BEEF, then searches all 65,536 possible leading pairs against its own independently calculated full SHA256 commitment. A later small source revision added a direct OpenSSL SHA256 consistency check before the candidate enumeration. The original complete run preceded that minor extra check; a subsequent full rerun was interrupted by local execution time limit and must not be claimed as completed. The candidate loop and source control logic were unchanged.

Reproducer: [portable C11/OpenSSL/OpenMP SFT](../agents/agent7/k04_prefix2_donor3_copier_sft.c).

## Boundary and follow-on

This experiment excludes only the specified five-byte two-stage copying geometry. It provides no authenticated K04 physical coupon bits and no terminal K08 words. There is no independent evidence that any physical copy-stage fault has this shape, so further unanchored variants have weak priority. A physically grounded complete selected-object join or intact independent whole-output holdout is a stronger next mechanism. Preserve original acceptance and verifier unchanged.
