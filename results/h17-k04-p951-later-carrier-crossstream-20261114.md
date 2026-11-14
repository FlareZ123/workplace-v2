# K04 p951 later-carrier cross-stream test

**Date:** 14 November 2026  
**Status:** Negative, bounded, reproducible  
**Script:** [`agents/agent6/k04_p951_later_carrier_sft.py`](../../agents/agent6/k04_p951_later_carrier_sft.py)

## Question

The conditional p951 MT19937 model built from 132 intact printer packets and 15 node50 control matches leaves all 128 bits of the selected K04 packet at stages 951–954 unconstrained. A source-motivated extension is to test whether later recorder material supplies the missing stage constraints:

1. the four K05 node49/event82 control words selected by the signed routing rule; and
2. the eight raw LT-204 DIAG_WORD values selected by the K02 freeze rule.

The HST PV fields were deliberately excluded: the telemetry export readme labels them engineering context, not raw diagnostic words.

## Method

- Rebuild the exact p951 symbolic basis from the repository's existing source function (rank 15,365).
- Extend its MT recurrence through stage 2,500.
- Reproduce the existing node50 model's 15 control matches and nine metadata anchors. Its joint rank remains 15,459, and the four target words at stages 951–954 retain 128 unknown bits.
- Search all 72 node50 records for metadata-only stage matches with at least 20 source-fixed bits. Only seq 9 at stage -793 and seq 44 at stage -545 appear; both are already in the control-match set.
- Select K05 node49/event82 rows in the exact UTC window, reject bad CRCs, and take greatest valid sequence per latch. Test their four 32-bit control words against every p951 output stage 951–2,500, requiring at least eight fixed bits.
- Select K02 DIAG_WORD values using the exact tag/field/quality/state/window/sequence/revision rule. Test both Python `getrandbits(16)` high-half and raw low-half interpretations against every p951 output stage 951–2,500, again requiring at least eight fixed bits.

## Result

- No selected K05 control word matches any later p951 output stage at the eight-fixed-bit threshold.
- The eight selected K02 DIAG_WORD values do not form a source-ordered later-stage chain. At most, isolated half-word matches occur; they do not provide the eight ordered carriers required to constrain the target.
- The node50 metadata-only search discovers no additional stages beyond two already-known anchors.
- The p951 target quotient remains **128 unknown bits**.

## Interpretation and limit

This rejects the specific claim that the selected K05 latch words or the K02 raw DIAG_WORD block are later-stage outputs of the same p951 MT19937 stream that explains the node50 control anchors and printer-packet geometry. It does not disprove the local node50 fit, nor does it recover K04. It also does not justify treating HST PV values as raw generator words.

The surviving export still lacks an authenticated native source that determines the K04 packet. Do not repeat this exact p951/K05/K02 join or broaden it into another blind PRNG sweep. A future attempt needs a materially different target-bearing source relation or the native ESC-N coupon/spool artifact.
