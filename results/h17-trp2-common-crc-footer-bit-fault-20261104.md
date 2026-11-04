# H-17 preservation copier: all four TRP2 CRC-invalid rows share one footer-bit defect

**Agent 47 | 4 November 2026 | New concrete cross-row copy/invalidation signature, not a recovered REC8 component.**

## Source observation and alternative causal models

The original recorder file `resources/evidence/recorder/trip-recorder.raw` is a `TRP2DUMP` version 2 export with 88 fixed 24-byte records. Each record contains 20 bytes of data plus a little-endian IEEE CRC32 at offsets 20..23. Its original SHA256 is `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`. The original printer source is separately pinned at `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

Exactly four original records fail CRC: **seq900, seq901, seq902, seq903**, from node49's rejected candidate series. Their stored checksum differs from the recomputed original data CRC by the **exact same word `0x00000100`** in every case. A full brute-force search over **all 24 bytes × eight individual bits** of each invalid record finds one, and only one, whole-record single-bit repair for each:

| CRC-invalid record | Original checksum syndrome `stored XOR computed` | Only single-bit restoration |
| --- | --- | --- |
| seq900 | `00000100` | stored CRC byte offset21, bit0 |
| seq901 | `00000100` | stored CRC byte offset21, bit0 |
| seq902 | `00000100` | stored CRC byte offset21, bit0 |
| seq903 | `00000100` | stored CRC byte offset21, bit0 |

The other **84** original records have matching CRCs and need no repair. A compact **heldout entire-record result** follows: train on the three failed rows 900..902 to infer XOR `0x00000100` in the CRC field; without inspecting seq903's repair choices, predict its exact defect, apply the one-bit edit, and check all 24 bytes against the original record's own recomputed CRC. It succeeds. A single-bit difference in row data cannot explain any of these four original syndromes under the stated CRC implementation.

This is evidence that **the four invalid statuses share a highly structured transformation** at the checksum footer, rather than four generic randomly corrupted packets. Competing interpretations include an intentional checksum invalidation marker, a deterministic exporter/recapture fault applied to a selected series, or a native source system that generated a shared invalid-CRC convention. The surviving bytes do **not** distinguish those origins. The checksum uniquely identifies the minimal one-bit **repair**, not independently authentic physical recorded values or writer chronology.

## Exact selection counterfactual: common footer-bit errors govern the K05 winner

The original source K05 selector chooses the maximum valid seq for every latch0..3 at node49/event82 inside the original eight-second window. The binary file has **twelve** node49/event82 candidates inside that window, and all share the physical timestamp `2026-10-03T21:14:02Z`: older good seq200..203, selected good seq300..303, and CRC-invalid larger seq900..903. If the four invalid rows' **only** CRC-footer bit0 at offset21 were repaired, all four would become valid and outrank every signed K05-selected 300-series row.

The read-only counterfactual produces these complete original-component outputs:

| CRC policy | Winning four seq values | Concatenated 16-byte control | Original K05 slot commitment |
| --- | --- | --- | --- |
| Original correct exclusion | 300,301,302,303 | `FF8B78200A56E8586DCDA00EF01E4572` | **PASS** |
| Onebit footer repairs only | 900,901,902,903 | `C2DE39CCBA1947822A4EE66DF2595C84` | **NO_MATCH** |

This sharply identifies a **functional role** of the four common footer anomalies: the CRC fail state is exactly what prevents a complete higher-sequence rival record group from replacing the real authenticated K05 value. The pattern is compatible with a deliberately invalidated decoy/rejected group, or a controlled export fault applied specifically to the same high-priority series. It remains impossible to infer intent, source code or a physical producer from checksum mismatches alone. Thus a generic claim of accidental four-row corruption would be overconfident. This result is more causally discriminating than just fixing a checksum without checking the K05 selector.

## What the result contributes and does not contribute to K04

The strongest prior related work, [Agent6 node49 series lattice](h17-k04-node49-interleaved-latch-lattice-20261104.md), observed the four bad-CRC rows' CONTROL words fitting a conditional shared printer MT stage layout. That work found that the **actual selected K05 seq300..303** has no comparable stage fit. The common checksum-footer syndrome gives a new, simpler source-specific explanation for the four **nonselected** rows' invalidity and strengthens the warning against treating discarded records as physical selected values. It does not change the original rank or identify a selected K04 raw coupon.

As a deliberately conditional target transfer, I mapped the same bit position (second byte, least significant bit) onto each of the selected printer coupon's four 32-bit words and checked all **16 subsets** of lane-specific toggles against the unchanged K04 mask and original full SHA256 commitment. Original result **0 matches**, planted complete-source-positive **1**. This is **not a new K04 copy-error exclusion**: every one of these 16 outcomes is already covered by the predecessor's exhaustive `<=4` arbitrary changed printer bytes. This transfer lacks any source attestation that the spool copier shared the recorder checksum writer, and **none of the newly identified CRC defects applies to physical selected coupon bytes as observed**.

A productive next test would require a genuine shared copier stage with both original record and exported copy available for a full 16-byte withheld prediction, or a source-linked original checksum for the selected ESC-N print. Neither is contained in this specific recorder footer observation. If the operator instead marked a rejected candidate series by toggling CRC bit8, the proper interpretation is a **deliberate invalidation convention**, whose selected-stage implications differ from random bit rot.

## Reproduction

[Source-pinned single-file Python3 test](../agents/agent47/h17_trp2_crc_footer_fault_sft.py) parses the untouched two original binary source files, recomputes all 88 CRCs, exhausts 192 possible single-bit repairs per invalid packet, predicts the heldout fourth defect and performs only the separated explicitly speculative K04 check. It requires the Python standard library. An original ZIP local-source run printed:

```text
TRP2_original_sha256=PASS records=88 good_CRC=84 bad_CRC=4
seq=900 syndrome=0x00000100 only_single_bit_repair=[(21,0)]
seq=901 syndrome=0x00000100 only_single_bit_repair=[(21,0)]
seq=902 syndrome=0x00000100 only_single_bit_repair=[(21,0)]
seq=903 syndrome=0x00000100 only_single_bit_repair=[(21,0)]
blinded_fourth_bad_CRC_seq903_single_bit_prediction=PASS
speculative_printer_transfer_assignments=16 original_K04_hits=0 synthetic_recovery_hits=1
```

The original evidence, route, acceptance, official verifier, and candidate have not been edited. **REC8 remains K01/K02/K03/K05/K06/K07 individual PASS, K04/K08 missing and combined INCOMPLETE.** The shared CRC-footprint is a constrained source-provenance observation whose most defensible consequence concerns validity of rejected TRP2 records; it is not an original selected physical coupon bit.
