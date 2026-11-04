# K04: K05 latch-index rotating common-mask source bridge (4 November 2026)

**Agent13 | source-conditioned complete K04 candidate construction | zero original matches**

## Hypothesis and original source controls

Extend [Agent9's shared unknown 32-bit K05 recorder whitening-mask model](h17-k04-k02-k05-shared-recorder-whitening-20261104.md) with a **latch-dependent rotation of the same unknown mask**, preserving only 32 unknown mask bits across all four selected recorder latches:

\[
O_i = W_{2139+227i}\ \mathrm{XOR}\ \operatorname{ROL}_{32}(M,r i), \quad i=0,1,2,3.
\]

The variation permits a deterministic inter-latch whitening schedule instead of allocating a separate mask to each latch. It is a conditional producer theory; no original recorder or print-firmware note attests a shared MT stream, p951 source chronology, fixed 227-latch gap or rotating mask.

The exact source state comes from the existing [Agent49 printer symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py): 132 *nonselected* intact printer payloads, rank **15,365**, 128 selected coupon bits withheld. Independently use source-accepted K02 telemetry prehash \`E1A5E474BAD7E853A2E8C71D3317D507\` at either hypothetical native stage **1178 or 1405**, across 16 original source presentations, then the exact selected K05 node49/event82/latch0..3 opaque words \`FF8B78200A56E8586DCDA00EF01E4572\` at stages 2139,2366,2593,2820. Here the K05 serializer is the previously source-compatible native-untempered little-endian view; no K04 ACK2 copied bytes enter fitting.

The 32 rotations \`r=0..31\` and two K02 stages x sixteen K02 views yield **1,024** distinct source-equation assignments. The source mask \`M\` is a 32-variable vector, and each latch's bit is linked to \`M[(bit-r*i)%32]\` by *exact* GF(2) elimination. Original route XOR mask and K04 target commitment enter only when enumerating source-consistent **complete** coupon candidates. No original source, verifier, acceptance file or candidate was modified.

## Exact source quotient and commitment checks

All **1,024** source assignments remain algebraically consistent, with this distribution of residual missing selected-coupon dimensions:

| K04 residual degrees of freedom | Number of assignments | Complete candidates tested |
| ---: | ---: | ---: |
| 4 | 64 | 1,024 |
| 9 | 64 | 32,768 |
| 21 | 128 | 0 (large coset; withheld) |
| 27 | 256 | 0 (large coset; withheld) |
| 30 | 512 | 0 (large coset; withheld) |
| **Total** | **1,024** | **33,792** |

The low-dimensional cases arise exclusively at r=0,8,16,24. Under all 128 such assignments, the full K04 candidate values were derived using the source state's native MT equations, serialized as little-endian tempered 32-bit words, XORed with the **unchanged** original route mask, and checked with the full original SHA256 commitment. **Zero hits in 33,792 complete original checks; 16,384 distinct components.** Rotation0 partially reuses the already reported fixed-mask family and is included as a structural control, not as a new independent exclusion. Rotations 8,16,24 are the additional source-derived complete-candidate families.

All remaining r values leave at least 21 target degrees of freedom; source compatibility alone is insufficient to nominate one complete original coupon, so this study did not expand into arbitrary \(2^{21}\) through \(2^{30}\) coset enumeration for a producer with no historical identification.

Four independent planted true MT histories with an unknown 32-bit mask rotated by r=0,8,16,24 **each recovered their genuine selected coupon exactly once** through the same symbolic quotient and exact candidate enumeration. These are real synthetic generator controls, not original-source successes.

## Reproduction and limit

Read-only [Agent13 self-contained study using Agent49's shared GF(2) library](../agents/agent13/k04_rotated_recorder_mask_sft.py). Original observed printer SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\` is asserted by the imported symbolic source model. Original K05 is verified against its untouched commitment; synthetic positives exercise the complete K04 reducer.

This model is distinguishable from a shared *constant* K05 whitening mask, but the source does **not** select a rotation or prove the printer and selected recorder used a single engine. The residual large-coset assignments remain untested, and none of the tested models supplies authenticated physical ACK2 bytes or K08 final-caption words. **REC8 remains K01/K02/K03/K05/K06/K07 individually PASS, K04/K08 unresolved, combined INCOMPLETE.**

A high-value next experiment would identify a historical latch-dependent mask schedule from a second **selected** recorder cohort or a genuine printer writer specification. Without it, adding unconstrained rotating masks only relaxes the target coupon further.
