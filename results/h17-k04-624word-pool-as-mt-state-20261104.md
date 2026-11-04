# K04: complete 624-word original-source pool used as an MT19937 state, 976,748,544 coupon candidates

**Agent 17 | 4 November 2026. Original K04 SHA256 commitment matches: zero.** A new complete-coupon construction from preserved sources was actually executed, with an independent planted synthetic positive in every shard. Six individually accepted components are unchanged; K04 and K08 remain missing, combined REC8/1 INCOMPLETE.

## Why this differs from the preceding 624-word experiment

[Agent39's four-stream MT mosaic](h17-k04-624word-fourstream-mt-mosaic-20261104.md) observed the exact count of **624 independently preserved four-byte words** and tested whether they were **624 consecutive generator outputs**, arranged in 12,288 conventional source-block layouts. Four independently observable MT19937 recurrence comparisons failed for every layout. The present test asks a **different full-key-generating question**: suppose the 624 source words formed an offline seed/state pool, then the selected escrow coupon was four output words generated **after one MT twist** of that pool. Under this assumption the original recorder and printer values are *state input*, so Agent39's consecutive-output recurrence failures are not a precondition.

This producer model is speculative. There is **no record establishing that the escrow printer pooled these four source families**, or that the media used MT19937. It deliberately allows sources captured after the selected 18:02 ACK as input to a hypothetical *offline precomputed* coupon, which would be chronologically impossible under a live contemporaneous producer. The newly recognized MAIL13/MAIL16 prepublication dependencies justify inspecting data-generation order as an alternative hypothesis; they do not prove this one.

## Original source pool and pinning

Four source families supply exactly 624 original 32-bit values, in their own documented internal order:

| Source | Four-byte words | Original extraction |
| --- | ---: | --- |
| Printer spool | **528** | All 132 unselected 16-byte PAYLOAD packets, including routine and exceptional copies, with 18:02 selected ACK2 row129 completely omitted |
| TRP2 recorder | **88** | Every 24-byte record's opaque CONTROL at offset 12; four CRC-invalid records remain identified as raw copies, not valid K05 winners |
| K01 signed WN-14 | **4** | Source-emails 03/06, ink groups A,B,C,D |
| K06 issued RC-17 C | **4** | Revision C page strips, issue SERVICE_ORDER |
| **Total** | **624** | 2496 source bytes |

The code verifies original SHA256 of the printer spool \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\` and recorder \`5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba\`. K01 and K06 raw values must satisfy their original independent SHA256 commitments. The exact selected 18:02 ACK2 content is asserted in the untouched source as a selector and then excluded from all pool bytes. The source route mask and K04 commitment are checked before generating candidates. No original evidence, route, acceptance, official candidate or verifier is edited.

## Exact finite construction

For the four entire source groups P/R/I/C, try all **24** group orders. Within a group, try eight conventional printer layouts (per-word byte endian, row order, fourword packet order) and four recorder, four ink, four procedure layouts (per-word endian and source-row reversal). For **each** group independently choose direct 32-bit word input or MT19937-untempered word input (16 binary selections). Thus \`24 × 8 × 4 × 4 × 4 × 16 = 196,608\` complete 624-word native MT state assignments.

Run exactly **one** standard in-place MT19937 twist on each populated 624-word state. For every **621** consecutive fourword windows inside that single output block, construct the full 16-byte hypothetical coupon under eight serializers: native vs tempered 32-bit output, little vs big endian per word, forward vs reverse fourword order. XOR each complete coupon with the **unchanged** K04 route mask and compare SHA256 of the resulting 16-byte component with the **full original** K04 commitment \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`.

This covers exactly \`196,608 × 621 × 8 = 976,748,544\` complete coupon-to-K04 commitment assignments. These are assignments, not a distinct-coupon count; multiple state orders can yield identical partial output windows.

## Actual original execution and controls

The original 46-file local export was extracted read-only. The C++17/OpenSSL single-file worker was compiled locally and all **16 mutually disjoint group-native-input mode shards** were run to completion, each covering **61,046,784** original K04 assignments with **zero hits**. Each shard generated a separate, well-defined planted synthetic MT one-twist coupon from actual source pool bytes at output window 307, and the **same SHA256(masked-component)** path detected its planted commitment **1,536 times** across duplicate layout assignments. Across all shards: **976,748,544 genuine-target checks, 0 matches, 24,576 synthetic-positive assignment hits**.

The implementation's MT temper inverse is checked on five fixed 32-bit vectors. An independent Python \`random.Random(314159)\` control also confirmed that the worker's in-place MT twist and temper reproduce all **624** actual CPython next outputs from the object's original 624-word internal state, before original-target enumeration.

Portable exact original-source test:
- [Python source extraction, original pins and shard runner](../agents/agent17/k04_624_seedpool_sft.py).
- [C++17 MT twist, complete-coupon constructor and acceptance checker](../agents/agent17/k04_624_seedpool.cpp).

Run all modes by invoking the Python test in a checkout with C++17, OpenSSL/libcrypto and \`g++\`. The test compiles the worker in a unique temporary directory and reads the repository's original \`resources/\`; its \`--mode N\` option runs one disjoint mode and asserts the exact original-negative and synthetic-positive counts. The original execution used the same source extractor, compiled C++ enumerator and all modes, before committing this report.

## Meaning and next cracking direction

The exact **one-twist, whole-source-pool-as-624-native-state** family is excluded as a source for the selected K04 component, despite 976 million complete target checks. It does not exclude a multi-twist variant, independent keyed state initializer, different source subset/order, unknown printer source, true physical coupon, or copied-media fault. The cardinality 624 is source-observed and makes this a bounded construction worth testing; it is not proof of an escrow firmware algorithm.

The productive next path is a source-identified **emission schedule with a genuinely target-informative independent fourword donor**, or a historical physical coupon. K08 still requires Emily's actual normalized final caption or an attested literal editing rule. Original status: K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined INCOMPLETE. No newly authenticated selected coupon bits or final caption words.
