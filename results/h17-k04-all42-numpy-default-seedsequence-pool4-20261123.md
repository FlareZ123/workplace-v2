# K04: exact NumPy default MT19937 SeedSequence pool4 inversion under all42 source chronology

**Agent 1 | 23 November 2026 | Complete conditional producer exclusion at 625 actual output offsets; K04 remains missing.**

## What was reconstructed

This uses Agent11's frozen single native-MT19937 133-row *all42* stage vector with a complete original-source GF(2) fit: 528 intact source words, 25 fullword and 17 partial original recurrence witnesses, source rank **15,434**. The source stage vector is **historically unconfirmed** and predicts **0/132** complete original held-out packets. This experiment asks whether that one stage interpretation could arise from the **actual NumPy `MT19937(SeedSequence(...))` default four-word pool initializer**, thereby recovering a complete source producer and a selected coupon.

The default NumPy pool4 emits initialized MT state words `S[i]` for `i=1..623` via `b_i = INIT_B * MULT_B^i mod 2^32`, `f_i=b_i*MULT_B mod2^32`, `w_i=(pool[i mod 4] XOR b_i)*f_i mod2^32`, `S[i]=w_i XOR (w_i>>16)`, where `INIT_B=8B51F9DD` and `MULT_B=58F38DED`. `S[0]=80000000`. Both factors are odd, so a **single source-determined full `S[i]` uniquely inverts to the matching 32-bit pool residue**:

```text
pool[i % 4] = (((S[i] XOR (S[i] >> 16)) * inverse_mod2^32(f_i)) mod 2^32) XOR b_i
```

Every independent source-fixed word with the same residue must recover the **same** pool word, irrespective of the entropy supplied to NumPy SeedSequence. A contradiction is final for this initializer, without enumerating possible entropy values. The source projection fixes numerous complete initialized-state words in each of four residues; once all four pool words agree, the program independently rebuilds all 624 initialized state words and checks every source-determined bit.

## Original and planted runs

The original printer SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Its selected 18:02Z PS-261003-0417 ACK attempt2 row129 is **omitted before copied payload decoding**. Source only is consulted during producer recovery. There are **625 possible NumPy raw-output origins** in the first cycle of this particular stage model: its initial output from initialized word623 (`pos=623`, modeled as offset **-1**) and every 624 possible offsets 0..623 after the first twist.

| Original-source inversion outcome | Offsets |
| --- | ---: |
| Contradiction with fixed `S[0]=80000000` | **126** |
| Two complete initialized words in one pool residue invert to different pool values | **499** |
| Source-compatible complete default pool4 generators | **0** |
| Total original origins checked | **625** |

For origin -1, a separate NumPy `random_raw` control confirms the first generator output equals `temper(S[623])`. This initial origin fails `S[0]` against original source. The 624 post-twist offsets were executed in **three disjoint original-source blocks [0,200), [200,400), [400,624)**. Their incompatible outcomes were 44+38+43 initial-state mismatches and 156+162+181 pool4 mismatches respectively, giving the exact table above. No original source-compatible pool4 model and therefore no complete model-generated target coupon exists in the enumerated domain.

**Five genuine positive controls pass:** actual `numpy.random.MT19937(numpy.random.SeedSequence(seed))` initial states at offsets -1 (two seeds), 0, 93, 616 generate the same 133-row all42 stage stream with selected row withheld. Every genuine initialized-state mask agrees, the exact pool inversion recovers all four real pool words, and regenerating the 624 initialized words reproduces NumPy's state. These checks establish that original rejection reflects the source bytes under this frozen stage map rather than a faulty pool4 inverse.

## Boundary and next action

This **does not exclude NumPy MT19937 globally**. A different original printer stage geometry, nondefault `pool_size`, independent issuer, reseeding or copy mechanism is outside the test. Previous Agent33 work rejected NumPy pool4 for a different hypothetical p951 first-cycle alignment; this covers the 625 origins of the later independently full-source-consistent *all42* chronology and demonstrates how to rule out a whole seeded state family without guessing seed values.

Reproducer: [Agent1 NumPy default-pool inversion SFT](../agents/agent1/k04_numpy_pool4_all42_source_sft.py), with [original all42 native-state source projector](../agents/agent1/k04_all42_cpython_n98_extended_sft.py). All five genuine seeded cases and all original offset blocks were executed locally; source, verifier, original acceptance commitments and canonical candidate unchanged.

No authentic K04 byte or K08 exact author-final caption is recovered. Original recovery remains **six accepted components, K04/K08 missing, REC8 combined incomplete**. Further seeded-family sweeps without a source-authenticated printer model are unlikely to establish a physical selected coupon.
