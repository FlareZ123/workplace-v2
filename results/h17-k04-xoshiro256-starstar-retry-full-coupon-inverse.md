# K04: invert xoshiro256** retry-flank outputs to reconstruct full missing-middle coupons

**Agent 16 | 3 November 2026.** A new exact, target-reaching complete-coupon producer hypothesis, tested with the original 18:01 and 18:03 REQUESTED packets. **No historical K04 recovery**.

## Source-selected test, and distinction from earlier xorshift family

Original print spool, SHA256 **7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083**, contains the same ESC-N logical job **PS-261003-0417** at:

- **18:01 UTC, attempt1 REQUESTED**: CD3E4F216ADB2FB180DA2AA90B33F7A4.
- **18:02 UTC, attempt2 ACK**: original retained payload has **unverified integrity**, so it is completely withheld from this experiment.
- **18:03 UTC, attempt3 REQUESTED**: 44D53DFC29D7943A95D89371DA58EC64.

The two REQUESTED fields are real surviving original-source strings. Their correctness as original *generated* payloads is also unverified, and their reported state does not prove physical printing. MAIL-16 does establish which attempt received the ACK.

Previous [Agent24 xorshift128+ missing-middle inversions](h17-k04-xorshift128plus-middle-attempt-full-inverse.md) treated a distinct 128-bit generator with upper/lower 32-bit truncation and found UNSAT on the original two flanks. This new test instead uses the standard **xoshiro256** (star-star)** 256-bit fourword state with its two 64-bit outputs per 16-byte printer packet. This is a substantively different family with a particularly useful *fully reversible* output function.

## Why this mechanism can crack a complete coupon

For xoshiro256**, the emitted 64-bit word is:

    output = rotl(state[1] * 5, 7) * 9 mod 2^64

Because 5 and 9 are odd, both have inverses modulo 2^64. Reverse their multiplications and rotation to obtain the **entire 64-bit state[1]** at each observed output step. The xoshiro256** state transition is linear over GF(2). Four observed 64-bit outputs, interpreted as two each from attempts1/3, therefore yield a **256-equation system on 256 initial state bits**.

The original bracket may be separated by other unobserved draws, so freeze a bounded source model:

- Attempt1 uses output steps **0 and 1**.
- Attempt3 uses output steps **L and L+1**, for **L=4..64**.
- Missing selected attempt2 uses any two consecutive outputs **j and j+1**, **j=2..L-2**.
- Test little- and big-endian 64-bit serialization and normal/reversed 64-bit lane order.
- For each GF(2)-consistent placement, enumerate **all** free initial-state bits when rank is 254, 255 or 256, regenerate the complete missing 16-byte packet, XOR the **unchanged** original K04 mask, and apply the **unchanged** original 256-bit slot SHA256 commitment.

This directly reconstructs a *whole* missing-middle coupon from independent flanking observations if the hypothetical producer and packet chronology are correct. The source-flank fit excludes the copied selected ACK2 bytes, mask, and target commitment. The commitment is used only to test completed coupons.

## Original read-only execution

| Quantity | Result |
| --- | ---: |
| Candidate output spacing L | 61 |
| Endian/lane serializations per spacing | 4 |
| Source-grounded flank geometries | **244** |
| GF(2)-consistent bracket geometries | **143** |
| Total complete compatible initial-state assignments | **248** |
| Selected-middle output positions and state assignments tested | **7,454** |
| Distinct full 128-bit coupons | **7,454** |
| Original full SHA256 K04 commitment matches | **0** |

All four 64-bit original outputs were explicitly reconstructed and asserted against their source values for every compatible generator state. The 244 GF(2) systems had rank254 in 40 cases, rank255 in 140 cases and rank256 in 64 cases. Rank deficiency was **fully enumerated** rather than silently choosing one state or pretending a 255-rank system is unique. The 143 consistent geometries cover all 248 actual solutions, and the 7,454 finished coupons are globally distinct.

No xoshiro256** candidate in the stated producer/spacing/serialization family recovers K04.

## Actual seeded generator controls

The [portable source-pinned SFT](../agents/agent16/k04_xoshiro256_retries_sft.py) is a read-only standard-library Python file. It uses four planted genuine 64-bit state words and the actual xoshiro256** recurrence, creates two intact source flanks, then deliberately hides the selected-middle pair before running the same GF(2) state inversion. It recovers the **entire true generator state** and exact two-output missing coupon for selected starts 2, 3, 13, 17 and 30 under 4 packet orientations, **20/20 planted end-to-end positives**. The original test and synthetic controls run with the same inversion routines.

Reproduce from repo root:

    python agents/agent16/k04_xoshiro256_retries_sft.py

## Limits and next target-bearing evidence

The original archive never certifies xoshiro256** as the printer generator. Its ordinary packets exhibit separate speculative MT19937 correlations, and dispatch REQUESTED does not certify media contents or a shared sequential PRNG. If the true producer uses xoshiro256++ / xoshiro256+ / a different 32-bit extraction, is reseeded per job, skips more than the frozen 64 output window, or if either flank was copied incorrectly, this exclusion does not cover it. Broadening an unauthenticated emitter list without an independent held-out original generator fingerprint would have low value.

**No original selected coupon bit is authenticated.** Exactly six original slots remain PASS, K04 and K08 remain MISSING, combined REC8/1 INCOMPLETE. The strongest next step is a trustworthy independently indexed original emitter/capture witness for 18:02 or the exact original Emily keeper-final text.
