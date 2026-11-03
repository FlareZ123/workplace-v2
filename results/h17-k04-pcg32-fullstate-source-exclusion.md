# K04: seed-free complete PCG32 state inversion on original printer payloads (Agent27)

**3 November 2026, normal mode. Outcome: NO source match for three frozen-increment PCG-XSH-RR 64/32 models; no K04 source coupon recovered.** Exact original spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original selected ESC-N ACK attempt2, K04 route XOR mask, commitment, K08 phrase and verifier are **never inputs** to this producer test.

## Distinct hypothesis and exact state inversion

Test the PCG32/XSH-RR generator in the official [minimal PCG reference](https://www.pcg-random.org/download.html), with a 64-bit hidden state, 64-bit fixed odd increment, and `state = 6364136223846793005 * state + increment mod 2^64`. Four successive original source packet words must be its four consecutive 32-bit outputs under a specified serializer.

The output is `rotr32(((state>>18)^state)>>27, state>>59)`. Given only **one** original full 32-bit output, enumerate its 32 possible rotation values. Undo the rotation, then reconstruct exactly all state bits **27..58** from high to low by XOR inversion; rotation gives state bits **59..63**. Only the **27 lower state bits** remain. Each observed first output therefore identifies precisely `32 × 2^27 = 2^32` possible 64-bit internal states, every one of which is tested in the complete source-positive candidate search. No seed dictionary, phase assumption, stochastic state sample, calibration on selected payload or partial-bit heuristic is used.

Test three pre-frozen increments, separately: `DA3E39CB94B95BDB` (minimal/reference sequence), `14057B7EF767814F` (common one-sequence increment), `0000000000000001` (minimal odd increment). For each, test the **four original byte serializations**: individual 32-bit words BE or LE, with four-word order forward or reversed. The original intact earliest printer ACK row0 is `FBBBC54356483F5864BB3F06794518A5`, obtained by source-pinned extraction. None of the three increments is historically identified as the printer implementation.

## Reproducible actual outcomes

For every one of **12** (increment, serializer) conditions, the finite search enumerated exactly **4,294,967,296** candidate internal states compatible with the observed first source word, advanced the PCG recurrence, and checked all remaining three observed words. **Zero** complete four-word source matches in **51,539,607,552** total candidate-state tests. This excludes the entire 64-bit initial-state space for those twelve *fixed-increment direct four-consecutive-output* producer models. In particular a changed initial seed or unknown original phase cannot repair a failed model; phase is already absorbed in the arbitrary initial 64-bit state.

Positive controls: 128 inverse identities across all 32 rotations, and the entire matching search recovered exactly one planted state `853C49E67000002A` with all four generated PCG32 words for each tested increment. Original spool SHA-256 is checked before source extraction, and neither the six known key bytes nor any K04/K08 acceptance material is used. Complete SFT: [`agents/agent27/k04_pcg32_fullstate_inverse_sft.c`](../agents/agent27/k04_pcg32_fullstate_inverse_sft.c), requiring C11, OpenSSL SHA256 and OpenMP. The independently executed original implementation is `/mnt/data/agent27_k04_pcg32_inverse_sft.c` SHA256 `2faec940bc0821aa1f4b52872522657b96cfd7e5ef72e6569d4677de8acb94d6`; the committed SFT is a repo-portable cleanup retaining the same mathematical inversion, original source and exact enumeration.

## Scope and research consequence

This is **a source-level generator exclusion**, not a seventh recovered component. It does not exclude arbitrary 64-bit increments (which increase generator unknowns), PCG64/PCG64DXSM, separate streams, altered rotations, non-consecutive output emission, copied/changed physical ESC-N ACK2, or any other historical generator. It improves on a narrow seed-list pilot by exhausting **every 64-bit state** of three named standard producer families without needing to find a producer seed. The direct K04 coupon still requires a source-attested target-bearing mechanism.

Six historically accepted components unchanged. Authentic selected K04 bits **0/128**, exact final K08 words **0**, combined REC8 **INCOMPLETE**. Do not extrapolate this bounded producer-family exclusion to a general statement that PCG is impossible or that the original printer is a PCG variant.
