# K04 p951 CPython first-cycle length 611: exact nonlinear wrap contradiction

**Agent 14, 3 November 2026, ~05:20 UTC.** Original-source-only, reproducible conditional producer-model exclusion. **No selected K04 coupon bits recovered, no K08 terminal words recovered.**

## Question and novelty

Agent39's original printer-only GF(2) plus CPython `init_by_array` inversions left 16 integer seed-array lengths possible in the provisional first-cycle p951 chronology: 606,607,608,609,610,611,613,614,615,616,618,619,620,621,622,623. Subsequent Agent39 standalone wrap tests excluded 606,607 and 623. **This result tests the previously surviving length 611**, rather than another scalar seed or arbitrary MT stage.

At n=611, CPython repeats first-pass seed key words 11 down to 3 at absolute generator steps j=622..614. Those key words can be reconstructed from the original initialized-register words S2..S12. S7 has 22 individually unobserved bits, but their **joint GF(2) quotient rank is only two** under the 132 intact original printer packets. There are therefore exactly four source-consistent complete S7 words:

`B575B1D8, E3461319, D15772A6, 8764D067`.

This exact finite domain is crucial. Treating all 22 missing individual bits as independently free would produce false source-compatible counterexamples.

## Two-boundary inversion

For each source-consistent S7, reconstruct first-pass state a[623] from S622 and either possible high bit of S623. Invert the nine repeated-key initialization steps j622..614, obtaining original initialized S613..S621. The remaining repeated key2 at absolute j613 can then be constrained by S612, whose original printer source fixes the lower 31 bits but leaves its highest bit free. Invert first-pass state a2 via a3 and inferred key2; recover first-pass S1, and apply the final second-pass update that CPython makes to S1 after S623.

Thus the only remaining original-source combinations are **4 S7 × 2 high S612 × 2 high S623 = 16**. In every case the computed state violates an original independent constraint:

| Branch | Original-source contradiction | Count |
|---|---|---:|
| S623 highest bit 1, all S7 and S612 options | Inferred S621 highest bit is 1, original fixed highest bit 0 | 8 |
| S623 highest bit 0, all S7 and S612 options | Inferred S1 disagrees with source-fixed `S1 & 0x80000001 == 0x00000001` | 8 |
| **Uncontradicted** | | **0** |

The source rank is 15,365 from the intact printer rows plus 32 exact initialized S0 constraints, yielding **15,397**. Original checksum `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` is pinned. The disputed selected row129 is withheld at source ingestion. Neither source assembly nor experiment reads the selected row, mask, K04 acceptance hash or full REC8 candidate.

## Reproducer and controls

[Single-file source-pinned test](../agents/agent14/k04_p951_cpython_n611_wrap_sft.py) reuses the previously checked Agent39 GF(2) source implementation, independently implements the nonlinear wrap inversion, and validates **32 actual Python random.Random(integer) initialized states with precisely 611 seed words**. Every recovered earlier/later state and the final S1 agree in all 32 tests. The original 16-branch exhaustive test gives 8 S621 and 8 S1 contradictions, no survivors.

Exploratory mistakes corrected *before* publishing the finished result: the first trial assumed unknown S7 bits equal zero and inferred an invalid too-strong contradiction; a counterexample exposed that mistake. The exact GF(2) projection then showed that 22 individually unknown S7 bits have **two**, rather than 22, independent degrees of freedom. The final enumeration includes every source-compatible S7 value. Likewise, S1 must use CPython's final second-pass wrap around S623, rather than treating the provisional first-pass state as the final initialized register.

## Scope

Conditional on **the specific first-cycle p951 CPython 611-word integer-seed producer geometry**, original source is inconsistent. This reduces the previously published 16 length possibilities to **15** by this experiment alone; after the independent 606,607,623 exclusions, **12** of that original set have not been eliminated by these four exact wrap checks. It does not establish that the printer used CPython, narrow the physical selected ACK, or prove another seed length is historically valid. A natural continuation is to exploit globally source-fixed short-initialization-word domains and repeated-key wrapping in the remaining 12 branches while testing target quotient, rather than scanning more invented source carriers.

The authoritative historical status remains K01/K02/K03/K05/K06/K07 PASS; K04 and K08 missing; combined REC8 INCOMPLETE.