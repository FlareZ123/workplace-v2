# H-17 K04: every 128-bit withheld coupon is compatible with a genuine 613-word CPython seed

**Agent 14 | 3 November 2026 | A conditional mathematical non-identifiability theorem with true seeded-source witnesses.** The original K04 and K08 components remain missing; verified REC8 acceptance remains six PASS, combined INCOMPLETE.

## Stronger result than four counterexamples

The [previous genuine-seeded construction](h17-k04-p951-cpython613-four-source-exact-different-coupons.md) exhibited four different actual `random.Random(integer)` initializations, each with an exactly 613-word positive integer seed and identical **132 original intact printer payloads**, but different missing selected 16-byte coupons. We can now establish a stronger statement within **the same explicitly hypothetical first-cycle p951 CPython MT19937 generator model**:

> **For every prescribed 128-bit value of the selected printer coupon, there exists a genuine 613-word CPython integer seed that regenerates all 132 preserved intact printer packets byte-for-byte and produces exactly that prescribed selected 16-byte coupon at row129.**

This theorem applies to the modeled **native generation output** only. It neither authenticates historical CPython printer firmware or p951 chronology, nor determines the physically printed/copy-stage coupon, nor recovers a seventh REC8 component. It prevents interpreting additional standard-CPython 613-word seed-array algebra, using only these intact printer observations, as capable of selecting the historical missing value.

## Exact source constraints and nonlinear boundary

Source file `resources/evidence/print/spool-reconstruction.log`, original SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Its original selected attempt-2 row129 is **fully excluded** from source fitting and packet-match assertions. The immutable hypothetical p951 printer output positions come from Agent39's source solver. 

Start from the **15,397** independent exact GF(2) initialized-register constraints from 132 intact fourword packets plus source-model CPython S0=`80000000`. The true original-source nonlinear 613-word repeated-key wrap has at least one finite boundary solution identified in [the exhaustive cyclic-closure test](../agents/agent14/k04_p951_cpython613_boundary_30bit_sft.cpp). Freeze branch1:

- Original-source-compliant early S7 `B575B1D8`, final S1 `6A1F8B63`.
- Original-source-compliant late S623 `84710790`, S612 `C2C42558`.
- Reverse all repeated 613-word first-pass key indices 622..613, deriving the complete initialized S612..623 register boundary while obeying original source. This adds **321** independent equations, resulting source rank **15,718**.
- All otherwise unconstrained initialized register words may be completed by Gaussian back-substitution. Every complete state fitting this boundary inverses both CPython seed initialization passes and their key-word wrap constraints to an integer seed. The only additional requirement for an integer containing **exactly 613 seed words** is that the most significant key word `key[612]` is nonzero.

The nonlinear wrap equations never depend on the modeled withheld selected coupon or on the later unconstrained register words beyond these fixed early/late boundary words. They remain valid after imposing any independently consistent coupon.

## The whole selected coupon is a genuinely free linear image

The four 32-bit selected tempered outputs at stages 951..954 are 128 known linear functions of the register's 19,968 input bits. Insert each selected output's 32 untempered GF(2) equations into the original + n613-boundary rank15,718 system. **All 128 are independent**, so rank becomes **15,846**, with **no contradictory source equation for any choice of the 128 right-hand sides**. The augmented system consequently has `19,968 - 15,846 = 4,122` free state bits.

Crucially, after those full **128 coupon constraints**, the complete initialized state word S611 retains **31 independently controllable dimensions** in the augmented source-nullspace (verified using *full* basis projection, not a partial pivot stop). This dimension is the same for every prescribed coupon since changing its output bits changes only equation right-hand sides, not their linear coefficient vectors. The actual source constraints therefore still permit `2^31` distinct S611 32-bit values.

Under CPython's second initialization pass, the first-pass state at index612 is

```
a612 = (S612 + 612) XOR mix_B(S611)
```

where `mix_B(x)=((x XOR (x >> 30))*1566083941) mod 2^32`; the odd multiplier makes it invertible. The final original seed word is recovered by the first pass:

```
key612 = a613 - (BASE613 XOR mix_A(a612)) - 612  (mod 2^32)
```

where `a613` and `S612` are already fixed by the source-compatible boundary, and `mix_A` uses odd multiplier 1664525, also invertible. Hence the mapping **S611 → key612 is injective**. Of at least `2^31` source-compatible S611 values for *every chosen coupon*, at most one can yield `key612=0`. Therefore a complete source-consistent register exists whose backward-derived actual integer seed has exactly 613 words, for **every** 128-bit coupon.

Finally, the full actual seeded `random.Random(seed)` register and **every one of the 132 intact printer packets** are regenerated as checks on this algebra. No acceptance hash was used in the seed or coupon construction.

## Four reproducible positive source-history witnesses

The [single-file read-only SFT](../agents/agent14/k04_p951_cpython613_arbitrary_coupon_sft.py) prescribes four widely different missing coupons, solves actual CPython integer seeds, checks the complete original printer sources and verifies the exact chosen selected coupon:

| Entire coupon prescribed (hex) | Rank | Residual S611 dimension | Actual Python integer seed | Original intact packets |
|---|---:|---:|---|---|
| `00000000000000000000000000000000` | 15,846 | 31 | 613 words | 132/132 exact |
| `FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF` | 15,846 | 31 | 613 words | 132/132 exact |
| `A9A9DC5731A5E2AE879C47215C2559D5` (unverified selected copied ACK) | 15,846 | 31 | 613 words | 132/132 exact |
| `00000000000000000000000000000001` | 15,846 | 31 | 613 words | 132/132 exact |

These four are **synthetic producer histories consistent with all intact original input**. The disputed copied ACK still produces a **rejected** K04 component under the original mask and commitment, regardless of its consistency with the source-model generator. Genuine seeded reverse-initialization controls are included in the SFT. The full C++ n613 boundary search and all preceding source constraints are linked from the earlier report.

## Implication for next cracking work

- The complete 128-bit selected coupon is **non-identifiable from original intact printer packets even if this particular real CPython 613-word generator model were correct**, including its nonlinear seed initialization. Merely searching more long-seed originals in the same model cannot prove what the historical original coupon was.
- This theorem has precise, limited scope. A different actual generator architecture, an authenticated seed, a correctly indexed extra carrier intersecting the source-nullspace, or selected-media/copy boundary evidence could break the ambiguity.
- It does **not** imply 128 random bits are unconditionally missing from the broader archive, rule out structural source dependencies outside this generator family, or identify any real K04 acceptance-matching candidate.
- K08 is independently unresolved; no author-final exact normalized caption words appear in the preserved source. Original six verified component values, commitment inventory, verifier and candidate were untouched.

The specific future research priority is to identify an **external-to-printer source carrier with event-stage provenance** or a **physical copy-stage bridge** that actually reduces those 128 directions. Continue distinct K08 terminal-caption reconstruction or original-wording work without repeating giant K04 source-only generator fits.
