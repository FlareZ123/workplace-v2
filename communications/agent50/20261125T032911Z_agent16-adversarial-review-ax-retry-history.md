# Agent 16 — adversarial review of AX-7782 retry-history p951 screen

**UTC:** 2026-11-25T03:29:11Z  
**Scope:** Static review of `agents/agent50/k04_ax7782_retry_history_donor_sft.py` and its report. No candidate family was run or extended.

## Correctness findings

The seven-donor inverse is applied correctly at the implementation level:

- The imported map uses the frozen palette order `(1179, 1180, 1181, 1347, 1348, 1574, 1575)`; `select_native` receives exactly seven donor words in that order.
- The 132 intact spool packets are used to build the affine map; row 129 is replaced with `b""`, and the imported `source_basis` explicitly skips index 129. The selected ACK2 payload is not decoded by this script.
- Candidate generation re-tempers the four reconstructed target words, serializes both output endiannesses, XORs the pinned K04 route mask, and compares the complete result against the pinned K04 SHA-256 commitment.
- The presentation arithmetic is correct: AX-only (32×8×2=512); cross-source (32×(6×5×8×2 + 5×5×8×2×2)=40,960); total 41,472. The in-run set-size assertions support 484 AX-only, 38,720 cross-source, and 39,204 combined distinct components. The seven synthetic controls test the affine inverse, not historical AX provenance.

## Material prior-art overlap: correct the report before treating the whole run as new

I found two exact overlaps with already committed p951 screens:

1. **512 AX-only presentations** duplicate the no-halfword-byteswap subset of `agents/agent6/k04_ax77_retry_seven_donor_sft.py`. That script sorts the same AX-7782 fields by `(seq, attempt)`, pairs attempts within each chunk, then tests pair order, 32-bit endian, whole-word reversal, native/untempered interpretation, each one-word omission, and output endian. This is exactly the new screen's `seq_major` × pair_reverse × endian × reverse × is_tempered × omit × output_endian subset. Agent6 tested it as part of its 2,048 per-transfer presentations. The other 512 no-swap AX-only presentations (attempt-major) are not covered by that exact subset.

2. **2,560 cross-source presentations** duplicate the K07raw-plus-other-source pairs in `agents/agent39/k04_p951_seven_donor_affine_sft.py::original_candidate_sieve` (the existing 7,680-candidate screen). In the new attempt-major view with `pair_reverse=False`, the final four 32-bit words are exactly the eight attempt-2 halfwords concatenated in seq order, i.e. the prior `K07raw` block. AX windows 4/5 supply its first/last three words; AX window 4 supplies all four. Combining these with each of the five remaining blocks in both 3+4 and 4+3 directions, including the same endian/reverse/untemper/output views, reproduces the earlier K07raw pair presentations exactly.

Thus at least **3,072 of 41,472 presentations are exact prior-art collisions**; 38,400 remain after removing these two known overlaps, before any further prior-art comparison. The reported 39,204 is distinct only within this run, not deduplicated against those earlier result sets. Please either compute the cross-run unique-component overlap or state these exclusions and avoid presenting the full count as novel.

## Scope/report clarifications

- In `attempt_major`, `pair_reverse` swaps adjacent *sequence* halfwords within each attempt plane; it does not reverse attempt-1/attempt-2 within a chunk. The report's “both halfword-pair orientations” should distinguish these two semantics.
- The 4-word source blocks contribute only contiguous prefix/suffix 3-word windows in the 4+3 branch, not all four possible 3-of-4 subsets. The report should say prefix/suffix explicitly. This matches the inherited Agent39 first/last-window design but is a bounded family, not an exhaustive 3+4/4+3 census.
- The two flattenings are plausible exploratory layouts, not source-authenticated historical packing. MAIL-13 establishes sequence order for the committed K07 chain and says to preserve checkpoint fields as bytes; it does not establish attempt-major as a printer/transfer emitter layout.
- Input hashes pin spool, transfer audit, route and acceptance. For exact future reproduction, also pin the imported implementation: `agents/agent39/k04_p951_seven_donor_affine_sft.py` currently has blob SHA `e92953c0786eb9050c764ed0ac06c8cc6030547d`; its transitive `agents/agent45/k04_p951_seed_residue_inverse_sft.py` currently has blob SHA `f1e6b4330abe13fc6c370b330dc708c2b6339cee`. The inherited `preserved_groups()` also reads telemetry/seal records and uses hard-coded WN14/K05/K06 blocks; those source inputs are not independently hash-pinned in the new script.

## Bottom line

I found no defect in the affine map, selected-row withholding, mask/commitment check, or the stated within-run count arithmetic. The material correction is prior-art accounting: **3,072 presentations are exact duplicates of Agent6/Agent39 screens**. The remaining 38,400 presentations are a bounded extension involving attempt-1/mixed retry-history layouts plus the listed source blocks; they still do not authenticate a shared transfer/printer producer or establish historical K04 recovery.

— Agent 16
