# K04: all-phase nested xorshift1024* binary-seed producer falsifier

**Agent29, 4 November 2026 UTC.** An original-source, selected-target-independent test. **All 16 source-consistent serialization configurations of a contiguous 64-bit xorshift1024* *inner binary-seed stream* are contradictory; all 16 matched synthetic seeded controls pass.** This excludes a specific two-level producer architecture, under the hypothetical original printer p951/CPython first-cycle `Random(bytes)` model. It does **not** recover original selected K04 or terminal K08.

## Why the attempted producer could reach K04

Under [Agent15's original-source binary seed analysis](h17-k04-p951-python-sha512-binary-seed-fingerprint-20261104.md), the 132 intact printer packets pin **86 disjoint 32-bit segments of the unknown binary seed B** (62 complete, 24 with a one-bit ambiguity). The hypothetical long B is supplied to standard CPython `Random(B)`; if B itself came from a deterministic low-state producer, reconstructing that producer could fill the missing B bytes, meet the SHA-512 seed fingerprint and predict the omitted selected original coupon. The recorded 18:02 ACK2 copy, K04 XOR mask and K04 commitment were deliberately withheld.

The separate [Agent29 128-bit nested-producer falsifier](h17-k04-nested-linear-seed-producer-20261104.md) ruled out xorshift128 and xoshiro128** as B emitters. This attack changes both generator state dimension and word layout: **standard xorshift1024\*** carries 16×64bit linear state, advances a circular pointer, transforms two registers by shifts31/11/30, and multiplies the resulting output modulo2^64 by odd constant `1181783497276652981`. The output multiplier is invertible on every low-bit prefix. Its full initial state is potentially reconstructible because the 86 original-source seed words together constrain thousands of B bits.

## All byte phases and evidence preservation

The B segments are extracted only from `resources/evidence/print/spool-reconstruction.log` with original SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, by Agent15's [original native-register SFT](../agents/agent15/k04_p951_sha512_seed_fingerprint_sft.py). Row129, the disputed selected printer ACK2, is excluded before decoding. No other original key component, commitment or verifier enters the model.

For **each of eight possible alignment offsets** of the 32-bit B fragments against the generator's 64-bit output and **both 64-bit big- and little-endian output serializations**:

1. Reconstruct every source-known byte of B. An ambiguous seed word changes only its highest bit, leaving the bottom seven bits of its first big-endian byte plus the next three bytes fixed.
2. For each generator output byte window, collect the longest fully source-fixed **least-significant-bit prefix** of its observed output. Unknown byte windows contribute zero constraints. Multiply this prefix by the 64-bit modular inverse of the constant, retaining only those known low bits, to obtain exact low bits of the *linear pre-multiplied* generator output. This technique allows all eight byte offsets without falsely interpreting incomplete 64-bit bytes as complete observations.
3. Generate the GF(2) coefficient for each such bit as a linear function of the 1,024 initial generator state bits. Build a source-only Gaussian-elimination basis; stop on the first source-contradictory equation.
4. **For every one of the 16 configurations**, separately generate a synthetic true xorshift1024* stream with nonzero planted state, apply the same original index-selection and one-bit source-domain masking, and require that the solver accept all synthetic equations at rank1,024.

## Executed original-source outcome

| Source observation | Result |
|---|---:|
| Enumerated byte-offset and output endian combinations | 8 × 2 = **16** |
| Original source contradictions | **16/16** |
| Independently planted true-stream cases | **16/16 accepted**, rank 1,024 |
| Original selected physical K04 bits recovered | **0/128** |
| Authenticated K08 terminal words | **0** |

The detailed program prints per-configuration number of original source-visible low-bit equations, source rank and the first contradictory equation. For example, offset0/big has **2,059** source-visible low-bit equations but becomes inconsistent at equation1,025 (rank1,023); offset7/little has **1,120** source-visible equations and becomes inconsistent at equation1,024 (rank1,023). Other configurations disagree at rank736..1,024. These early contradictions on several phases arise from dependencies of the linear generator map, not merely from exhausting its 1,024 unknown bits.

[Portable SFT: `agents/agent29/k04_nested_xorshift1024star_sft.py`](../agents/agent29/k04_nested_xorshift1024star_sft.py), locally executed against the supplied ZIP's original spool using an independent locally replicated implementation of Agent15's 86-word source extractor. The 16 original negatives and 16 synthetic positives were reproduced. A dedicated GitHub Actions run was unnecessary for this sub-ten-second source-discrimination workload.

## Interpretation and next decision

The stated source constraints are incompatible with a binary B assembled by serializing **contiguous standard 64-bit xorshift1024\*** outputs in either endian, under any 8-byte start phase, **without skipped generator outputs or secondary transformations**. The same original-source dependency **does not authenticate CPython as the actual printer producer**, identify an intact selected physical ACK2, or touch an original K04 hash. The result is an exact conditional 1,024-state class exclusion, rather than a universal claim about pseudorandom generators or unknown binary seed B.

The most effective subsequent construction would either demonstrate a historically selected ACK2 source-stage mechanism on the genuine role-matched intact comparator or identify a source-defined long binary-seed layout distinct from the excluded affine, 128bit and 1024bit generator families. Repeating arbitrary nested generator names is not itself a recovery strategy. Original candidate, commitments, resources and verifier remain unchanged; K01,K02,K03,K05,K06,K07 individually PASS; K04 and K08 remain MISSING; combined REC8/1 INCOMPLETE.
