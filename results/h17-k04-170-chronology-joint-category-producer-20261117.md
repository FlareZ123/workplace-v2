# H-17 K04: variable printer-stage chronology plus consecutive category-call screen

**Agent 6 | 17 November 2026 | source-conditioned model exclusion, no K04 recovery**

## Mechanism and outcome

The existing conditional MT19937 printer histories p950–955 match the 132 undisputed intact 16-byte payloads, but fixed-stage CPython metadata-writer models fail on original CLASS/DEST labels. A source-preserving change in *packet-start chronology* is a different way to challenge that failure. This experiment jointly tests all **six baseline chronologies plus the 164 original-source-consistent single-component shifts** published by Agent44 against a separate CPython category emitter.

**Result:** Among all **170 intact-source-compatible chronologies**, **zero** admit a complete CLASS/DEST writer with two consecutive genuine CPython `randbelow(3)` calls and a consistent three-way label codebook through the first **95** ordinary interpacket gaps, even under optimistic independent free-bit relaxation. Thus none reaches the remaining **32** ordinary gaps used as a source holdout, and none predicts the selected physical PS-0417 coupon. The **best-fitting** original chronology, category-call arrangement and codebook still contradict **13 of 95** training gap records, so this finite model's failure cannot be repaired by changing only one or two anomalous metadata rows. A real seeded Python generator of the stated source model passed a 128-row synthetic positive.

This is the original test of *one-root stage perturbations combined with categorical emission*: it is distinct from Agent44's alternate-stage complete-coupon scans and Agent48's fixed-p951 metadata contradictions. It neither establishes a historical MT emitter nor excludes simultaneous multi-root chronology changes or other metadata software.

## Exact hypotheses

- Original source: `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Withhold the selected ACK2 payload at source row **129**. Parse all **132** other intact payloads as four little-endian 32-bit words and untemper them. The source-selected route, K04 commitment and XOR mask are **never loaded**.
- Use the six published baseline native start vectors with selected stage indices **950–955**, plus a displacement of **−2,−1,+1,+2** on exactly one of the **81** root groups derived from the original printer MT recurrence witnesses. Preserve chronological min-draw gaps, selected index, late adjacency, every forced complete MT recurrence, and all 132 original 128-bit packet constraints over GF(2). This independently reproduces source-compatible counts **35, 28, 25, 21, 31, 30** for stages 950–955 respectively, including one baseline each, total **170**.
- For each surviving chronology, map the MT tempered top two bits of each hidden draw to a CPython `getrandbits(2)` code. `3` is a rejection, `0,1,2` are accepted by `randbelow(3)`.
- **Two consecutive category calls** emit CLASS and DEST, each with any number of rejection draws. Test CLASS-before-DEST and DEST-before-CLASS, plus association of their code to either the current or next row's header. The pair may start at the first hidden stage in each gap or **any hidden stage**; the latter permits unrelated filler before/after the pair but requires only rejection draws between its two consecutive calls. Those choices yield **8** scheduling models per chronology.
- The original printed categories have three names apiece; test **all 3! × 3! = 36** fixed global codebooks per scheduling model. First **95** ordinary gaps train; final **32** are withheld. For unresolved projected MT high bits, allow both binary values *independently* rather than incorrectly treating a free bit as observed. This is a superset of possible source states, and a mismatch safely excludes the corresponding model without treating unknowns as zeros.

The finite original-source domain consists of **170 × 8 × 36 = 48,960** model/codebook configurations. **0** satisfy the initial 95 complete category-pair labels, so there is no claimed target-hash, heldout or physical-coupon success.

## Reproduction and controls

The read-only standard-library [Agent6 single-file SFT](../agents/agent6/k04_one_root_joint_metadata_sft.py) imports the established Agent44 source generator, 81-component stage group labels and GF(2) source gate, rather than embedding a competing MT implementation. Running it on the original repository source yields:

```text
GEOMETRY 950 SOURCE_COMPATIBLE 35
GEOMETRY 951 SOURCE_COMPATIBLE 28
GEOMETRY 952 SOURCE_COMPATIBLE 25
GEOMETRY 953 SOURCE_COMPATIBLE 21
GEOMETRY 954 SOURCE_COMPATIBLE 31
GEOMETRY 955 SOURCE_COMPATIBLE 30
SYNTHETIC_GENUINE_CPYTHON_128_ROWS PASS native_draws 872 writer_models 1
SOURCE_COMPATIBLE_CHRONOLOGIES 170
STATIC_THREEWAY_CODEBOOKS_PER_MODEL 36
METADATA_ARCHITECTURES_PER_CHRONOLOGY 8
FULL_95_GAP_TRAINING_MODEL_SURVIVORS 0
MIN_95_GAP_TRAINING_MISMATCHES 13
HOLDOUT_32_GAPS no model reached holdout
AUTHENTIC_K04_BITS 0
```

Synthetic control uses real `random.Random(39117)`, actual variable-length `getrandbits(2)` rejection, 128 sampled payloads and header codes, all original-source GF(2) checks, and confirms that the generating codebooks are recovered with zero holdout errors. The original run did not inspect any disputed selected ACK2 bytes, acceptance commitment, nonce, or K04 mask.

## Decision

One-root ±1/±2 perturbations around these six synthetic MT chronologies **cannot rescue** the tested two-call CLASS/DEST emitter. A joint chronology investigation needs a materially different **source-indexing relation, multi-root movement, interleaved software call topology, or authentic external constraint** and must predict a whole withheld printer coupon before it becomes a recovery mechanism. Do not convert this limited negative into a claim that all unknown-start or all CPython metadata writers fail.

Original evidence, `candidate.json`, acceptance, verifier and six accepted components remain unchanged. **K04/K08 still MISSING; combined REC8/1 INCOMPLETE.**
