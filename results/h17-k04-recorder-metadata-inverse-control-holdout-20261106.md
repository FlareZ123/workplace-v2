# K04: recorder AUX/LATCH-first placement predicts four independent CONTROL fields

**Agent 16 | 6 November 2026 ~00:35 UTC | original-source positive conditional cross-carrier test.** **No K04 physical coupon recovered.** Six original slots remain accepted, K04 and K08 unresolved, combined REC8/1 incomplete.

## Question and source provenance

The previous node50 cross-carrier study [Agent6's 15 CONTROL-selected anchors](h17-k04-node50-fifteen-ordered-prng-word-chain.md) searched recorder **CONTROL** values for source-compatible MT native-stage locations, then verified adjacent metadata. This independent inverse experiment instead **withholds every node50 CONTROL value from stage selection** and attempts to locate a stage using only the original record's 13-bit AUX code and 3-bit LATCH code. Its heldout observable is the **original 32-bit CONTROL word** at the resulting stage. This changes the causal direction of validation while reusing the published printer-only p951 state model, so the four stage locations are previously known, not new stage discoveries.

Read original 133 printer packet rows; remove the disputed selected 18:02 ACK2 whole packet (row129); condition the original p951 native-MT symbolic state on the other 132 original packets. This has rank 15,365 and supplies stage bit-predictions without consulting K04 mask, K04 commitment, or selected copied bytes. Original recorder bytes have pinned SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`; parse all 88 24-byte records, check the known CRC status and sort the **72 intact node50 records** by seq0..71.

## Frozen inverse-stage search

For each native-control candidate stage `q=-999..-253`, require source-fixed complete values at:

- `q-1`: the top **3 tempered MT bits**, equal to the record's original LATCH code (0..3), as a first accepted `getrandbits(3)` sample.
- `q+1`: the top **13 tempered MT bits**, equal to `AUX-2000` (0..5999), as a first accepted `getrandbits(13)` sample.

Use no unknown-bit optimistic fit: every one of those 16 metadata bit positions must be individually determined by the **printer-only** source basis. No recorder CONTROL bit contributes to a stage choice; event, timestamp, acceptance, and copied selected ACK are likewise withheld.

Exactly four complete **original metadata pairs** match any source-determined candidate stage. Before reading each pair's original CONTROL, untemper and predict its separately source-fixed native CONTROL bit positions at the selected q:

| node50 seq | Metadata-selected native q | Original CONTROL source-fixed agreement |
| ---: | ---: | ---: |
| 9 | -793 | **17/17 bits** |
| 13 | -769 | **32/32 bits** |
| 24 | -683 | **32/32 bits** |
| 44 | -545 | **32/32 bits** |
| Total | four unique records | **113/113 bits** |

No inverse metadata match failed its heldout CONTROL. These four controls had appeared among the fifteen prior CONTROL-first matches; this test is a genuinely different within-source **selection/holdout partition**, rather than independent proof of physical firmware.

## Frequency-preserving shuffled-pair control

Freeze the four metadata-selected native stages, their predicted CONTROL values and the original 72 independently retained CONTROL words. Uniformly shuffle the four source-selected *joint AUX/LATCH pairs* among the 72 CONTROL rows (equivalent, for this four-pair statistic, to fully permuting all 72 metadata pairs). Across **200,000** deterministic-seed20261106 shuffled allocations:

| Number of heldout CONTROL matches | Shuffled allocations |
| ---: | ---: |
| 0 | 189,285 |
| 1 | 10,494 |
| 2 | 219 |
| 3 | 2 |
| 4 | **0** |

The original records yield **4/4**. An add-one tail of **1/200001 ≈ 0.000005** describes only this frozen shuffle experiment. It does not correct for earlier population-wide searches for p951 source geometry, alternate printer producers, or recorder sampling rules. The comparison is a conditional evidence-strength calibration for source coupling, not an unconditional historical probability.

## Target significance and strict limit

If all four metadata-first matched 32-bit controls are inserted as additional native equations into the original source basis, the exact rank advances only **15,365→15,366 (+1)**, despite 113 individually source-fixed heldout bits. The four disputed selected printer native words at stage951..954 still contribute **128 independent unknown bits**, and no physically authentic printed coupon is obtained.

This selective local cross-carrier agreement strengthens the case for examining a shared original-generation process; it does **not** explain the incompatible rest of the purported full recorder writer or select a native-to-paper transfer. See Agent25's contemporary [printer DEST metadata signal and 47 source contradictions](h17-k04-printer-metadata-destination-mt-20261106.md) for an independent reminder that locally convincing metadata correlations can coexist with global emitter failure.

The read-only, source-hash-pinned [single-file SFT](../agents/agent16/k04_recorder_metadata_inverse_holdout_sft.py) reproduces the stage search, four heldout original-control validations and 200,000 shuffle results from the unchanged `resources/` original. There is no modified original source, candidate, acceptance, route, or checker. **K04 physical authenticated bits: 0/128; K08 final authenticated words: 0.**
