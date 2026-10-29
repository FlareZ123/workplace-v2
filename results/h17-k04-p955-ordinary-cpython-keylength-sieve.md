# H-17 K04: 42 original ordinary-row CPython seed-residue witnesses, 395 conditional key lengths excluded

**Agent 47 (29 October 2026).** Source-only, hypothetical first-cycle producer discriminator. **No authenticated selected coupon bits recovered; K04 and K08 remain missing.** This result does not consult the disputed ESC-N selected ACK, route mask, REC8 acceptance digest, or other completed slots.

## New original-derived constraint

Use the surviving unmodified print spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, and the *previously published* source-compatible, historically unauthenticated MT19937 start-vector `results/h17-k04-source-consistent-index955.json` in workplace-v1. In that conditional common-producer geometry, printer row129 begins at stream word955.

**Remove every exceptional `Z` row128..132, including selected row129.** Only original 128 intact *ordinary* spool records contribute to the 19,968-bit MT initialized-register GF(2) elimination. The exact ordinary-only equation rank is **15,014**, contradiction count **0**. It fixes **190 complete initialized MT19937 register words**; 427 other words have at least one fixed bit. (The current [Agent47 source-pinned donor SFT](../agents/agent47/k04_p955_seedseq_original_donors_sft.py) also records rank15,305 when all 132 other printer records are used.)

Unlike the earlier v1 Agent26 seed-period screen, which found seven potential key-term positions in several short conditional source windows with an unknown phase, the full ordinary-only p955 geometry fixes **42 distinct complete three-consecutive-word windows** able to reconstruct exact CPython `init_by_array` key-term values at predetermined pre-output register indices. The 42 numbers are directly recomputable from the original spool, with the target entirely excluded.

## Exact necessary-condition math

For a standard CPython `random.Random(integer_seed)` / `init_by_array` initializer whose input `key_length = n` lies in `1..624`, the first mix makes 624 updates. For indices `i>=4`, far from the wrapped special state word1, the final initialized register `S[i-2:i+1]` fixes the term `KEY[(i-1)%n] + ((i-1)%n)` modulo `2**32`. Invert the second mix locally:

```
B[i] = (S[i]+i) xor ((S[i-1] xor (S[i-1]>>30))*1566083941 mod 2**32)
term(i) = B[i] - (G[i] xor ((B[i-1] xor (B[i-1]>>30))*1664525 mod 2**32)) mod 2**32
```

Here `G[i]` is the reference `init_genrand(19650218)` state. Both formulas exactly implement documented CPython `Modules/_randommodule.c` initialization arithmetic. As a source-only necessary equality, **two recovered terms at indices whose `i-1` positions are congruent modulo `n` must be identical**. This excludes whole key lengths without enumerating any seed values or touching K04's hash. It is a necessary condition only; a surviving length may still be incompatible with other constraints.

## Executed original result

| Quantity | Outcome |
| --- | ---: |
| Original normal printer records contributing | 128 of 128 |
| Selected and all other late exceptional records included | 0 |
| Original initialized-state GF(2) rank | 15,014, zero contradictions |
| Fully source-fixed 32-bit initialized-state words | **190** |
| Independently indexed complete three-word key terms | **42** |
| CPython input key-array lengths tested | **1..623** (623 total) |
| **Conditionally excluded lengths** | **395** |
| Conditionally surviving lengths | 228 |
| **Contiguous early excluded lengths** | **1..144**, every length |
| First not excluded length | 145 |

Two exact original-source witnesses, for example:

- `n=1`: key-term at `j=4` is `E433AC11`; at `j=5` it is `32E2A5D4`. The same residue requires equality, so this length fails in the conditional p955 model.
- `n=144`: terms at `j=131` and `j=275` both map to residue131, but are `5AD3D29D` and `FD7F5141`, giving a direct contradiction.

Lengths `145` and `623` pass **this necessary filter only**. Length624 would be automatically free of repeated-residue witnesses (also not ruled out by this test); lengths greater than624 change the reference first-mixing-iteration count and lie outside this certificate.

## Reproducibility and original-heldout controls

The [read-only SFT](../agents/agent47/k04_p955_cpython_length_sieve_sft.py) recovers the original 190 full words from the pinned spool through the existing Agent47 GF(2) routine, derives the 42 terms, checks each `n` exactly, and asserts the 395 exclusions and 144-length prefix. It tests actual Python `random.Random` initialized states made from 12 independent known input lengths `1,2,3,4,5,13,20,31,80,145,256,623`: **all 12 pass** all 620 valid term equations, including the length623 edge. The SFT makes no attempt to derive a selected original K04 coupon candidate.

## Critical provenance and target-reachability limits

The entire claim is **conditional on the pre-existing p955 chronology and common MT19937 producer**, both of which are supported as payload-compatible mathematical models rather than authenticated historic printer code. The p955 vector was originally selected using original *late* recurrence relations, despite those late payloads being omitted from this experiment's affine equations. Accordingly, calling the 42-term test an independent blinded late-event observation would be incorrect.

A failure of `init_by_array` word lengths 1..144 in **this** model is a precise producer-family exclusion. It does **not** establish what the H-17 printer truly used, eliminate alternative stream origins/restarts/copy stages, or determine any original selected row129 payload bit. A physically authenticated selected-event producer bridge, independent media/mask integrity, or newly preserved original coupon remains necessary for K04. Emily's absent final keeper-envelope words independently block K08.

**Nearest prior art:** v1 [Agent26 seven-key-term period sieve](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-seven-residue-seed-period-gates.md) and its 17 scoped length exclusions, v1 [whole-spool p955 projection](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-global-stream-target-observability.md), and v1 Agent22 sparse `std::seed_seq` initialization donors. This result is a **different input geometry and 42-term, 623-length original-source test**, independent of the separate C++ seedseq formula. These original values leave the K04 selected quotient 128/128.
