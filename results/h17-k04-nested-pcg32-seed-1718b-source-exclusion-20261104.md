# K04: complete 2^34-state nested PCG32 binary-seed source exclusion (4 November 2026)

**Agent 24.** Original eight-slot REC8 status remains **six PASS**, K04/K08 MISSING, combined INCOMPLETE. This result is a finite, conditional generator exclusion, not a reconstructed original coupon or physically authenticated key bit.

## Distinct complete-seed reconstruction hypothesis

In Agent 15's [hypothetical p951 CPython `Random(bytes)` source-fingerprint model](h17-k04-p951-python-sha512-binary-seed-fingerprint-20261104.md), the unknown binary input `B` is constrained by preserved source packets, including these relative **consecutive 32-bit seed-input word positions** (not directly observed generator bytes):

| `B` word relative to `key[602]` | Permitted source-derived values |
| ---: | --- |
| 0 | `64589C88` or `E4589C88` |
| 1 | `49342EC0` |
| 12 | `6425CF5B` or `E425CF5B` |
| 579 | `06EDCDAD` |
| 580 | `FD6A4CF7` |

Could `B` be consecutive 32-bit native outputs of **PCG32 XSH-RR 64/32**, with an unknown 64-bit generator state but the published one-sequence increment `1442695040888963407`? If yes, reconstruct its state from an early output, check untouched farther source seed words, then emit all `B` bytes and regenerate the hypothetical selected K04 coupon via CPython. This is an independently testable complete-candidate mechanism that does not depend on copied ACK2 integrity.

The PCG32 output function and transition follow the [official minimal reference](https://www.pcg-random.org/download.html): `rotr32((uint32)((s>>18 ^ s)>>27), s>>59)` and `s' = 6364136223846793005*s + 1442695040888963407 mod 2^64`. Two uniform byte orders per 32-bit `B` word were tested. An unknown seed phase is absorbed by the arbitrary 64-bit state at relative word0.

## Exact inversion, original test and controls

For each possible first output and each of **32 rotations**, invert the XSH RR relation to identify all 37 upper state bits (positions27..63). The 27 lower state bits remain wholly unconstrained by that first output, so exhaustively enumerate all `2^27` of them. This checks every one of `2^32` internal states compatible with each first output and does not rely on seed lists or SMT model incompleteness. Use exact PCG LCG jump coefficients to predict source-relative word12 independently, then original word1, 579 and 580.

The four predeclared authentic cases are `2` first-word possibilities × `2` byte orders. Their exhaustive original outcomes:

| First-word option | Byte order | Complete internal states | States matching independently retained word12 | States also matching retained word1 |
| --- | --- | ---: | ---: | ---: |
| `64589C88` | big | 4,294,967,296 | 3 | **0** |
| `E4589C88` | big | 4,294,967,296 | 0 | **0** |
| `64589C88` | little | 4,294,967,296 | 3 | **0** |
| `E4589C88` | little | 4,294,967,296 | 0 | **0** |
| **Total** | | **17,179,869,184** | **6** | **0** |

There were **zero** valid source candidates, before any later 579/580 check, SHA-512 seed digest, copied coupon, route mask or K04 target commitment. The source test is decisive for the exact stated architecture.

The read-only test SHA256-pins original `resources/evidence/print/spool-reconstruction.log` as `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. It verifies a **genuine planted PCG32 original state** `AABBCCDD9800002A`: the same first-word/rotation/low27 search recovers exactly its withheld full state using authentic synthetic words at positions 0,1,12,579,580, with an exact unique positive. On original data it completes all four full state intervals, without reading selected K04 spool bytes or any acceptance commitments.

**Reproduction:** [portable C/OpenMP/OpenSSL complete-state SFT](../agents/agent24/k04_nested_pcg32_seed_inverse_sft.c). Locally executed equivalent complete implementation: `/mnt/data/h17local/nested_pcg32_seed.c`, SHA256 `6dbaa92d3bf7194b311b399ae25025cd480aa7717eac1f30b57a0988cf7f1eca`, with the exact four original counters above. The committed version preserves the same inversion, state enumeration, output and original-source pins and was remotely read back exactly; no separately dispatched GitHub Actions rerun was needed.

## Scope and implication

This **nested binary seed** model is distinct from [Agent 27's direct PCG32 four-word printer source exclusion](h17-k04-pcg32-fullstate-source-exclusion.md): that predecessor consumed four direct spool payload words, whereas this attack uses **five conditionally inferred distant words of an intermediate 2.4 kB Python binary seed**. It is also distinct from Agent29's nested xorshift128/xoshiro128** and xorshift1024* seed tests and Agent15's unrestricted 32-bit affine LCG stream. No historically surviving H-17 source states either PCG32 or CPython p951 was actually used; the retained-word constraints are conditional on the upstream model.

Unspecified PCG increments, skipped generator outputs, independent reseeding, nonstandard serializers, or a wholly different source architecture are outside the test. **The target-bearing missing ESC-N physical coupon still has zero authenticated new bits**, and no verbatim K08 final caption was found. This result eliminates a compact path from surviving packets through an inner 64-bit PCG32 state to a complete K04 coupon, so additional brute-force searches of the same one-sequence nested PCG32 model would be redundant.

### Nearest new adjacent test

A separate [two 64-bit-output-block phase test](../agents/agent24/k04_seed_64bit_pair_parity_sft.py) exhausted 36 SplitMix64, xorshift64*, and raw full-state PCG LCG64 phase/layout candidates with zero independent source-word matches. Both are finite **source-input reconstruction** investigations and should not be misconstrued as authentication of the disputed printer ACK2.
