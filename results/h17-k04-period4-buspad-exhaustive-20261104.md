# K04 full 32-bit repeated copier wordpad: 2^32 exact original exclusion

**Agent42, 4 November 2026 05:14 UTC.** Original selected printer coupon K04 remains **MISSING**. The source-pinned whole-word periodic XOR copier-fault family has been exhaustively checked with unchanged original acceptance and no original hits. This is a complete **finite model exclusion**, not evidence of the historical printer's failure type.

## Mechanism and why this model is distinct

Treat the physical coupon copied in the selected ESC-N / PS-261003-0417 / RECOVER / attempt-2 ACK at 18:02 UTC as potentially corrupted in a **32-bit-wide repeated word serializer**. Let `P` be its reported 16 bytes, `M` the original published K04 16-byte XOR mask, and `U` an arbitrary 32-bit word (little-endian byte pattern). Define the hypothesized true physical coupon `Q(U) = P XOR (U || U || U || U)`; the resulting candidate component is `K04(U) = Q(U) XOR M`. No word choices or caller-supplied special values are constrained: all **2^32** values of `U` are enumerated.

Agent8's [earlier periodic copier-fault gate](../agents/agent8/k04_periodic_copy_channel_sft.cpp) exhausted 1..24-bit repeated XOR faults and one-, two-, three-byte modular additive faults. This report covers the previously omitted **four-byte repeated XOR pad**. Unlike Agent19's [four-word correlated byte-lane](h17-k04-four-word-correlated-byte-lane-20261104.md), it changes **all sixteen bytes**, linked by a common unknown word rather than four independently arbitrary bytes in one lane.

The fault interpretation is a hypothesis: the sources **do not** attest a damaged 32-bit printer serializer. Its usefulness is a bounded path to an exact complete candidate if that failure mode occurred.

## Reproducible source and test

- Original copied ACK `A9A9DC5731A5E2AE879C47215C2559D5`, selected by job, CLASS=RECOVER and final ACK attempt. Original ESC-N XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C`; unchanged `SHA256(K04)` commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- Read-only SHA256 pins on original `resources/evidence/print/spool-reconstruction.log`, `resources/evidence/recovery-routing.json`, and `resources/acceptance.json`.
- Reproducer: [Agent42 C single-file test](../agents/agent42/k04_repeated_32bit_buspad_sft.c) and [manual CI workflow](../.github/workflows/agent42-k04-repeated32-buspad.yml). Each test builds one correctly padded 16-byte SHA-256 block, validates its native SHA256 compression against the standard complete hash, then compares all eight digest words. A second SHA256 target, constructed from planted repeated wordpad `0xA17F35E4`, is checked on the same exhaustive traversal; the original acceptance stays unchanged.
- Local original-source checks: two 1/128 subshards passed, including the planted `0xA17F35E4` positive on subshard 80/128.
- [Actions run **41777783122**](https://github.com/FlareZ123/workplace-v2/actions/runs/41777783122): dispatched at **05:12:04 UTC**, completed with `conclusion=success` at **05:12:43 UTC**. Checked workflow jobs via GitHub Actions list: **32 of 32 completed SUCCESS**, 30 on page1 and 2 on page2. Every shard enumerates a disjoint `[shard × 2^27, (shard+1) × 2^27)` range, with one expected planted positive globally; the code exits nonzero for any missing/unexpected planted control or any original match.

## Result and scope

| Quantity | Observed |
| --- | ---: |
| Complete original candidate hashes | **4,294,967,296** |
| Original K04 matches | **0** |
| Planted control | **1**, expected and enforced by all shards |
| CI completion | **32/32 SUCCESS** |
| Source-selected physical coupon recovered | **No** |
| Original K08 inscription recovered | **No** |

This rejects the finite repeated 32-bit XOR wordpad family. It does not reject different widths, modular-addition encoders, independent word errors, or missing upstream source. The original six accepted slots and combined **INCOMPLETE** status remain unchanged.
