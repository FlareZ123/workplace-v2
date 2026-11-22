# K04: exact xoroshiro128+ two-64-bit-output source inversion and original full-coupon exclusion

**Agent 8 | 22 November 2026 | Original K04: 0/524,270 whole-coupon checks.** K04/K08 remain missing and combined REC8/1 incomplete; six historical accepted slots unchanged.

## New, distinct target-reaching mechanism

Unlike the 22 November xoshiro128+ model, xoroshiro128+ emits **one 64-bit modulo-sum output** from a two-word 128-bit generator state. Both published 128-bit xoroshiro128+ state transitions have the same output `(s0+s1) mod 2^64` and differ in their exact XOR/rotate schedules: **(55,14,36)** (2016) and **(24,16,37)** (2018). The original source does not say its printer used either generator. This bounded speculative producer is distinct from the earlier ordinary-spool **low-bit** exclusion ([prior art](h17-k04-xoroshiro128plus-metadata-lowbit-exclusion-20261105.md)), which did not invert a complete incident-date REQUESTED source anchor to generate actual K04 candidates.

The original source contains two **complete** 16-byte unacknowledged PS-261003-0417 / ESC-N RECOVER request packets, at 18:01Z attempt1 and 18:03Z attempt3. The disputed 18:02Z attempt2 copied ACK is **withheld entirely** from modeling; its dispatch ACK and copied payload do not authenticate media. Interpret each REQUESTED packet as two consecutive native 64-bit generator outputs, under either 64-bit byte order and either word order. This defines **16 exact original source-view tests**: two recurrence schedules × two request anchors × four serializers.

Given the first 64-bit source output `y0`, eliminate one unknown state word: `s1 = y0 − s0 (mod 2^64)`. Z3 then solves one remaining 64-bit unknown against the **entire second 64-bit output** using the exact source recurrence. Block each successful complete initial state, enumerate until UNSAT, and reconstruct **whole 16-byte** future packets for REQUESTED1 or previous packets for REQUESTED3, using the algebraically exact inverse state update. Compare the opposite independent REQUESTED packet as a whole-source holdout. For each possible whole selected coupon, XOR the original routing mask `8556C8CB6140A7F9A5123AC7571BEE1C` and compare the SHA256 of the **entire resulting component** to the unchanged original K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The historical source's output gap and producer link are assumptions, not facts.

## Original test, including complete 0-gap-adjacent selected windows

| Source transition | Original source views | Full-state source preimages | Full 16-byte candidate checks | K04 original matches | Opposite complete REQUESTED packet matches |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2016 (55,14,36) | 8 | 5 | **327,667** | **0** | **0** |
| 2018 (24,16,37) | 8 | 3 | **196,603** | **0** | **0** |
| **Total** | **16** | **8** | **524,270** | **0** | **0** |

All 16 exact source-view inversions **terminated UNSAT after all full state models were enumerated**; no capped or UNKNOWN source view. From each source state, enumerate 65,536 native 64-bit output positions. REQUESTED1 forward checks complete candidate two-word windows at positions2..65534 (**65,533** per state); REQUESTED3 backward checks positions0..65534 (**65,535** per state), including the immediate preceding two-output packet. Unlike an arbitrary fixed separation, this directly includes a zero-intervening-word coupon between the two preserved attempts.

Original detailed source-state distribution:

- 2016: REQUESTED1 little/normal **1**, little/reversed **3**, both big views **0**; REQUESTED3 big/normal **1**, remaining three views **0**.
- 2018: REQUESTED1 big/normal **1**, other three **0**; REQUESTED3 little/normal **1**, big/normal **1**, other two **0**.

The actual source is SHA256-pinned printer spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; the original route, acceptance commitments, candidate file and verifier remain unchanged. Counts represent **complete assignments**, not a globally deduplicated coupon set.

## Calibrated positive controls and consequence

For both official transition variants, 1,000 genuine forward/backward state inversions preserve all 128 internal bits. Independent planted two-output source packets recover the true internal seed from **all** complete Z3 preimages; inversion terminates UNSAT, with **four** state preimages in 2016 and **two** in 2018. The native-stream synthetic producer recovers a separate full 16-byte future packet byte-for-byte under the same forward replay. These are mathematical and computational controls; no true physical ESC-N media were recovered.

Read-only [source-pinned single-file SFT](../agents/agent8/k04_xoroshiro128plus_summed_twoanchor_sft.py) implements the state inverse, the 16 historical source views, whole original SHA checks and independent holdout. The live unmodified K04 commitment rejected every modeled whole candidate.

**Decision:** Neither published xoroshiro128+ source model within the tested serializer/gap windows yields the missing K04. The intact opposite request is also never reproduced in the specified window, weakening their same-stream premise. This does **not** exclude other generator families, independently seeded attempts, corrupted original REQUESTED data or the missing native physical ESC-N coupon. The recovered key remains **6/8 individually PASS, combined INCOMPLETE**.
