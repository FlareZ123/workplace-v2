# K04: exact two-gap native-MT coupon constructor and original-source rank synergy

**Agent18 | 9 November 2026 | original selected physical coupon still unresolved.**

## Recovery route, conditional on native producer

Fresh [Agent23 source-only gap constraints](../agents/agent23/k04_mt_stagefree_gap_bounds_sft.py) place two antecedent 4-word MT19937 blocks for the historical ESC-N selected event in *unprinted* ordinary spool intervals. A prior independently sourced p951-compatible writer schedule assigns:

- Original intact printer **row43** `PS-261003-0343` to native starts 324..327, with word327 known from its last four source bytes.
- Missing native **328..331** to the unprinted interval before row44 starts at 335.
- Original intact printer **row96** `PS-261003-0396` to native starts 717..720.
- Missing native **724..727** to the unprinted interval before row97 starts at 729.
- Selected disputed **row129** `PS-261003-0417, ACK2, RECOVER` to native starts **951..954**.

No original source selects this MT schedule as the historical physical printer producer. These are **conditional positions**, not factual metadata on actual missing native print jobs. The selected copied `A9A9...` spool field must never be treated as authenticated paper/coupon data.

### Deterministic complete-coupon constructor

If two **independently indexed and authenticated** native output blocks `S[328..331]` and `S[724..727]` are recovered as four whole consecutive 32-bit MT words each, then existing intact printer native word `S[327]` plus them uniquely determine the entire 128-bit selected source packet:

For each `j=0,1,2,3`, set `t=327+j` and compute

```text
Y       = (S[t] & 0x80000000) | (S[t+1] & 0x7FFFFFFF)
S[951+j]= S[724+j] XOR (Y >> 1) XOR ((S[t+1] & 1) * 0x9908B0DF)
```

All operations are unsigned 32-bit. Untemper the independently recovered 32-bit **printed** output values to get native S words. Temper computed `S[951..954]`, serialize each as little-endian u32, concatenate to 16 bytes, then XOR the **unchanged original** K04 mask `8556C8CB6140A7F9A5123AC7571BEE1C`. Only then compare SHA256 of the complete 16-byte result to historical K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Even a producer-consistent output requires the original acceptance to succeed before becoming a recovered key.

The independently implemented `reconstruct_selected_native` is in the linked [single-file SFT](../agents/agent18/k04_mt_causal_gap_residual_sft.py), and three genuine seeded Python MT19937 outputs yield three **complete withheld 16-byte synthetic selected packets** reproduced exactly. No original missing donor data was fabricated.

## Original-source quantitative value of each missing block

The original unmodified printer SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected copied row129 is excluded from the original-source GF(2) model. Rebuilding [Agent49's 15,365-rank exact symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py), then conditioning on independent complete native output words at those two target-causal gaps, yields:

| Indexed external donor data assumed | New independent source rank | Selected 128-bit uncertainty remaining |
| --- | ---: | ---: |
| None | 0 | 128 |
| Only source block 328..331 | +128 | 128 |
| Only source block 724..727 | +128 | 127 |
| Both complete original blocks | +256 | **0** |
| Blocks 328..330 and 724..727 | +224 | 31 |
| Blocks 328..331 and 724..726 | +224 | 32 |

All seven genuinely intact historical control packets used to test the rank function add exactly zero new dimensions. The selected q951..954 and each individual 4word missing precursor window have independently **128/128 free bits** under source-only constraints. Thus a value-only match to an unindexed 16B blob cannot authenticate a missing donor. The identity, stage and physical origin of both independently recovered blocks must be supported, rather than chosen because the computed result happens to fit the target hash.

## Scope and next concrete action

This **does not recover K04** because neither required indexed complete 16-byte donor is retained in the original 46-file preservation ZIP. It supplies a precise two-block acquisition and reconstruction procedure that would replace the damaged paper coupon if the underlying producer hypothesis is correct.

Seek the native per-output buffer/queue stream spanning **row43→44 and row96→97**, with source-byte integrity and original chronological native indices, or a producer initialization witness that reconstructs these exact words. The observed job records surrounding these gaps and two independently indexed source objects should be treated as separate evidence until a native manifest establishes the stage mapping. The usual independent physical paper-copy witness remains valid without the MT assumption.

Original six components K01/K02/K03/K05/K06/K07 remain PASS. K04 and K08 are MISSING; combined REC8/1 remains INCOMPLETE. Original source files, verifier, commitments, routing and canonical candidate were not changed.
