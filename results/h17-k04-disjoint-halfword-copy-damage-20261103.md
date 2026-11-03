# K04: two separated 16-bit-aligned copy-damage repairs, complete original commitment exclusion

**Agent 38 | 3 November 2026 | 19 GitHub Actions jobs SUCCESS, 81,604,378,624 exact K04 SHA256 assignments, 0 original matches.**

## Target and source

The historical selected incident record remains ESC-N / `PS-261003-0417` / RECOVER / attempt 2 / 18:02 UTC. The selected reconstructed spool buffer is `A9A9DC5731A5E2AE879C47215C2559D5`; the source route mask is `8556C8CB6140A7F9A5123AC7571BEE1C`. Their recorded XOR reduction `2CFF149C50E54557228E7DE60B3EB7C9` fails the unchanged official K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The original spool bytes were pinned by SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` in every job.

The selected physical coupon is not independently authenticated by an ACK. This study assumes a *specific possible copying fault*, not a confirmed damaged physical print or a recovered original.

## Distinct full-coupon reconstruction

The copied ACK could hypothetically differ from the true coupon in exactly **two separate 16-bit-aligned halfwords** within its 16-byte packet. Since the recorded mask is fixed, the same four byte replacements are possible directly on the reduced component. For each pair of halfword starts `a,b`, replace byte positions `a,a+1,b,b+1` with every four-byte assignment. The other twelve bytes remain fixed.

There are eight aligned halfword starts `{0,2,4,6,8,10,12,14}`. Among the 28 unordered start pairs, omit the seven adjacent pairs, already exhausted by contiguous-four-byte searches; also omit `(0,8)`, exhausted by Agent10 on 30 October, and `(0,14)`, exhausted by v1 Agent8 on 20 October. This leaves **19 previously unexhausted supports**:

```
(0,4)  (0,6)  (0,10) (0,12)
(2,6)  (2,8)  (2,10) (2,12) (2,14)
(4,8)  (4,10) (4,12) (4,14)
(6,10) (6,12) (6,14)
(8,12) (8,14) (10,14)
```

Each support has `2^32 = 4,294,967,296` full candidate assignments. The union contains overlap on partially unchanged bytes, but all such lower-footprint candidate classes were previously excluded by the original commitment; the 19 independent full-support sweeps cover exactly the stated two-disjoint-halfword model.

## Source, controls, and actual execution

- [Precommitted exact scope](../agents/agent38/k04_two_disjoint_halfword_preplan.md), written before the target sweep.
- [C/OpenSSL/OpenMP original-commitment program](../agents/agent38/k04_two_disjoint_halfword_sft.c). A four-byte replacement planted into support `(0,4)`, with complete synthetic SHA256 target, was recovered in a positive-control subrange. The source pin, selected record, mask and original commitment are rechecked before every exhaustive run.
- [Explicitly manual GitHub Actions workflow](../.github/workflows/agent38-k04-disjoint-halfword.yml), no automatic push-triggered cost.
- [Completed 19-job run, 3 November 2026](https://github.com/FlareZ123/workplace-v2/actions/runs/41721471264). Every job concluded **SUCCESS**. Individual target comparison logs were retrieved through the GitHub Actions log reader: every job contained exactly `DONE support_id=N complete_candidates=4294967296 original_hits=0`, and together the supports covered each `N=0..18` once. Total full SHA256 assignment checks **81,604,378,624**, **0 original K04 matches**.

The bitplane-corruption hypothesis in [Agent38's separate test](../agents/agent38/k04_bitplane_copy_fault_sft.py) is a different fault topology; it also returned zero original hits with a planted positive. Neither technique reproduces the original selected physical print.

## Scope and decision

This is a full negative **only for this selected-copy error family** under the recorded original mask. It does not exclude modifications to five or more bytes, unaligned halfword faults, a false mask, a different original source object or a non-copy-stage producer. A synthetic positive validates computation, not historical source provenance. Do not expand to arbitrary four-byte supports without a reason from the surviving original records.

**Actual authenticated K04 bits gained: 0. K08 original final-caption words gained: 0.** Original K01/K02/K03/K05/K06/K07 still individually PASS; K04 and K08 remain MISSING, combined REC8 INCOMPLETE. No official source, acceptance file, original verifier or candidate was altered.
