# K04 eight-pair printer-copy stage diagnostic (4 November 2026)

**Agent 16, original source-bound negative.** The original accepted REC8 slots remain K01, K02, K03, K05, K06 and K07; K04 and K08 are still unresolved and combined acceptance is INCOMPLETE.

## Question and prior-art boundary

The selected physical coupon for logical ESC-N, job `PS-261003-0417`, RECOVER ACK attempt 2, is represented by a *reconstructed* spool copy lacking independent integrity authentication. A specific possible copying mechanism would preserve all eight adjacent 16-bit fragments while transposing their order and/or reversing the two bytes inside each fragment. Fragment boundaries at 2-byte intervals are a hypothesis about a copier/serializer, **not identified by an original printer document**.

The older workplace-v1 [contiguous-fragment permutation SFT](https://github.com/FlareZ123/workplace-v1/blob/main/results/check_h17_fragment_permutations.py) enumerated arbitrary source cuts and orientations for **2..5 fragments**; its precise bounded test did not include all **eight prealigned 2-byte fragments**. V2 [byte-lane reassembly](h17-k04-lanewire-permutation-sieve.md) covers independent byte permutations within four fixed 4-byte words, while [bit-raster readback](h17-k04-bit-raster-readback-model.md) spans a distinct family of structured raster mappings. This eight-pair model is a modest, finer-grained finite extension; the broad copy-stage premise overlaps heavily with previous research and has low independent historical support.

## Original-bound candidate construction

Original printer source SHA256:
`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

Selected original copied spool `P=A9A9DC5731A5E2AE879C47215C2559D5`; prescribed route mask `M=8556C8CB6140A7F9A5123AC7571BEE1C`; unchanged K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

For a permutation `T` of the eight aligned two-byte segments with an independent within-segment reversal flag, construct three *complete* 16-byte candidate components:

- Stage 0: `T(P) XOR M`, copying/ordering the opaque payload before the route reducer.
- Stage 1: `T(P XOR M)`, copying/ordering the already-reduced component.
- Stage 2: `P XOR T(M)`, treating the route mask itself as the transposed buffer.

The exact construction evaluates `8! × 2^8 = 10,321,920` assignments per stage, with the original full SHA256 check applied to every 16-byte component. The selected first payload pair `A9A9` means stage 0 has two assignments for each generated coupon, so assignments must not be described as distinct values. The recorded source metadata and hash are checked before the enumeration.

## Executed result and controls

Compiled the source-pinned C++17/OpenSSL SFT locally and ran it against the untouched original spool:

```text
pairs=8 permutations=40320 flips=256 assignments=10321920
original_by_stage=0,0,0
planted_by_stage=2,1,1
```

Thus **30,965,760 complete candidate-stage SHA256 comparisons produced zero original K04 commitment matches**. Three independent in-memory planted complete commitments were generated with nonidentity fragment permutation `(7,1,4,2,6,0,5,3)` and within-fragment reversal. Their exact multiplicities, 2/1/1, were recovered and asserted; stage 0 duplicates because its copied first pair is `A9A9`.

The [read-only source-pinned single-file test](../agents/agent16/k04_eight_halfword_stage_sft.cpp) is retained. Reproduce on a C++17/OpenSSL installation against `resources/evidence/print/spool-reconstruction.log`. No resource, original candidate, route, verifier or acceptance commitment was changed.

## Scope and next direction

An authentic K04 cannot be obtained **within these three specified eight-fragment permutations** of the selected copied payload and mask. Nothing establishes this transfer model or the selected physical coupon. This negative adds no independently authenticated selected K04 bit, no final K08 word, and no new accepted REC8 component. A different actual producer/transfer source, original selected coupon or author-final keeper caption remains required for complete recovery. Do not expand arbitrary fragment counts merely for computational novelty without a source-based copying stage cue.
