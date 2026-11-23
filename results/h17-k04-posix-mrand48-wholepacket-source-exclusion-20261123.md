# K04 POSIX mrand48 whole-packet source gate (23 November 2026)

**Agent 49 | 132 original intact packets × four serializations; zero pair matches.** No missing original K04 value recovered.

## Complete producer hypothesis

Treat each 16-byte retained printer payload as four consecutive signed-32-bit `mrand48()` outputs from one 48-bit POSIX LCG state. Permit both 32-bit word endiannesses and forward/reverse four-word order. Hidden draws *between* packets are unconstrained; the necessary test is entirely within an intact 16-byte packet. Because the first observed output discloses the top 32 state bits, enumerate all **65,536** possibilities for its unobserved low 16 state bits, advance the actual POSIX recurrence

`s_{n+1} = (0x5DEECE66D × s_n + 0xB) mod 2^48; output_n = s_n >> 16`,

and check the next **three complete** 32-bit outputs. Any producer in this exact class must at least fit the first output pair in every packet, regardless of startup seed, prehistory, timestamps, or interpacket draw gaps.

This is a distinct legacy office-device generator hypothesis, not a conclusion that the actual printer used `mrand48`. It does not attempt another native-MT draw-gap, category-map, or byte-copy repair.

## Original original-source test

Input `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The disputed `PS-261003-0417 / ATTEMPT=2 / ACK / RECOVER` row is **skipped by descriptor before its PAYLOAD is hex-parsed**. Source parser asserts exactly 132 other intact 16-byte packets and one selected exclusion. No K04 acceptance target, route mask, canonical candidate, or copied selected 18:02 payload is accessed by the algorithm.

| Four-word view | Two-word valid state from any intact row | Complete 16-byte valid packet |
|---|---:|---:|
| Little endian, forward | 0/132 | 0/132 |
| Little endian, reverse | 0/132 | 0/132 |
| Big endian, forward | 0/132 | 0/132 |
| Big endian, reverse | 0/132 | 0/132 |
| **Total** | **0/528** | **0/528** |

The source-only test evaluates all 132 × 4 × 65,536 = **34,603,008** first-state possibilities with all 32 observed bits compared at every step. Each of four genuinely generated POSIX `mrand48` four-output packets is inverted to its unique after-first-output 48-bit state; corrupting the fourth output bit makes the planted complete-packet inversion fail. All four positive and four negative controls pass. Local stdlib Python execution completed on the original attached export.

**Reproducer:** [`agents/agent49/k04_mrand48_source_sft.py`](../agents/agent49/k04_mrand48_source_sft.py), default original repo path or `--spool` for an isolated extracted copy. The output is deterministic JSON, with source digest, source row count, all views and planted controls.

## Decision and boundary

The **four-consecutive-`mrand48` whole-packet model is incompatible with every intact original 16-byte printer payload**, before target selection and without relying on a specific initial seed or stage offset. Do not use that exact producer to infer the lost selected K04 packet or spend time brute-forcing its seed.

This bounded negative does not exclude other LCG serializers, nonconsecutive call models, an independently generated selected physical coupon, or the native-MT hypotheses currently under separate study. Importantly, it provides **zero authenticated selected physical K04 bits** and **zero original K08 final words**. The original six accepted slots and combined-incomplete REC8/1 state remain unchanged; no original evidence, acceptance, verifier or canonical candidate modified.
