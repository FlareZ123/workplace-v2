# K04: one-packet V8 state quotient with a variable retry window

**Agent 7 | 3 November 2026 | Complete target-reaching test of one hypothetical producer, no original match.**

## Source and question

Original spool SHA-256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Exact job PS-261003-0417 RECOVER attempts:

- 18:01:00Z REQUESTED attempt 1: CD3E4F216ADB2FB180DA2AA90B33F7A4
- 18:02:00Z ACK attempt 2: disputed physical/copy payload, **excluded from producer inference and candidate generation**
- 18:03:00Z REQUESTED attempt 3: 44D53DFC29D7943A95D89371DA58EC64

Unlike workplace-v1 Agent49's fixed-gap paired-buffer V8 pilot (agents/agent49/k04_v8_state0_byte_serializer_sft.py), this test inverts the first packet **alone**, enumerates its entire remaining state quotient, predicts full attempted-second-packet candidates over a variable-gap window, and independently tests attempt 3.

## Conditional producer and original-source outcome

Hypothesize 16 opaque packet bytes from the **historical V8 state0 upper-byte** xorshift128 output, in native forward or 64-value reverse-cache order. The output is state0 >> 56 after each xorshift128 transition, the older V8 state0 extraction path. It is not established that the print subsystem actually used V8. Modern V8 uses a different sum-based output path, **not excluded here**. See [V8's historical blog](https://v8.dev/blog/math-random) and [current V8 source](https://github.com/v8/v8/blob/main/src/base/utils/random-number-generator.h).

Each observed upper byte is GF(2)-linear in the initial 128-bit state. Inverting all 16 bytes of attempt 1 yields:

| Hypothetical serializer | First source packet | State quotient | Follow-up |
| --- | --- | --- | --- |
| Direct high byte | Consistent rank 126 | Exactly 4 full states | All 16-byte windows beginning at offsets 16..8192; **32,708** complete K04 assignments |
| Reverse-64 cache | Original first packet inconsistent after rank 116 | No consistent state | No target values justified |

For direct mode, each predicted packet is XORed with the **original** route mask. Its 16-byte component is checked against the **untouched** K04 SHA256 commitment 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0. All **32,708** assignments yield **NO_MATCH**. Independently, none of the four states reproduces the preserved attempt-3 full 16-byte buffer at any offset 16..16384.

Six synthetic initial-state controls (three each for both serializers) are recovered from their own generated 16-byte first packets: all have rank 126 and include the true seed among the four completions. Source SHA and official route/commitments are read, not modified.

Reproducer: [Agent7's source-pinned Python standard-library SFT](../agents/agent7/k04_v8_retry_lowrank_sft.py). It reads original REQUESTED attempt 1 and 3, withholds the disputed selected ACK2, and writes no source.

## Scope and next hypothesis

This resolves the one-packet initial-state ambiguity for an old V8 output mapping and tests every complete prospective component in the defined window. The original heldout attempt-3 failure weakens a common-stream account across all tested positions. Both REQUESTED buffers are retained fragments with no independently authenticated payload integrity. This mathematical producer hypothesis does **not** establish historical use, certify selected bytes, or recover a seventh component.

Different output transformations, separately seeded event state, or different printer transfer stages remain open. A separate modern sum-of-two-states V8 byte-output SMT pilot returned UNKNOWN after 15-second timeouts even for a planted control, so it is **inconclusive** and must not be treated as a negative certificate.

REC8 remains six individually accepted components, K04 and K08 unresolved, combined INCOMPLETE.
