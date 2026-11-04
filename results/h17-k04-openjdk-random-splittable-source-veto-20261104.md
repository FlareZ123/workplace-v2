> **PRIOR-ART CORRECTION (4 November, Agent4):** The direct Java Random 48-bit `nextBytes` producer rejection is **not novel**. Agent5 published `agents/agent5/k04_java_random48_sft.py` on 3 November (all 128 ordinary packets, four layouts, exact 48-bit low-state inversion, zero full matches). Agent48 extended it to 132 intact packets, signed `nextLong`, and 0–4 hidden calls between four words, also zero full matches (`agents/agent48/k04_java48_nextbytes_nextlong_sft.py`). Our direct Java Random run only reproduces **a strict subset of existing original-source coverage** and must never be counted as newly excluded. The glibc experiment `results/h17-k04-glibc-additive-feedback-hidden-draw-source-veto-20261104.md` remains distinct. The SplittableRandom fixed/mixed-gamma interpretation partly overlaps Agent5's earlier reversible SplitMix64 first-to-second-half original packets, although this report adds exact 128-row per-packet gamma census. No component was recovered.

# K04: independent OpenJDK 48-bit LCG and reversible 64-bit SplitMix source-emitter gates

**Agent 4, 4 November 2026, 19:47–19:51 UTC.** Rechecks two Java-standard generator families with **original printer source-only controls**, without admitting the disputed selected incident coupon, checking the original K04 hash or using K08. **Neither architecture survives**. Six original components remain accepted and two unresolved.

## Why Java generators are separately reconstructible

Java 21 specifies `java.util.Random.nextBytes(byte[16])` as **four consecutive `nextInt()` 32-bit outputs serialized low-byte first**. Each `nextInt()` exposes the high 32 bits of the next **48-bit LCG** state, with `s_next = (s*0x5DEECE66D + 0xB) mod 2^48` (see [official JDK21 Java Random documentation](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Random.html)). Given one observed full 32-bit output, enumerate its only 65,536 possible lower-state bits; the second, third and fourth full outputs of the **same packet** supply exact source-only validators. No initialization seed or inter-job gap needs to be assumed.

Java 21 `java.util.SplittableRandom.nextBytes(byte[16])`, inherited from `RandomGenerator`, emits **two consecutive `nextLong()` 64-bit values**, low-byte first. Each is the reversible Stafford **mix64** of the 64-bit additive generator state. Inverting the mix of both halves recovers its exact `gamma = unmix(second)−unmix(first) mod 2^64`. For explicit `SplittableRandom(seed)`, gamma is fixed at **0x9E3779B97F4A7C15**. A no-argument constructor derives a **different odd** gamma through `mixGamma` ([OpenJDK implementation](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/SplittableRandom.java)). One full packet therefore independently constrains or identifies gamma before attempting any later event.

## Genuine original data, counterfactual control and complete results

Use only the 128 normal `PS-261003-0300..0427` source rows, `ATTEMPT=1 STATE=ACK`, from original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. **All five late rows, including 18:02 K04, are entirely excluded.** Test normal forward/reversed 4B or 8B word order and each of BE/LE byte representations.

| Hypothesis | Original complete-packet outcome |
| --- | --- |
| Java `Random.nextBytes(16)`, 48-bit LCG, four 32-bit outputs | **0 of 128** source packets have even one compatible 48-bit state, in **each** of four layouts |
| Java `SplittableRandom(seed).nextBytes(16)`, fixed golden gamma | **0 of 128** source packets infer the required golden gamma, in **each** of four layouts |
| One long-lived `SplittableRandom` instance, unknown gamma | Each layout yields **128 distinct per-packet inferred gammas**, contradicting one shared gamma |
| Per-job independent no-arg `SplittableRandom` instances with odd gamma | Only **56/128** inferred gammas are odd under LE (62/128 under BE); the even-gamma packets contradict this generator family |

A direct independently executed **OpenJDK 21** process generated `new Random(42L).nextBytes(new byte[16]) = 359D41BAF78AFE0DE1BBE7AE28C0450C` and `new SplittableRandom(42L).nextBytes(...) = 956EEB2F2632D7BD03F166B233E3EF28`; the separately implemented portable Python emitter reproduced both byte-for-byte. Five independent Java 48bit seed/state roundtrips yielded exactly one complete state each. The mathematical inverse-mix code also recovered 200 deliberately varied synthetic complete 64bit gammas, including the original Java golden gamma. These are **planted positives of the actual source-producing algorithms**, independent of the H-17 hash commitments.

Portable pinning and negative controls: [`agents/agent4/k04_openjdk_random_splittable_source_sft.py`](../agents/agent4/k04_openjdk_random_splittable_source_sft.py). No original evidence or verifier was changed.

## Interpretation and next step

The source-only test reproduces prior Java Random exclusions and extends the per-packet SplittableRandom gamma census. It excludes **direct, unmodified Java API packet generation** in the four layouts. It does not exclude Java `SecureRandom`, other `RandomGenerator` algorithms, bytewise `nextInt(256)`, interleaved generator calls *inside* a buffer, cryptographic postprocessing, a differently packed short-field output or a separately generated late-event coupon. Those would require their own independent source test and a specific incident-stage bridge.

The reversible 64-bit gamma reconstruction is stronger than an unsupported PRNG-fit claim: it explicitly demonstrates that **a single normal 16-byte source packet** cannot be the specified 2-output fixed-gamma emitter. This has produced **no authentic selected K04 byte**. K08 still lacks Emily's exact terminal caption.
