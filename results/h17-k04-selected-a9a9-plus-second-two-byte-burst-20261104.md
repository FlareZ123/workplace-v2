# K04: selected A9A9 initial pair plus independently corrupt second byte pair

**Agent 19 | 4 November 2026.** A completed original-source-pinned **51,539,607,552 full SHA-256 candidate** search produced **zero matches** to the unchanged K04 slot commitment. The 96 disjoint jobs all succeeded, and the full correction search recovered **two independent planted complete synthetic coupons** as controls. Six other original slots remain PASS; K04/K08 missing and combined REC8/1 INCOMPLETE.

## Original-source clue and model

The incident-date route `ESC-N` resolves to `PS-261003-0417`. Its final ACK is at `2026-10-03T18:02:00Z`, `ATTEMPT=2 STATE=ACK CLASS=RECOVER`, and the unauthenticated copied 16-byte payload is:

```text
A9A9DC5731A5E2AE879C47215C2559D5
```

Across all **133 original copied spool payloads**, this selected record is the **only one with two identical leading bytes** (`A9A9`). That is a weak, retrospectively selected anomaly: among 133 otherwise random two-byte pairs, roughly half an equal-leading pair is expected, so seeing one does **not** independently establish a damaged header, a sentinel, or the original coupon values. The original custodian and MAIL16 explicitly say spool ACK dispatch does not authenticate the copied media.

One capture-stage hypothesis is a two-byte replacement at copied byte indexes **0,1** plus an *independent second adjacent two-byte burst* starting at byte index **j=3..14**. Each of those four bytes is allowed to be **arbitrary 0..255**, with every other selected copied byte preserved; burst at j2 belongs to the inherited prior exhaustive contiguous-four-byte search and is not rerun. Thus 12 distinct byte-support pairs, each with 2^32 independent replacement tuples. The two bursts may cross original word boundaries, so these candidates generally fall outside both inherited contiguous-four-byte replacement and v2 common byte-lane independent-fault tests.

The original route XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C` is unchanged; every corrected full 16-byte payload is XOR-reduced and then SHA-256 hashed against original K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The source confidence is *speculative fault geometry*, with mathematical exactness of enumerated coverage.

## Complete original computation and positive controls

The [C/OpenSSL original-source-pinned reproducer](../agents/agent19/k04_four_word_byte_lane_sft.c) contains modes 4..15 for these twelve support patterns. Its original source checks require:

- `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- `resources/evidence/recovery-routing.json`, SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- `resources/acceptance.json`, SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

The SFT's self-test recovers two separately planted complete 16-byte SHA-256 targets using exactly the same transformation and comparison path as original candidate checks:

1. Four independently arbitrary same-position byte-lane replacements `DEADBEEF` at source byte indexes 2,6,10,14, as a control for modes0..3 inherited from the immediately previous distinct complete search.
2. Two arbitrary byte pairs `B10C89AB` at positions 0,1 and 8,9, as a positive for new **mode9**.

Both synthetic true components are found exactly once.

The corrected [manually dispatched two-burst search](https://github.com/FlareZ123/workplace-v2/actions/runs/41756636645) was run on SHA-pinned source commit `82c05c60ecb3097896b2ef801268d160f53062be`. Its 12 mode values ×8 disjoint 32-bit shards per mode produce **96 distinct jobs**, all with `conclusion=success` as confirmed by a complete four-page listing of original GitHub Actions job IDs. Each job checks precisely `2^29=536,870,912` full original candidates, returns an error on any actual original match or missing source pin/positive control, and prints a final `DONE ... original matches=0` counter. Sampled raw logs show:

```text
Synthetic 4-independent-byte lane positive: PASS
Synthetic independent dual-burst positive: PASS
ORIGINAL mode=4 shard=0/8 range=0..536870911 candidates=536870912
DONE mode=4 shard=0 complete=536870912 original matches=0

Synthetic 4-independent-byte lane positive: PASS
Synthetic independent dual-burst positive: PASS
ORIGINAL mode=15 shard=3/8 range=1610612736..2147483647 candidates=536870912
DONE mode=15 shard=3 complete=536870912 original matches=0
```

| Search dimension | Original checked |
| --- | ---: |
| Burst starts `j=3..14` | 12 |
| Independent four-byte corrections per burst | 4,294,967,296 |
| **Total original complete K04 components** | **51,539,607,552** |
| **Accepted original matches** | **0** |

An initial [96-job run](https://github.com/FlareZ123/workplace-v2/actions/runs/41756336197) failed at compilation due an erroneous `lane` progress-print variable, before testing any original target. This was corrected in commit `82c05c60ecb3097896b2ef801268d160f53062be`; the failed run is not counted in the successful coverage claim.

## Distinctness, decision and limitations

This exclusion is a source-motivated **two-disjoint-whole-byte-burst** model beyond the earlier contiguous four-byte and same-byte-lane models. It targets a different 4-byte support family from the 4 November 17.18b independent lane check. It must not be confused with the 4 November four-*hex-nibble* check: **that nibble search was redundant prior art**, already fully covered by v1 Agent40's October18 all-position four-nibble work, and does not supply novel coverage.

The result rules out only copy-stage byte *substitutions* at indexes 0,1 and an independently selected adjacent two-byte pair j,j+1 (j3..14), with all other copied bytes faithful. It cannot authenticate the true physical ESC-N coupon or its damaged positions, reject other four-byte supports, shifts/insertions/deletions, a different upstream printer producer, or a faulty mask. It has **zero authentic K04 bits** to place into the recovery key. K08 original keeper's exact final words are likewise unquoted.

**Next decision:** avoid multiplying weakly motivated error geometries after repeated full negatives. The most valuable future input remains a source-backed original physical selected-coupon witness or a generator/capture model that predicts an unseen authenticated copied packet before testing K04. Until then, keep K04 missing and original REC8 incomplete.
