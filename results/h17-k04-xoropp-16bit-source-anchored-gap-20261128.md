# K04 — exact xoroshiro128++ erased-retry recovery with a 16-bit sum-state witness (28 November 2026)

**Agent 48 — mathematical reconstruction available; original K04 not recovered.** The surviving original PS-261003-0417 REQUESTED attempt-1 and REQUESTED attempt-3 packets are treated as *hypothetical* outer blocks from one xoroshiro128++ 1.0 stream, with the selected attempt-2 payload omitted from inference. Their presence and chronology do not establish that the printer actually used this PRNG or emitted consecutive 64-bit draws.

## Complete-output recovery mechanism

For a state `(a,b)` of two 64-bit words, xoroshiro128++ 1.0 emits

`y = ROTL64(a+b,17)+a`,

then updates `t=a XOR b; a'=ROTL64(a,49) XOR t XOR (t<<21); b'=ROTL64(t,28)`. All additions and shifts are in unsigned 64-bit semantics. Assume an **independently known 16-bit segment** of the initial sum `c=a+b`, either low16 or high16. From the intact first output `y0` the full initial state is parameterized exactly by just one unknown 64-bit sum:

`a=y0-ROTL64(c,17); b=c-a`.

One QF_BV solve fixes the given 16-bit `c` segment and asserts the other intact outer outputs `y1,y4,y5`. A satisfying state forward-generates the **entire** withheld 128-bit middle `(y2,y3)`, not just a parity or guessed source byte. For a historical model, serialize these two words in the same packet orientation and apply the unchanged official K04 route XOR mask, checking the *whole* component against the unchanged official SHA-256 commitment.

[Source-free exact inverter and positive controls](../agents/agent48/k04_xoropp_sum16_gap_erasure_synthetic.py). Nine planted erased-middle cases recovered **both missing words and the exact planted initial state**: six independently seeded low16 anchors and three high16 anchors. Three deliberately incorrect low16 anchors returned definite UNSAT. A separate local two-output first-packet inverse (without any later flank) recovered both planted sum-anchored states at low/high16 and refuted both one-bit-wrong anchors. These checks validate the *conditional mathematical inverter*, not its historical source model.

As a solver-informativeness control on one planted erased-middle six-output stream, low4 and low8 initial sum bits both timed out at 120 s, low10 solved at 108.3 s, low12 at 59.9 s, and low16 within seconds. These are narrow runtime observations, not a universal minimum source-entropy theorem; an unanchored SMT attempt also remained UNKNOWN at 120 s. A separate previously published 82-primary-Boolean solver had demonstrated an unanchored *planted* inversion, but historical source models remained inconclusive; this result does not supersede it.

## Untouched historical acceptance check

The source-side witness hypothesis was deliberately narrow and finite: the original committed AX-7782 attempt-2 audit has eight two-byte checkpoints. Treat each checkpoint as a **hypothetical** low16 or high16 of the printer's initial sum state, and test both checkpoint byte interpretations, both packet 64-bit word endiannesses, both packet word orders, and both sum-bit locations. There are exactly `8 * 2 * 2 * 2 * 2 = 128` cases. The full 16-byte candidate and original K04 commitment are examined **only if** a case is SAT. The disputed ACK2 copied bytes are not imported.

At 7,000 ms per case, the 128 original-source cases gave **0 SAT, 84 UNSAT, 44 UNKNOWN** and **no K04 candidate**. The UNKNOWN cases are unresolved, not source-independent contradictions. The original spool, committed transfer audit, routing sheet and acceptance bytes are SHA-256 pinned by the [redacted source-side reproducer](../agents/agent48/k04_xoropp_sum16_checkpoint_source_screen.py); it prints only aggregate solver statuses and a Boolean historical commitment result. It neither logs source payloads nor recovered bytes. No source-bearing CI was run.

A second exploratory *local-only* trial tied the 16-bit state field to the **same-job serial 0417**, using decimal 417 or the literal-digit hex reading 0x0417, both initial-sum and initial-XOR interpretations, low/high16 placement and four original packet word views. Across 32 models: **0 SAT, 11 UNSAT, 21 UNKNOWN** at 7 s; zero complete K04 candidates. These interpretations are conjectural, not documented printer seed rules; this does not exclude other initial-state values or other generator families.

## Acceptance consequence and decision

**No original K04 component was recovered.** No model in the tested source checkpoint or job-ID domains survived to construct a complete coupon, and the physical copied ACK2 remains unauthenticated. Six original REC8/1 slots remain accepted; K04 and K08 remain unresolved and combined acceptance incomplete.

The genuinely reusable increment is **exact prediction of both erased 64-bit words from just one authentic 16-bit sum-state witness plus the intact flanks**. The next target-reaching step would be either a source-authenticated printer state/checkpoint link (rather than an arbitrary cross-archive 16-bit match), or a better truly unanchored inversion from the original producer. Do not extrapolate the bounded source-model negatives to all xoroshiro streams, and do not substitute these synthetic successes for historical recovery. No quarantined PDF was opened and no original source, verifier, commitment, or canonical candidate was changed.
