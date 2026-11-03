# K04: pre-ACK printer-cohort checksum escrow alternative

**Agent 2, 3 November 2026. 8,569,470 complete original K04 candidates, zero acceptance matches.** Six previous individual components remain PASS; K04 and K08 remain MISSING and combined acceptance remains INCOMPLETE.

## Alternate original-producing mechanism

Instead of interpreting the selected 18:02 spool as an independently generated random coupon, hypothesize that an ESC-N escrow job carried a **derived aggregate** of earlier intact printer packets, as might happen with a parity or accounting checksum. This interpretation is not stated in the H-17 record. The source does attest timestamps, job identity, CLASS and DEST for 129 recorded printer rows preceding the selected 18:02 ACK2.

A source-controlled finite model exhaustively considers all **8,385 contiguous intervals** from those 129 pre-ACK records. Each interval's rows are partitioned into the nine observed CLASS × DEST categories (LABEL/STORES/RECOVER × bench/desk/store). For each of the **511 nonempty group-subset selectors**, compute either (a) 128-bit bitwise XOR of every included packet or (b) the sum of all included 128-bit packets modulo 2^128, preserving original byte order. XOR the resulting 16-byte hypothetical escrow coupon with the untouched K04 route mask, and SHA256-compare the complete resulting 16-byte component to the original unchanged commitment. This gives exactly `8,385 × 511 × 2 = 8,569,470` candidate assignments. Many selectors collapse when some categories are absent, so these are assignment counts, not guaranteed distinct components.

This is mathematically distinct from [our four-same-job additive retry-word producer](h17-k04-retry-additive-word-producer-sieve.md) and from [Agent23's source-only GF(2)/GF(256) packet-rank diagnosis](../agents/agent23/k04_source_packet_affine_parity_rank_sft.py). It directly tests full original K04 candidates under a different **aggregate-escrow producer** instead of fitting unspecified random states.

## Original-source result

- Printer file SHA-256 pinned to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The missing 18:02 selected ACK row is deliberately excluded from all source aggregates. Rows after the selected event are also excluded to preserve causal time ordering.
- All 9 metadata categories, 129 inputs and 8,385 contiguous windows are asserted.
- Original K04 commitment matches: **zero**, across 8,569,470 assignments. Local Python standard-library run took **5.63 s** on this runtime.
- Synthetic positive control: an externally specified pre-ACK interval [3,41] and category bits {1,4,6} produces a planted SHA256 target. Full enumeration recovers that **exact** interval/selector/operation once. The same planted digest occurs 80 times over differing assignments due to identical aggregate outputs in windows with excluded-category rows.

The [portable read-only SFT](../agents/agent2/k04_escrow_cohort_aggregate_sft.py) reproduces this test from the original `resources/` directory. Neither original evidence, acceptance inventory, candidate nor checker was modified.

**Interpretation:** These results exclude the defined two aggregate functions with a uniform source interval and shared category selector. The original documents supply no proof of checksum-based escrow, and independent category-specific transforms, hidden keys, future source inputs, alternate print buffering or real paper coupon content remain outside the model. No authentic selected K04 bit was established, and K08 final words remain unknown. Avoid scaling arbitrary cohorts without an original producer cue.
