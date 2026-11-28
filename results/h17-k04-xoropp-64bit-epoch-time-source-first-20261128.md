# K04: three complete 64-bit epoch-time seed brackets for canonical xoroshiro128++ first-packet producer

**Agent31 | 28 November 2026 | original-source complete producer exclusions; no seventh recovered component**

## Why this hypothesis and how it could reach the full K04 coupon

The 28 November arbitrary-state xoroshiro128++ inversion work now produces source-compatible states, but many are conditional on speculative event-stage choices. A narrower *actual complete producer* hypothesis is that the printer initialized a standard SplitMix64 pair from a 64-bit UTC epoch timestamp and used the published xoroshiro128++ 1.0 output/transition to produce the intact requests and missing intermediate coupon. If any candidate reproduced the **entire intact 16-byte first packet**, it would supply the whole initial generator state: the selected K04 coupon at every intervening output window could then be constructed and independently SHA256-checked under the unchanged official routing mask, and the untouched third REQUESTED packet withheld for another source control.

A 32-bit seed domain was already fully excluded at phase0 in [Agent31's earlier result](h17-k04-splitmix32seed-xoropp-firstpacket-full-domain-20261128.md); these experiments are distinct because **the time-unit seed is 64-bit**, not merely the low 32 bits, and permit 0 through 63 discarded generator outputs.

**This producer architecture is hypothetical**, not an attested printer implementation. Neither the real random seed nor the print-stage phase is given by the source; these are explicit bounded original-data falsification tests rather than historical reconstruction claims.

## Frozen source and stage geometry

Use exactly one of three intact original source anchors from SHA256-pinned `resources/evidence/print/spool-reconstruction.log` (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`):

1. **16:45:00 UTC label event**, interpreted as an initialization time. Check the *later* same-job `PS-261003-0417 ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER` intact packet at 18:01, as an alternate same-job reseed premise.
2. **18:01:00 UTC request**, interpreted as an immediate generator initialization time. Check the same intact request packet at generator offset 0..63.
3. **07:00:00 UTC ordinary printer batch start**, interpreted as a fresh stream-seed time. Check the intact `PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL` first batch packet.

For each second, *independently* use the 64-bit unsigned integer represented by the complete UTC Unix epoch second multiplied by 1,000 (ms), 1,000,000 (μs), or 1,000,000,000 (ns), plus **every** one of the 1000/1,000,000/1,000,000,000 subdivisions respectively. This is a total of **3,003,003,000** distinct tested 64-bit seed hypotheses across the nine disjoint *(event anchor, resolution)* experimental models. Although different time-unit interpretations represent different clock models, there are no unvisited seed integers inside any declared interval.

Seed SplitMix64 with the 64-bit epoch-time integer and take its first two consecutive output words as the xoroshiro128++ state; check both state-word orders. For each seed/order, run all **64** possible output phases 0..63. At each phase, compare the first generator 64-bit output in each of **four complete packet serializer views**: little/big endian within each native 64-bit word and forward/reverse order of the two 64-bit words. If any first 64-bit word matches, compare the independently generated next output word to the other 64 original packet bits. The copied selected 18:02 ACK2, original K04 SHA target, K04 route mask, and any protected PDF are **not** inputs to this source-first fit.

## Completed original-source results

All nine original-source intervals finished with success exit0 using source-equivalent `g++ -O3 -std=c++17` native code. Every interval completed all seeds with no first-word or complete-packet match.

| Event / target packet | Resolution | 64-bit seeds | State orders | Phases | First 64-bit word matches | 128-bit whole-packet matches |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 16:45 label → 18:01 REQUESTED1 | millisecond | 1,000 | 2 | 64 | 0 | 0 |
| same | microsecond | 1,000,000 | 2 | 64 | 0 | 0 |
| same | nanosecond | 1,000,000,000 | 2 | 64 | 0 | 0 |
| 18:01 REQUESTED1 → itself | millisecond | 1,000 | 2 | 64 | 0 | 0 |
| same | microsecond | 1,000,000 | 2 | 64 | 0 | 0 |
| same | nanosecond | 1,000,000,000 | 2 | 64 | 0 | 0 |
| 07:00 batch start → PS-0300 ACK1 | millisecond | 1,000 | 2 | 64 | 0 | 0 |
| same | microsecond | 1,000,000 | 2 | 64 | 0 | 0 |
| same | nanosecond | 1,000,000,000 | 2 | 64 | 0 | 0 |
| **Total** | | **3,003,003,000** | | | **0** | **0** |

There are **384,384,384,000 generator-stage comparisons** (3,003,003,000 seeds ×2 state orders ×64 consecutive startup phases); each comparison checks membership in the four source-serializer first words before attempting a complete packet comparison. Every one of the nine full original-source scans finished with exit0. The three billion-seed nanosecond intervals took 254.043s, 252.541s, and 251.447s on this CPU setup, respectively; smaller intervals under one second each. This is an *executed finite negative*, not an aborted partial job.

**Synthetic full-object control:** the exact stage scanner recovered **48/48 deliberately planted complete 16-byte packets**, including all four serializer presentations, both state orders, phases 0,17,63 and both endpoint 64-bit timestamp seeds. It required both original-style 64-bit outputs, not just a partial word. All original-source source-file hash/input-format controls were separately checked locally, and the program refuses nonunique original first-packet anchors.

The exact standalone source-only C++ implementation, including its target-independent control, is [`agents/agent31/k04_xoro_time_seed64_unified.cpp`](../agents/agent31/k04_xoro_time_seed64_unified.cpp), commit [`dcaede10`](https://github.com/FlareZ123/workplace-v2/commit/dcaede10601f7aa12fec06542c7aec8f6df41632). Each bracket is replayable by calling it with the indicated mode and half-open base-10 interval; it asserts a maximum 1 billion seeds per invocation. Execution was local, never GitHub Actions.

## Interpretation and remaining ambiguity

These original source results rule out **only** epoch-ms/μs/ns seeds within the *three exact source-identified seconds*, with 64-bit SplitMix64 startup (two word orders), canonical xoroshiro128++ 1.0, first packet at generator phase 0..63, and four 64-bit packet layouts. The result does **not** identify the real printer generator, rule out a clock shifted by seconds/minutes, a duration-derived seed, unsigned high bits other than the tested epoch timestamp, unknown secret salt, initialization beyond phase63, or independent selected-event reseeding. It produces **zero** new authenticated K04 coupon bits. Testing arbitrary 64-bit seeds without an evidence bridge would not be a finite historical recovery; do not infer a universal seed exclusion from this bounded screen.

Source-driven continuation must identify a more selective actual printer seed/provenance relation, a genuine author-final K08 phrase emitter, or an original copy-stage carrier. The original six slots K01/K02/K03/K05/K06/K07 remain PASS, K04/K08 remain MISSING and combined REC8/1 remains INCOMPLETE. No original evidence, protected PDF, acceptance file, verifier or canonical candidate was modified.
