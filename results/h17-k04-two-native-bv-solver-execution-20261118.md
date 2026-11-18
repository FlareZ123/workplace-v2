# K04: complete missing-middle coupon inversion with two bit-vector engines (18 November 2026)

**Agent 8. Original K04 remains unresolved; no original full-coupon model was obtained.** The original recovered archive components K01/K02/K03/K05/K06/K07 remain individually accepted. K08 remains missing; combined REC8/1 is incomplete.

## Question and target-facing model

The selected physical source for K04 is the 18:02 UTC ESC-N, PS-261003-0417 attempt-2 ACK RECOVER coupon. Its copied `PAYLOAD` does not pass the original K04 slot commitment. The preserved same-job *18:01 REQUESTED attempt1* and *18:03 REQUESTED attempt3* provide two complete, distinct 16-byte source records. Their original bytes are held as immutable source pins:

- attempt1 `CD3E4F216ADB2FB180DA2AA90B33F7A4`;
- attempt3 `44D53DFC29D7943A95D89371DA58EC64`.

A speculative same-stream producer model interprets each request as two consecutive native 64-bit `xoroshiro128++` outputs, at indices 0,1 and 4,5 respectively, treating the missing attempt2 as indices 2,3. It tests four conventional endian/word-order views. The `xoroshiro128++` transition and output scrambler are expressed exactly as fixed-width 64-bit equations. **The selected ACK2 copied payload is never used as solver input.**

The direct and algebraically eliminated versions of this model had already been investigated by Agents 23/4/50, including a CryptoMiniSat XOR formulation. The present contribution is a **native Bitwuzla 0.9.1 comparison against Z3 4.15.4**, with executed planted full-coupon controls and complete independent source readback. This is a solver-backend execution check of a previously proposed causal hypothesis, not a newly discovered printer relation.

## Executed, source-pinned results

| Solver | Planted inversion with 16 known low bits of initial s0 | Original 4 exact-source serializer views | Original candidate produced |
| --- | --- | --- | --- |
| Z3 QF_BV 4.15.4.0 | SAT, complete planted middle coupon recovered in **1.041s** | All four **UNKNOWN** after **360.0s/view** | **No** |
| Bitwuzla 0.9.1 | SAT, complete planted middle coupon recovered in **1.660s** | All four **UNKNOWN** after **360.0s/view** | **No** |

The genuine planted initial state was `5D1DE1A5CAFEBEEF / 17A5B3CB69A1CBCA`; the independently generated two missing native words serialize under little-endian forward order to `A5B673F0C2A585BD63DAD6E1497F9ECF`. Both engines recovered the identical full withheld 16-byte packet from planted flank outputs with the low16 state control. This is a bounded **conditional inversion-liveness** result. No corresponding state restriction is present in the real source.

- Z3 planted [run 44278764142](https://github.com/FlareZ123/workplace-v2/actions/runs/44278764142) and four-view original [run 44279200904](https://github.com/FlareZ123/workplace-v2/actions/runs/44279200904); script [`agents/agent8/k04_xoroshiropp_bv_bracket_sft.py`](../agents/agent8/k04_xoroshiropp_bv_bracket_sft.py), [manual workflow](../.github/workflows/agent8-k04-xoro-bv.yml).
- Bitwuzla planted [run 44280130176](https://github.com/FlareZ123/workplace-v2/actions/runs/44280130176) and four-view original [run 44280307239](https://github.com/FlareZ123/workplace-v2/actions/runs/44280307239); script [`agents/agent8/k04_xoroshiropp_bitwuzla_sft.py`](../agents/agent8/k04_xoroshiropp_bitwuzla_sft.py), [manual workflow](../.github/workflows/agent8-k04-bitwuzla.yml).
- Each original script validates the source spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, filters exact 18:01/18:03 UTC RECOVER REQUESTED records, validates both original full payloads, then solves the hidden middle with no low-state prefix. A same-number job occurs at 16:45 with CLASS LABEL; filtering by job alone is invalid. The original acceptance and route mask are unchanged, read only.
- Original Z3 logs explicitly state `solver=unknown reason=timeout`; Bitwuzla logs explicitly state `bitwuzla=unknown`. Every job exits successfully by policy for bounded UNKNOWN, without publishing any selected 16-byte coupon or K04 verdict.

## Interpretation and next decision

This run does **not** falsify the same-job `xoroshiro128++` relation: neither engine proved UNSAT. The four 6-minute unknowns also make further unmodified backend timeout extensions unattractive without a new constraint or inversion algorithm. Previous Agent50 tests found 16-bit planted low-state controls tractable and unconstrained inversion similarly hard. Partitioning 2^16 possible unknown original prefixes would introduce an enormous unsourced combinatorial workload and is not supported by these timings.

The next materially distinct K04 attack should identify **a genuine source-indexed state restriction, a new exact-packet emitter relation, or a stronger algebraic inversion than either native solver**. On K08, continue a complete author-final text recovery rather than near-duplicate phrase guesses.

**Original authenticated missing data after these runs: K04 zero selected coupon bits; K08 zero author-final words. No combined recovery key.**
