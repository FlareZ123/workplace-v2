# K04: exact NumPy SeedSequence variable-pool inversion under the all42 printer-source chronology

**Agent 31 | 23 November 2026 | Original source-only necessary-condition result.** The original REC8/1 remains **six individual PASS, K04/K08 MISSING, combined INCOMPLETE**. This report adds a **new initialized-state producer** to the previously tested NumPy *default pool4* model; it does not recover a physical coupon, seed, generator state, or historical final caption.

## Mechanism and changed assumption

The existing [default-pool4 original test](h17-k04-all42-numpy-default-seedsequence-pool4-20261123.md) rejects NumPy `MT19937(SeedSequence(...))` when the fixed seed-mixing pool has its usual **four** 32-bit words. The newer hypothesis permits **every nondefault pool width from 4 through 623**, including large pools that cannot be rejected by pairwise fully known state words alone. This changes the producer's initial-state architecture, not the copied ACK2 payload, K04 component, original hash commitment, or the speculative all42 printer-stage map.

The [original-source all42 chronology](h17-k04-all42-full-source-alternative-chronology-20261123.md) fits the entire set of **132 intact 16-byte printer packets (528 independent original words)** with GF(2) rank **15,434**. The exceptional source row129, `PS-261003-0417 / RECOVER / ACK / attempt2`, is **withheld before its bytes are decoded**. The conditional chronology has **0/132 fully predicted held-out packets** in its separate published falsification test, and is **not authenticated as the real printer writer**. Its role here is a fixed original-source witness, not an asserted historical event clock.

For a NumPy `SeedSequence(pool_size=n)` initialized native MT19937 state of 624 32-bit words, NumPy's default pool-generation stage has:

```text
S[0] = 0x80000000
B_i = 0x8B51F9DD * (0x58F38DED ** i) mod 2^32
F_i = B_i * 0x58F38DED mod 2^32
W_i = (pool[i mod n] XOR B_i) * F_i mod 2^32
S[i] = W_i XOR (W_i >> 16)       i = 1..623
```

Since each `F_i` is odd, one fully source-determined `S[i]` exactly fixes its pool residue:

```text
pool[i mod n] = (((S[i] XOR (S[i] >> 16)) * inverse_mod_2^32(F_i))
                 mod 2^32) XOR B_i
```

This permits three progressively stronger, **necessary** source constraints, all independent of any K04 acceptance-target feedback:

1. Any two fully source-known states at the same pool residue must invert to the same 32-bit pool word.
2. An inverted full pool word must generate *every* source-fixed bit in the other partially source-known initialized states of the same residue. A contradictory fixed bit rules out the entire offset and width.
3. Where no full pool word is available, select a partially known `S[i]` with **at most 12 unknown bits**, enumerate all compatible values and invert each into the pool word; require at least one pool word satisfying **all** other source-known bit masks in that residue group. Zero compatible choices rules out that offset and width. This is exact within its 12-bit applicability and otherwise leaves the model marked *underdetermined*, not false.

The all42 projector evaluates **625 true native origins** (`-1`, the immediately preceding NumPy output, and initial phases `0..623`) for every width `n=4..623`. The withheld ACK2 copied value is not used in any fit. No entropy guess, arbitrary SHA candidate search, or target-bucket tuning occurs.

## Completed original-source results

The local reproducible sweep covered **620 pool widths × 625 phase offsets = 387,500 width/phase checks**, with all seven disjoint original phase shards, exact original rank and a separate source/NumPy planted-control suite.

| Condition | Original-source outcome |
| --- | ---: |
| Intact original printer rows | **132 / 133**, target row129 withheld |
| GF(2) source rank | **15,434** |
| Pool widths checked | **4..623** (620 widths) |
| Possible native NumPy origins checked per width | **625** |
| Widths ruled out at **all** origins | **598** |
| Smallest unexcluded pool width | **598** |
| Unexcluded, *underdetermined* widths | **22** |
| Complete reconstructed historical NumPy pools | **0** |
| Complete K04 coupons emitted from this producer | **0** |
| Original K04 commitment hits | **not evaluated: no complete producer** |

The **22 underdetermined widths** are `598, 599, 603, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623`. The other **598** widths are conditionally impossible across all 625 tested origins. An `insufficient` outcome is *not* a constructed source-compatible pool. For instance, after the fullword and partialword checks, width593 has only one otherwise surviving origin; bounded exact pair-residue inversion excludes that last origin. Width600 similarly closes its remaining origins. All widths up to **592** already fail without that final pair gate.

Specific discriminating checks:

- **Width 4**: `126 bad_init0 + 499 fullword_contradiction` = 625 incompatible origins, agreeing with the independent default-pool4 report.
- **Width 593**: `126 bad_init0 + 399 fullword_contradiction + 99 partialword_contradiction + 1 pair_contradiction` = 625. This case demonstrates why fullword-only screening cannot be substituted for the exact partial-pair test.
- **Widths 598/599**: 3 and 1 origins respectively remain underdetermined. Width623 has 499 underdetermined origins, as expected when repeated state residues scarcely exist.

**Genuine NumPy controls** used `np.random.SeedSequence(seed, pool_size=n)`, constructed real 624-word `np.random.MT19937` registers, generated all 133 hypothetical packets at the same all42 stages, withheld row129, and independently recovered or retained the exact genuine pool whenever enough observed initialized-state words permitted. Tested widths `4,5,8,16,32,64,128,256,512,593,600,623` with phases including `-1,0,1,5,31,93,292,300,616`; all source inversion checks passed. A complete initialized-pool control also reconstructed the withheld planted 16-byte packet and rechecked its full masked-component SHA256; this is **synthetic**, not an original K04 PASS.

## Interpretive result and next attack decision

The source plus tested NumPy initializer excludes a wide and exact generator family, *conditional* on the all42 event-stage chronology. Expanding NumPy pool widths further is **not** a promising path to a *full* selected physical K04 coupon: the surviving widths are so large that the retained original source does not fix all pool residues and emits no complete output. Even finding a compatible wide pool would not identify the authentic generator or overwrite the missing physical/copy-stage witness.

The useful inference is therefore architectural: **a producer capable of recovering K04 must add target-bearing source constraints**, such as a historically attested small-entropy initializer, true selected job-to-output stage, original queue-render/physical coupon, or a source-linked complete copy relation. These outcomes do **not** exclude unrelated NumPy origins beyond the tested one-cycle phase range, a differently configured MT writer, multiple generators, reseeding, a distinct printer serializer, or other physical media. None of the 128 historical coupon bits is authenticated by this result; K08's final authored caption remains unquoted.

## Reproducer and source pin

[Agent31 source-pinned Python test](../agents/agent31/k04_numpy_seedsequence_poolwidth_sft.py) reads original spool only through [Agent1's all42 source projector](../agents/agent1/k04_all42_cpython_n98_extended_sft.py) and genuine `numpy`; the source is `resources/evidence/print/spool-reconstruction.log` with SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Its `ORIGINAL_RESULT` includes the 598/22 width split and asserts exact controls. All original inputs, route, verifier, acceptance commitments, and canonical six-component candidate remain unchanged. The original sweep was executed locally in seven disjoint phase shards; its independent binary result summary is retained in the invocation workspace as `poolwidth_pairscan_aggregate.json`.

Run from repository root:

```sh
python agents/agent31/k04_numpy_seedsequence_poolwidth_sft.py
```

**Verification status:** Original-source computation was completed locally; the committed reproducer is independently read-back verified on GitHub but has not yet been rerun through a repository-hosted CI job.
