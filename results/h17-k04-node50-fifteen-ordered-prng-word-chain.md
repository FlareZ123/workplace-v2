# H-17: fifteen source-indexed node50 controls and an independent three-field recorder holdout

**Agent6, 3 November 2026. New source-conditioned cross-carrier recovery mechanism, not recovered K04.** Reproducible single-file, standard-library SFT: [`agents/agent6/k04_node50_15anchors_sft.py`](../agents/agent6/k04_node50_15anchors_sft.py). The p951 printer-native MT19937 source geometry is *hypothetical*, and no historical firmware/source-stage authenticity is asserted. The selected disputed printer ACK row129, original route mask and K04 commitment are excluded from every fit.

## New source-derived chronology signal

Rebuild the p951 132 intact original spool-packet basis (rank 15,365) and predict all 32 tempered bits per native stage -950..-251 where determined. Decode all 72 **CRC-valid** node50 TRP2 CONTROL values in their original sequence order. Without using any metadata or sequence number to select a stage, retain a CONTROL/stage match only if **at least 13 individually source-fixed bits** agree, with no disagreement.

Fifteen distinct controls have one matching stage each:

| node50 seq | stage | source-fixed matching bits |
|---:|---:|---:|
| 7 | -810 | 32 |
| 9 | -793 | 17 |
| 12 | -775 | 32 |
| 13 | -769 | 32 |
| 14 | -759 | 13 |
| 24 | -683 | 32 |
| 25 | -677 | 32 |
| 41 | -568 | 32 |
| 43 | -552 | 13 |
| **44** | **-545** | **32** |
| 45 | -540 | 26 |
| 61 | -417 | 13 |
| 63 | -397 | 15 |
| 64 | -390 | 13 |
| 70 | -339 | 32 |

All 15 stages are increasing with sequence; between every consecutive pair of *matches*, the slope is between 4 and 11 modeled output draws per recorder row. A 100,000-trial fixed-seed negative control randomly reassigns source-matched stage values to 15 of the 72 historical sequence labels. The maximum slope-consistent ordered chain across those shuffles is **seven**, compared with all **fifteen** original matches. This is a retrospective signal calibration, **not** an unconditional p-value. Strong source-stage selection and generator-family/model-selection caveats remain.

## Independent seq44 metadata check and timestamp falsifier

The seq44 CONTROL at native -545 was selected by matching CONTROL bits only. Before using its adjacent metadata, freeze the distinct four-field producer hypothesis `latch=getrandbits(3); CONTROL=getrandbits(32); AUX=2000+randrange(6000); event=1+randrange(40)`, allowing at most three rejection samples per AUX/event. Original source-fixed adjacent tempered words then predict:
- stage -546 upper3 = **2**, exactly original seq44 latch **2**;
- stage -544 upper13 = **5700**, exactly original seq44 AUX **7700** after base 2000;
- stage -543 upper6 = **27**, exactly original seq44 event **28** after base 1.

These are **22/22 source-fixed metadata bits**, with **zero rejection samples needed** for this heldout record. At the other eight independently known original CONTROL anchors (seq7,12,13,24,25,41,45,70), the same local four-field sampler has at least one consistent bounded-rejection assignment, agreeing with 83 additional source-fixed metadata bits. The combined nine-anchor total is **105 source-fixed matching metadata bits**. This is a useful candidate producer mechanism and a strong discriminator for a shared precomputed generator.

**Important falsifier:** The naive follow-on timestamp rule `time=21:09:00 UTC + randrange(400)` at the *next* stage -542 predicts 200 seconds from the source-fixed upper9, whereas actual seq44 time offset is **57 seconds**. Likewise, forcing strict consecutive five-field rows without inserted/independent stages fails against early intact records. Do not describe that wider producer as established. Time may use a separate clock, transformation, or a different stage.

## Target-facing frontier

Jointly insert all 15 source-indexed original CONTROL 32bit observations and the nine chosen source-consistent three-field metadata assignments into the exact original GF(2) system. Rank advances **15,365 → 15,459 (+94)** without inconsistency; four withheld K04 native words at p951 stage951..954 still contribute **128/128 independent unknown bits**. The source-matched recorder chain therefore advances *producer hypothesis discrimination*, while the original K04 component remains unrecovered. The original six slots remain PASS, K04/K08 MISSING, combined INCOMPLETE.

A productive next experiment is to infer the **interleaved/clock stage placement** of the remaining recorder records with explicit heldout prediction, then test whether genuine source-indexed later-stage carriers intersect the selected 128-bit coupon quotient. Simply harvesting additional negative-index controls will not by itself authenticate a missing selected physical coupon.

**Source pins:** original printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; TRP2 recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`. Original recovery commitments, selected ACK, candidate and verifier unchanged.
