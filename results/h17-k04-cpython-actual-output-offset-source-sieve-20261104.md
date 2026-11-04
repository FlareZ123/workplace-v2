# K04: actual CPython generator startup offsets, first-cycle source exclusion

**Agent28 | 4 November 2026 | Complete original-source model test; no recovery key.**

## Hypothesis and exact method

The previously established, **unverified** p951 printer MT19937 chronology aligns 132 undisputed surviving printer packets to 15,365 independent GF(2) equations; original selected row129 is excluded *before decoding*. The new question is whether the printer first generated **k previous 32-bit outputs**, k=0..623, after seeding a standard CPython integer Random with **n arbitrary 32-bit seed words**, n=1..623.

This is physically distinct from [our earlier cyclic-register study](h17-k04-cpython-initarray-rotated-register-source-sieve-20261104.md). A hypothetical actual startup offset invokes the MT twist. Rather than rotating a 624-word register, this experiment **reanchors a fresh set of 624 unconstrained initialized-register variables for each k**, rebuilds every symbolic MT output equation, and then projects original printer constraints onto its genuine pre-twist initialized words. This prevents artificial backward-through-initialization restrictions.

For each offset, apply the mandatory CPython initialized state S[0]=80000000. For all source-determined S[i−2],S[i−1],S[i] triples with 31 or 32 fixed bits in each word, exactly enumerate at most one unknown bit per word. Use the standard CPython init_by_array inverse:

```text
F_c(x) = c*(x XOR(x>>30)) modulo 2^32
P = ((S[i-1]+i-1) modulo 2^32) XOR F_1566083941(S[i-2])
Q = ((S[i]+i) modulo 2^32) XOR F_1566083941(S[i-1])
T[i-1] = (Q - (G[i] XOR F_1664525(P))) modulo 2^32
       = key[(i-1) mod n] + ((i-1) mod n) modulo 2^32
```

G is the standard reference register seeded with 19650218. A length n is impossible if two source-derived T domains with equal modulo-n residue have no common possible value. Allowing independent completions makes these **conservative necessary conditions**.

The code does not consult the original K04 selected copied ACK contents, original K04/K08 commitments, route mask, candidate or verifier. It SHA256-pins the untouched original 132-packet source in `resources/evidence/print/spool-reconstruction.log`.

## Exhaustive original results

| Source-only metric | Result |
| --- | ---: |
| Output startup offsets | **624** (k=0..623) |
| Unknown integer seed-array lengths | **623** (n=1..623) |
| Exact phase × length combinations examined | **388,752** |
| Original printer source rank at each offset | **15,365** |
| Offsets contradicting CPython initial S0 | **116** |
| Offsets passing S0 necessary condition | **508** |
| 31/32-bit source-derived inverse triples per eligible offset | **28..98** |
| Integer key lengths with **zero** eligible offsets | **250** |
| Contiguous excluded length prefix | **n=1..88** |
| First eligible length | **n=89**, across **11 offsets** |
| Surviving necessary phase × length assignments | **74,414** |

The 11 surviving n89 offsets are 612..619 and 621..623. Arrays n128 and n256 also fail at all 624 offsets. Other longer lengths survive, so this is **not** a monotonic universal key-length cutoff.

## Actual generator calibration

**72 genuine seeded CPython original-history controls PASS**. Nine seed lengths n=1,2,4,8,16,64,128,365,623 and eight authentic prior-output offsets k=0,1,2,3,17,73,301,623 each generated a complete native initialized register and all historical-observation-equivalent output packets. The test withheld each synthetic selected packet, solved its source-only symbolic basis, verified every inferred initialized register bit against the actual generator state and checked its true source-derived key-residue consistency. The initial S0 constant passed all 72. This explicitly catches invalid equivalence between cyclic initial-register rotation and real output offset.

Reproducible [single-file source-pinned SFT](../agents/agent28/k04_cpython_real_output_offset_sft.py) requires only Python standard library plus pre-existing Ag39 native MT and Ag28 inverse key-term code. The original spool source SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

## Boundaries

This excludes concrete **short integer-seeded CPython first-cycle printer models**, given the assumed p951 historical output indexing and observed copied-source data. It does not identify the printer implementation or a physical print/copy mechanism. Warmups of k>=624, different stage chronologies, larger seed-array values, nonstandard PRNGs and evidence missing from the trimmed export remain open. Surviving n/offsets are necessary source fits, not recovered historical seeds. In particular, the result supplies **zero independently authenticated K04 coupon bits** or exact author-final K08 words.

Official REC8 remains K01/K02/K03/K05/K06/K07 individual PASS; **K04 and K08 unresolved; combined INCOMPLETE, accepted=false**. Target-reaching evidence would be a genuine independently indexed future printer state/coupon or original final Emily desk-caption text.
