# K04 source bridge: K02 freeze halfwords do not match any printer MT three-output ancestor run

**Agent 9, 2 November 2026. Source-only new carrier probe, NO_MATCH.** No K04 selected coupon bit and no K08 exact word recovered. Original evidence, acceptance inventory and verifier were unchanged.

## New source-conditioned hypothesis

K02 derives from eight unsigned original `LT-204 / DIAG_WORD` 16-bit telemetry readings, selected as `GOOD / HOLD`, maximal revision for each sequence 0..7, within the source route's UTC interval. The eight original values before K02's final SHA256 reducer are:

`E1A5 E474 BAD7 E853 A2E8 C71D 3317 D507`

A previously observed MT19937-style relation among the **intact** printer words exposes 31 bits of an otherwise hidden ancestral generator state from a pair of outputs 227 generator positions apart. Two adjacent inverse-twist pairs yield a *complete* intermediate 32-bit ancestral state. A four-output pair of printer rows therefore exposes three full consecutive ancestral words, regardless of their unknown absolute stream index.

The hypothesis is that the original K02 diagnostic values are three *successive* 16-bit extracts of such a hidden printer MT output run, perhaps produced by a common offline/test-data generator. This is a model, not an attested historical cross-equipment link. We test native numeric and byte-swapped telemetry interpretations, and the upper/lower 16 tempered bits, rather than silently asserting a serialization convention.

This adds a **new carrier** to the successful v1 [AX-7778 three/four-halfword printer bridge](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-transfer-checkpoint-16bit-bridge.md). It is distinct from v1 Agent 2's **fixed-index p955 future-word** K02 test in `agents/agent2/k04_k02_future_halfwords.py`: the present scan searches *all intact printer pairings* at their relative offsets, no p955 model, no K04 target commitments.

## Exact source-only sieve

Source pins:

- Printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Freeze telemetry SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`.
- Disputed spool row129 (the 18:02 ACK2) removed before every state and donor computation.
- No K04 route XOR mask, K04/K08 SHA commitments, candidate key or combined verifier accessed.

For any increasing pair of *distinct* intact spool rows, untemper their four little-endian 32bit payload words `M[i]` and `E[i]`. For each position `i`, form `v[i]=inverse_twist(M[i] XOR E[i])`, where `inverse_twist` reverses the MT19937 0x9908B0DF recurrence. Its highest bit is one ancestral top bit; its lower 31 bits are the following ancestral state's low bits. Combine adjacent `v` to reconstruct three complete consecutive ancestor state words in each four-word pair. Temper these and compare any consecutive K02 length-three selection in four serialization/projection interpretations.

A companion three-output pairing starts at each source-row offset `(0,1)`, `(1,0)` or `(1,1)`. Two complete ancestors result; both possible highest-bit completions for the third partial ancestor are considered. Source labels and byte values remain unchanged.

| Source-derived assignment class | Complete original assignments | Original three-halfword source matches |
|---|---:|---:|
| Four printer words, three reconstructed full ancestors | **207,504** | **0** |
| Three printer words, two full plus one partial ancestor | **622,512** | **0** |
| **Total** | **830,016** | **0** |

This counts exact assignment tests, including orientations and source-sequence start positions, rather than guaranteed unique phrase/word triples. All 132 intact printer rows are included, giving `C(132,2)=8,646` pairings. A real CPython `random.Random(12345678)` MT stream is generated as an independent synthetic positive: actual outputs 397..400 and 624..627 reconstruct *exactly* actual ancestral states 1..3 and their original upper 16 tempered bits. Positive passes. There is no source-selected posterior candidate to test against the original K04 hash.

**Reproduce:** `python agents/agent9/k04_k02_mt_halfword_bridge.py source-archive.zip`. Standard-library Python; portable input ZIP argument; source-only and no file writes. Source code [here](../agents/agent9/k04_k02_mt_halfword_bridge.py).

## Consequence and next step

Under the defined MT recurrence/three-consecutive-output/16bit serialization model, K02 raw telemetry furnishes **no** new independently matched ancestral source run. In particular it cannot currently bridge the disconnected row43/44 or row96/97 target-side printer groups identified in v1 [source-indexed target donor cut](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-source-indexed-target-donor-cut.md). This is a source-only producer-conditional exclusion, not a proof of independent historical equipment generators.

The other source channels remain possible if a new calibrated transformation or *indexed* donor relation emerges. The copied K04 selected ACK still fails original acceptance, K08 final author-caption wording is not quoted. K01/K02/K03/K05/K06/K07 retain their earlier individual PASS status; REC8 combined remains INCOMPLETE and accepted false.
