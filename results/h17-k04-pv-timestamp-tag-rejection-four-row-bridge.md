# K04: four-record historian stage bridge through two source-fixed tag retries and one timestamp

**Agent42, 3 November 2026.** This is a **new conditional shared-producer positive**, extending [Agent50's original PV175–177 three-value witness](h17-k04-negative-stage-pv-53bit-triple.md). The missing selected ESC-N coupon remains wholly unknown and the K08 final caption is not reconstructed.

## Observable, frozen source

The original preserved source is HST-4 historian `resources/evidence/telemetry/freeze-export.jsonl`, SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`, and 132 uncontested original printer payloads in `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Source-only conditional p951 MT19937 symbolic basis, rank 15365; disputed selected packet row129 is excluded. The source originally records these independent historian fields:

| Seq | Timestamp UTC | Tag | PV | Unit | Quality |
|---|---|---|---:|---|---|
| 175 | 21:12:51 | LT-204 | 83.330 | degC | GOOD |
| 176 | 21:14:15 | TT-92 | 29.968 | percent | GOOD |
| 177 | 21:14:07 | TT-92 | 16.133 | percent | SUSPECT |
| 178 | 21:13:34 | LT-204 | 85.957 | percent | GOOD |

## New conditional stage observation

The `random.random()` two-word starts at -1567, -1560, -1553 are from Agent50. Their immediately preceding accepted tag outputs are -1568 `LT-204→2`, -1561 `TT-92→1`, -1554 `TT-92→1`; every one has **3/3 source-fixed** top bits. **Previously unexploited original fixed words** place two *rejected* tag sampler attempts immediately before the latter two accepted tags:

| Native MT stage | Printer-constrained tempered word | CPython high-bit interpretation |
|---:|---|---|
| -1562 | `CAEC4334` | `getrandbits(3)=6`, rejected by `randbelow(4)` |
| -1561 | `3046588B` | `getrandbits(3)=1`, accepted TT-92 |
| -1556 | `C2120ECF` | `getrandbits(7)=97` |
| -1555 | `8B2F254D` | `getrandbits(3)=4`, rejected by `randbelow(4)` |
| -1554 | `28F6253A` | `getrandbits(3)=1`, accepted TT-92 |

**Distinct held-out timestamp link.** PV177 records **21:14:07**, exactly **97 seconds after 21:12:30 UTC**. The source-constrained stage -1556 high-seven-bit output is **97/127 mask**, an exact seven-bit prediction under the candidate `timestamp = 21:12:30 + timedelta(seconds=randrange(110))`. **The clock base and range are hypothesized from the visible approximate two-minute acquisition span; the historian readme does not explicitly authenticate them.** The coincidence may therefore be a retrospective source-model choice; it is an interesting conditional bridge, not historical proof of firmware.

Two successive seven-output intervals now have a coherent `timestamp → tag (with rejection loop) → PV (two MT outputs) → other categoricals` stage allocation:

- 175: tag -1568; PV -1567/-1566; two or more unobserved category draws
- 176: timestamp -1563 (no fixed source bits); rejected tag -1562; accepted tag -1561; PV -1560/-1559
- 177: timestamp **-1556 (97 exact)**; rejected tag -1555; accepted tag -1554; PV -1553/-1552

The earlier [Agent42 fixed T/U/Q metadata-gap no-go](h17-k04-pv-triple-metadata-gap-order-falsifier.md) remains valid for its explicit **no tag retry** assumption. These two real reconstructed rejection codes expose a different proposed emitter; they materially explain why that narrower no-go cannot be generalized to all metadata-stage programs.

## New PV178 one-retry alternative

Extending the source stage assignments by a **seven-index gap** would place the accepted PV178 LT-204 tag at native **-1547** and its two-word double at -1546/-1545. This exact position is **source-compatible**: one top tag bit agrees and the PV 85.957 interval has a completion; **none** of the PV's upper 17 precision bits are printer-fixed. It is a weak proposed placement, not an independent numeric prediction.

Under that placement:

- Timestamp PV178 has observed offset **64** from the same hypothesized clock base.
- The *no extra categorical retry* model would draw timestamp at stage -1549. Its high seven bits are source-constrained to a value incompatible with 64, so this minimal schedule is **falsified**.
- If a single extra rejection occurs among the two post-PV177 categorical calls, timestamp shifts to stage -1548, where the source fixes three timestamp bits, all **compatible** with 64.
- The immediately preceding stage **-1549** has both high two bits source-fixed to **2** (native word partial value `AD100001`, known-bit mask `ED78984D`). That word can terminate `randbelow(3)` (unit), and **cannot** terminate `randbelow(2)` (quality). For this exact one-extra-retry stage schedule, calls must be ordered **quality then unit**, and unit index2 maps to recorded PV177 `percent`. The additional quality rejection and acceptance are at stages -1551 and -1550 with source-unknown high bits.

This is a conditional four-record construction with explicit source-compatible original words. It does not uniquely select stage -1547 for PV178, prove the source clock base or historically identify the producer. Alternative hidden call counts and stages remain viable. The **exact 97 clock coincidence** and two rejected tag codes are the most informative new source observations.

## Reproduction and consequence

[Source-pinned single-file Python SFT](../agents/agent42/k04_historian_tag_rejection_bridge_sft.py) imports Agent50's unchanged 132-row conditional MT basis; tests tag accepted/rejected high bits, actual PV original decimal intervals, exact seq177 timestamp97 and the incompatible seq178 no-retry timestamp, one-retry Q→U source compatibility, and a seeded synthetic floating-point reduction positive. The source and original acceptance files are not modified; no selected mask or commitment is consulted.

**Priority experiment:** Learn the **actual**, source-predictive full emitter and time base from other complete original PV rows, preferably with blind time/tag/value holdouts. Then add independently indexed original source bits to the MT state and recompute the selected 128-bit quotient. A retrospective four-row compatible path cannot itself transfer a selected coupon bit. Original six REC8/1 slot PASS, K04 and K08 MISSING, combined INCOMPLETE.
