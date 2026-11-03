# K04: long-lived CPython clock seed with hidden pre-spool draws

**Agent 1, 3 November 2026. Source-tested complete-coupon producer hypothesis falsified.** The original REC8 remains six individual PASS, K04/K08 missing, combined INCOMPLETE.

## New source-to-target mechanism

Previous Agent18 work tested **selected-only** 18:02 clock reseeding under short output offsets. This experiment instead examines a **single long-lived** CPython Random(integer_seed) stream initialized near the **first preserved routine printer event** at 07:00 UTC, with up to 8192 hidden 32bit outputs consumed before the first packet. If source calibration identified a seed and prefix, the frozen previously published p951 printer stream chronology would allow prediction of the selected 18:02 coupon. The selected 18:02 copied ACK bytes, K04 mask, acceptance hash and K08 data are **never** used to choose a seed, offset or output view.

The preserved original first intact packet is PS-261003-0300 at 07:00 UTC, bytes FBBBC54356483F5864BB3F06794518A5. The independent second intact job at 07:05 is 64176B6C3A91BD06B12FC0D90B3A7DB4. The original spool SHA256 is 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.

For each seeded genuine Python generator, inspect every getrandbits(32) native output at prefixes **0..8192 inclusive**. Compare each native word against four candidate first-word values: 32bit little or big endian, with fourword natural or reversed order. A collision triggers the three remaining output-word checks. A complete packet match would then face independent source checks against all 132 intact original packets using the frozen p951 index vector, withholding selected row129.

## Complete original-source experiments

| Seed timebase and interval | Integer seeds | Generator draws | Layout comparisons | Firstword collisions | Full 16byte matches |
| --- | ---: | ---: | ---: | ---: | ---: |
| UTC second, **2026-10-01 00:00:00 through 2026-10-03 07:00:00 inclusive** | 198,001 | 1,622,222,193 | 6,488,888,772 | **0** | **0** |
| UTC millisecond, **2026-10-03 06:59:00.000 through 07:01:00.000 inclusive** | 120,001 | 983,168,193 | 3,932,672,772 | **1** | **0** |
| **Total** | **318,002** | **2,605,390,386** | **10,421,561,544** | **1** | **0** |

Second seed values exactly range from decimal 1790812800 through 1791010800. Millisecond seed values exactly range from 1791010740000 through 1791010860000. The comparison count represents four equality checks per one generated native 32bit output. It must not be interpreted as ten billion independent PRNG draws.

The single incident-millisecond collision occurs at integer seed **1791010758824**, prefix output offset **4556**, byte view **big endian**, word order **reversed**. The subsequent three generator outputs disagree with the original packet; the seed fails the first full source check and is therefore not a reconstructed writer. All second-seed intervals were executed in disjoint chronological shards, as were the incident-millisecond intervals.

## Controls, producer boundary and result

The [portable source-pinned single-file test](../agents/agent1/k04_clock_hidden_prefix_sft.py) uses CPython's actual integer seeding, avoiding a reimplementation of init_by_array. It runs **48** seeded packet serialization controls for three seeds, four hidden prefix lengths and four packet layouts. A distinct planted source with seed 20261103 and 57 hidden outputs is uniquely recovered from a seven-seed, 72-offset grid. Source SHA256, row count and two original packet strings are asserted. A model fit to first original packet would be tested against all intact rows before being considered as a genuine target producer. No original first full-packet fit occurred.

**Exclusion:** This finite source test rejects a clock-initialized CPython getrandbits(32) producer with the stated seed intervals, 0..8192 initial draws and four direct packet representations. It cannot exclude longer hidden prefixes, other seed origins, altered serializers, per-job reinitialization, different generators or physical coupon/copy corruption. The archive does **not** attest actual CPython, clock seeds or p951 production indices. No K04 selected physical bit and no K08 terminal caption word were recovered. The six accepted original components remain unchanged; combined REC8 is INCOMPLETE. Further prefix scaling without an independent seed/producer source would have poor evidence value.
