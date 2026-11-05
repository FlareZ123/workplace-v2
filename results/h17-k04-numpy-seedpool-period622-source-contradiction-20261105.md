# K04: NumPy SeedSequence unknown seed-pool length sieve and exact n622 wrap contradiction

**Agent 30 | 5 November 2026 | New original-source algebraic certificate; no physical coupon recovered.**

## Structural question

Previous H-17 tests of NumPy's MT19937 `SeedSequence` producer tried default pool width 4 and nine nondefault choices 8, 16, 32. An unexplored possibility is an **arbitrary original pool period n**: initialized native MT word i>0 depends on a single 32-bit `pool[i mod n]` lane. Two initialized register positions with equal residue require the exact same pool word even when the original entropy source or seed length is unknown. This lets original printer state constraints reject *whole producer families independently of every possible seed value*.

The exact default NumPy seedpool initializer is
`B_i = (0x8B51F9DD * 0x58F38DED^i) mod 2^32`,
`M_i = (B_i * 0x58F38DED) mod 2^32`,
`S_i = V_i xor (V_i >> 16)`, `V_i = ((pool[i mod n] xor B_i)*M_i) mod 2^32`, for `i=1..623`. `S_0=0x80000000` is overwritten by NumPy and never constrains `pool[0]`. Each `M_i` is odd and invertible mod2^32, so every complete source-constrained `S_i` implies a single pool value; one unknown bit implies exactly two allowed pool values. Intersect allowed values at residues shared by distinct initialized register indices. This intersection is a conservative *necessary condition*, without any original selected K04 coupon, target commitment, routing mask or physical copy.

## Original printer sources and pooled-period census

Use untouched original printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, omit untrusted selected row129 before decoding, retain **132 intact original 16-byte packets** and the existing unverified p951 little-endian four-native-word printer geometry. Build the exact GF2 source basis of rank15,365 and reproject original initialized-state words for *real* prior generator output offsets k. Then test **all n=4..623** pool periods (620 widths) with no original seed guess. At startup k=0, **270 initialized-state words** have at least31 source-fixed bits.

| Genuine NumPy output startup offset k | Original source-fixed words usable as pool witnesses | Periods n=4..623 surviving necessary intersections | Interpretation |
| ---: | ---: | ---: | --- |
| **0** | **270** | **2: n622 and n623** | All n4..621 rejected by exact source pool-residue contradictions |
| 624 | 141 | 21 | First survivor n560; all n4..559 rejected, with additional scattered larger exclusions |
| 1248 | 97 | 81 by residue intersections | **All actual NumPy pool models excluded at this k**: independently original `S0=80000000` contradicts the source, so 81 are only what the *residue test alone* would leave |
| 2496 | 8 | 535 | Weak late-source observability; the necessary condition cannot identify a pool |
| 3744 | 4 | 609 | Most periods survive; n4 already contradicted |

The complete reference scan is [Agent30 arbitrary-period SFT](../agents/agent30/k04_numpy_arbitrary_period_source_sft.py) and [successful CI run 42078473927](https://github.com/FlareZ123/workplace-v2/actions/runs/42078473927). All **40 real NumPy seeded full-register controls** (eight true pool sizes 4,5,7,8,16,32,64,128 at each five offsets) passed: the planted actual width always survives the partial-original-source period sieve. NumPy itself, not a synthetic recurrence surrogate, generated the entire 624-word initialized register and all 133 simulated printer packet positions (with selected packet withheld for inference).

## New exact two-word wrap contradiction excludes n622 at origin0

The initial pool-period sieve overlooked source bits in state words with fewer than31 determined bits. For n622 specifically, initialized words i1 and i623 share pool residue **1**; they must have matching independently invertible pool terms despite 622 preceding initialization updates.

The original 132-packet source fixes:

- `S1 & 0x80000001 = 0x00000001` (MSB **0**, low bit **1**).
- `S623 & 0x7fffffff = 0x04710790` (31 low bits fixed; high bit unknown).

All **two** complete possible `S623` words can be inverted through `M623` to recover a candidate `pool[1]`, then forwarded exactly through NumPy's index1 initializer. The two predicted `S1` words are:

| Possible original S623 high bit | Forced S1 from same pool word | Contradiction with separately source-fixed S1 |
| --- | --- | --- |
| 0 | `62C95BD8` | Low bit 0, but source requires 1 |
| 1 | `EAF453E5` | MSB 1, but source requires 0 |

**Both** finite, exact original-source alternatives are impossible. Therefore the prior two remaining period candidates reduce from `{622,623}` to **`{623}` only**. The original printer excludes **every NumPy SeedSequence pool period n=4..622**, with *arbitrary 32-bit pool values*, at the stated k0/p951 printer geometry. This is a much stronger source-only class falsifier than testing particular seed words or a small list of pool widths. It does not prove that n623 is historically valid, because NumPy's actual entropy-to-pool mixing and original selected physical coupon remain unknown.

[Reproducer with exact two-value certificate](../agents/agent30/k04_numpy_pool622_wrap_sft.py), [successful CI run 42078918103](https://github.com/FlareZ123/workplace-v2/actions/runs/42078918103). A genuine independent `np.random.MT19937(np.random.SeedSequence(seed,pool_size=622))` stream reconstructed the true pool from one of the two possible state-word completions under the same source geometry: exact source-positive control **PASS**. The original two alternatives both fail.

## Bounds and next attack

This **does not** establish that the printer was written with NumPy or that p951 is its historical output placement. The 623-word period is qualitatively different: i0 is overwritten and i1..i623 occupy distinct pool residues. Thus this *periodicity test* alone cannot constrain the initialized register beyond the independently source-fixed `S0`. Period sizes n>=624 likewise have no repeated live pool residues, so they are outside the finite n4..623 sieve and cannot be excluded by this mechanism. A genuine 623-word `SeedSequence` entropy initialization would require an additional source-based seed-family constraint before reconstructing K04.

The genuine selected original K04 coupon remains fully unauthenticated, and K08's final Emily inscription is unquoted in the local export. Six original components PASS; K04 and K08 MISSING; combined REC8 INCOMPLETE. Next development should target a source-independent actual printer producer/copy mechanism or another **concrete, target-reaching** relation; this conditional NumPy seedpool family no longer warrants repetitive guessed small-width expansions.
