# H-17 K04: original-source V8 sum32 producer contradiction with seeded solver controls

**Agent18, 3 November 2026 (~09:01 UTC). Outcome: zero historically authenticated target bytes, new finite producer-family exclusion.**

## Hypothesis and why this is distinct

Original source file \`resources/evidence/print/spool-reconstruction.log\`, SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`, includes two fully intact early ordinary ACK printer packets for 07:00 and 07:05 UTC on 3 October 2026. The later 18:02 selected ESC-N ACK2 copied payload is **withheld**. Model a printer writer that constructs every 16-byte payload from **four consecutive 32-bit words** \`floor(2^32 * Math.random())\` under one V8-style 128-bit xorshift128+ state, with a fixed hidden extra-draw count between packets. Both big- and little-endian 32-bit serialization are considered.

The **current** [V8 RNG source](https://github.com/v8/v8/blob/main/src/base/utils/random-number-generator.h) returns \`(next_s0 + next_s1) mod 2^64\` before floating-point conversion. For these top32-bit samples, the exact output is \`(sum >> 32)\`. The [current math-random implementation](https://github.com/v8/v8/blob/main/src/numbers/math-random.cc) advances state in forward call order on 64-bit platforms. The packet writer assumption is unproven; the printer export never claims to have used JavaScript or V8.

Nearest prior art, **explicitly distinguished**: workplace-v1 Agent49 \`agents/agent49/k04_v8_state0_byte_serializer_sft.py\` previously tested an old **upper-byte of state0** model on same-job 18:01 and 18:03 REQUESTED packets. Workplace-v2 Agent7 [one-packet V8 quotient report](h17-k04-v8-retry-lowrank-quotient.md) enumerated 32,708 old-state0-derived K04 complete candidates and got no match; a modern *byte-output* V8 SMT pilot returned UNKNOWN. This experiment instead tests the **modern nonlinear sum of two state words** in a **32-bit word serializer** against **two source-original ordinary packets** and obtains exact UNSAT certificates. It does **not** resolve Agent7's byte-output timeout.

## Exact reproducible equations and evidence

Let state \`(a,b)\` be two 64-bit vectors. One call performs:

\`\`\`text
t = a XOR (a << 23)
t = t XOR (t >> 17)
t = t XOR b XOR (b >> 26)
(a,b) = (b,t)               [modulo 64-bit width]
word32 = ((a+b) mod 2^64) >> 32
\`\`\`

Read the original **entire 16-byte** 07:00 and 07:05 packet payloads as four words each. For \`gap=0..63\` hidden draws between packets and each byte order, existentially quantify both unknown original 64-bit state words and assert all eight observed 32-bit outputs exactly. Every proposal is a 128-unknown-bit QF_BV problem. Solve with Z3 **4.13.3.0**, original 128-bit record contents intact, source SHA pinned. A fixed gap of up to 63 is a concrete finite speculative schedule, not an asserted printer fact.

| Model scope | Checked | SAT | UNSAT | UNKNOWN |
| --- | ---: | ---: | ---: | ---: |
| Modern \`(a+b)\` sum32, gaps 0..63, both 32-bit byte orders | **128** | 0 | **128** | 0 |
| Planted real 128-bit seeded V8 sum32, gaps 0/3/7, seed fixed in solver | **3** | **3** | 0 | 0 |
| Independent first-bit flip of each planted second packet, same seed pinned | **3** | 0 | **3** | 0 |

The synthetic positive/negative controls are tests of formula correctness and source parsing, not historical evidence that this printer used V8. Original model queries all returned definitive \`unsat\` before the 1800ms per-query solver limit, and were executed for 0..7, 8..23, 24..39 and 40..63 in local batches. No missing K04 selected ACK bytes, original K04 acceptance hash or K08 caption were used as fit variables or tests. SFT: [\`agents/agent18/k04_v8_sum32_smt_sft.py\`](../agents/agent18/k04_v8_sum32_smt_sft.py), standard Python plus installed libz3, with original-source and seeded controls.

## Older V8 cache source model: incremental phase and serialization coverage

The historical [2018 V8 implementation](https://chromium.googlesource.com/v8/v8/+/4ff869ed3cab620e6cebb4af853ae0376f01e49f/src/math-random.cc) wrote 64 state0-derived doubles into a cache in forward generation order and returned them in reverse consumption order. A second source-only, exact GF(2) model tested both reverse-64 and direct call order; 8/16/32-bit top-of-state0 samples; both BE/LE 16/32-bit serializers; all 64 initial positions; and 0..3 fixed gap draws. That's **2,560 exact model assignments** using the same first two intact 16-byte printer packet source controls, with **zero consistent models**. Six independent genuine seeded synthetic state controls pass. Reproducer [\`agents/agent18/k04_v8_cached_state0_sft.py\`](../agents/agent18/k04_v8_cached_state0_sft.py). This is a broader **original ordinary-packet model parameterization**, not an entirely new underlying RNG family beyond v1 Agent49/v2 Agent7.

## Implications and limitations

These falsifiers rule out the explicitly tested **shared-state V8 word and historical state0 serializers** under the specified schedule and first-two-packet source mapping. They do not falsify independently reseeded packets, arbitrary per-record gaps, other V8 byte/range sampling and rejection, separate precomputed pools, corrected physical media not represented in this source, or all pseudorandom generators. In particular, a failed source emitter model recovers no selected original K04 coupon bits and supplies no final K08 words. No original archive, source, acceptance, canonical candidate, or verifier was modified.

The official state remains **six individually accepted slots; K04/K08 missing; combined INCOMPLETE**. Use this report to avoid retesting V8 32-bit sum fixed-gap source hypotheses. Future work should prioritize an independently witnessed source-to-selected-event or author-final caption relation with an actual complete-candidate construction, as recommended in [the 08:03 Critic source-causality pivot](../communications/broadcast/20261103T0803Z_Critic_source-causality-and-target-selection-pivot.md).
