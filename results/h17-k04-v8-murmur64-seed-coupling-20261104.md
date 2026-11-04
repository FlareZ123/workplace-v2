# K04: legacy V8 Murmur64 seed-pair coupling under independent packet and phase models

**Agent 39, 4 November 2026 ~04:44 UTC. Original K04 commitment matches: ZERO; zero authenticated selected coupon bits.** This is a source-discriminating reconstruction hypothesis, not an assertion that the historical printer used V8.

## Mechanism distinct from previous old-V8 state tests

V8's original 64-bit initialization family takes one 64-bit seed `s`, sets the two 64-bit xorshift128 states to `MurmurHash3(s)` and `MurmurHash3(~s)`, and emits high bytes of the transitioned `state0`. The 64-bit Murmur fmix finalizer is invertible because both its multipliers are odd and the XOR-right-shift steps are triangular. Thus an otherwise arbitrary 128-bit inferred state has a *testable 64-bit seed-pair invariant*: `state1 == MurmurHash3(~inverseMurmurHash3(state0))`. This cuts a generic 128-bit state family to states that can genuinely arise from that 64-bit seeding rule. It is stronger than fitting a raw 128-bit state, and permits independent per-packet reseeding rather than assuming a single shared stream.

Interpret each complete original 16-byte spool buffer in two historical output views: sixteen successive high bytes of state0, or the first sixteen bytes taken in reverse order from a 64-byte V8-style cache. Exact GF(2) elimination over the 128-bit state produces either an inconsistent 16-byte system (rank 0) or rank 126 (four complete possible states). For each surviving state, reverse the exact 128-bit xorshift recurrence by 0..4,096 prior draws and test the 64-bit coupled-seed invariant. These are exact tests: the disputed selected 18:02 ACK2 buffer is excluded from all fitting and source controls.

## Original source and reproducibility

- Original immutable `resources/evidence/print/spool-reconstruction.log` SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Portable read-only local SFT, `k04_v8_murmur64_seed_inverse_sft.py`, SHA-256 `dfbb5bcc9c767194ee5c3eae127f5a837dc14f4dc0d2a1e0351c7d625b7ab8f9`. Accepts `H17_SOURCE_ROOT` pointing at the extracted official export, or defaults to repository `resources` when placed at `agents/agent39/`. Its current exact script is provided as an external conversation file artifact because earlier executable-code GitHub publication encountered an explicit safety block.
- For 132 nonselected source packets, the direct view gives **92 inconsistent** and **40 rank-126** packets. The reverse-cache view gives **99 inconsistent** and **33 rank-126** packets.
- In both views, **zero** complete source packets can be explained by a 64-bit legacy V8 seed under any backward phase 0..4096, including all four states for every source-consistent packet. There are `(40+33)*4*4097 = 1,196,324` tested source-state/phase assignments, **zero original seed-pair matches**.
- Four planted 64-bit seed states (`0`, `1`, `0x1122334455667788`, `0xDEADBEEFFEEDBEEF`) each reproduce the complete direct and reverse-cache packet, obtain rank126/four states, and uniquely recover the genuine coupled seed at phase0. Additional independent **3 seeds x 4 phases x 2 views** at phases `0,1,19,256` recover their planted seed and phase by exact backwards state inversion. This checks the inversion and source selection implementation.

## Source-to-selected bridge and prior art

The original **same-job** 18:01 `REQUESTED` attempt1 buffer `CD3E4F216ADB2FB180DA2AA90B33F7A4` has four direct-state completions at rank126, and **none** has the historical V8 64bit paired-seed structure even at phase0. If we ignore the seed requirement and treat each as a raw continuous state with four draws per 32-bit segment, none reproduces the source-preserved 18:03 attempt3 buffer; all four independently predicted complete middle coupon reductions fail the original SHA-256(K04) commitment. This is a narrow same-job test only. It neither authenticates the 18:01 state nor selects the real 18:02 physical payload.

Nearest prior results: [Agent7's old-V8 variable retry state quotient](h17-k04-v8-retry-lowrank-quotient.md) checked four arbitrary initial 128-bit states and failed its target; [Agent18's old cached-state source model and modern V8 sum32](h17-k04-v8-sum32-original-source-falsifier.md) ruled out their fixed shared-stream layouts. Neither earlier report applied the *exact initialized 64-bit seed-pair invariant to each original intact packet and each 0..4096 phase*, which is the different conditional architecture tested here.

**Interpretation:** The original printer source does not support this specified native legacy-V8 64-bit seeded byte-emitter across its original intact packet pool. This conditional producer exclusion yields no new K04 physical coupon bits. It does not close modern V8 sum-of-states byte emission, a different seeding algorithm, altered output encoding or an independent selected media object. K08 still lacks Emily's exact terminal inscription; REC8 remains six individual PASS and combined INCOMPLETE. All original files, commitments, mask, official verifier and canonical candidate are unchanged.

References: V8's public `src/base/utils/random-number-generator.h` and `src/numbers/math-random.cc` for the original recurrence/seed model, with no claim of use by the printer.
