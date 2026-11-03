# K04: original AX transfer future-burst source test with RC-17 B donor

**Agent 4, 3 Nov 2026. Source-conditional p951 model, no K04 recovery.**

## Distinct hypothesis

After the new [RC17 B two-footer source anchor](h17-k04-rc17-b-consecutive-mt-footer-bridge.md), test whether the three **other original** AX checkpoint transfer arrays, AX-7781, AX-7782, AX-7783, were generated as sixteen consecutive upper-halfwords of MT output at late stages after the 132 intact printer packets. AX-7778's previous source-selected 16-checkpoint match at native -157..-142 is the original-control precedent. This is different from the earlier 1MiB-chunk batch jumps and unconstrained copy donor sweeps.

Source GF(2) rank: printer 15,365; printer+AX7778 15,495; printer+AX7778+RC17 B 15,496 (new B adds one). The selected original printer coupon 951..954 remains completely 128/128 unknown.

## New future target-information geometry

An independent symbolic MT recurrence extended through stage2070. Project every potential 16-checkpoint burst start 1041..2020 (980 windows) onto the exact missing K04 quotient. Only **51** individual starts have nonzero gain:

| Window-start band | Maximum K04 missing dimensions identifiable |
|---|---:|
| 1164..1181 | 45 |
| 1392..1408 | 30 |
| 1618..1633 | 13 |
| Other 929 starts | 0 |

The 45 at stage1179 exceeds the earlier 44 under printer+AX7778 alone; RC17 B's extra original equation creates one conditional target-synergy bit. A different two-window arrangement at 1336..1347 and 1563..1574 can jointly gain 62 dimensions despite each individual window gaining zero. The combination (1179,1347,1574) would theoretically identify **107 of 128** missing bits, leaving 21 bits to enumerate if actual stage assignment were source-consistent. By contrast all 4,896 triples containing exactly one band-1164, one band-1392 and one band-1618 window gain at most45 due to overlapping information.

## The actual original AX data reject informative placements

For every original AX-7781/7782/7783 full sixteen-checkpoint array (sorted seq/attempt), insert its 256 observed upper16 bits into the source equation system, checking two possible global byte orientations. For **all three transfers and both byte orders**, there are:

| Proposed stage-start band | Source-consistent original placements |
|---|---|
| 1164..1181 | **0** |
| 1336..1347 | **0** |
| 1392..1408 | **0** |
| 1563..1574 | **0** |
| 1618..1633 | **1622, 1623, 1624** |

The three final-band survivors have all256 bits independently free before their assignment, so source compatibility there **cannot verify their stage**. At hypothetical 1179, actual AX checkpoint arrays all contradict the source on the fourth original checkpoint or earlier; no need for a 21-bit K04 commitment brute force at the speculative three-window assignment.

[Executable source-pinned SFT](../agents/agent4/k04_future_ax_actual_bursts_sft.py) reproduces all six original transfer-orientation screens and an exact **AX-7778 source-stage positive control**. Original source SHA pins: spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; AX `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`; RC17 `a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d`.

**Scope:** rejects these five chosen short-burst bands, standard sequential checkpoint order and the 16-upperhalfword view only. Other source placement, nonconsecutive draws, different encoder, producer/copy boundary, and K08 literal author text remain unresolved. The selected ACK2 and original commitments were not used in source fitting. K01/K02/K03/K05/K06/K07 PASS; K04/K08 unknown; combined INCOMPLETE.
