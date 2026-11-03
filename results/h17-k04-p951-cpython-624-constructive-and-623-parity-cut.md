# K04 p951: constructively realize every selected coupon with a 624-word CPython seed; exclude seed length 623 by a one-bit source certificate

**Agent 19, 3 November 2026.** Mathematical and executable **conditional producer-model** result, distinct from any historical recovery. The original selected 18:02 ACK/commitment is withheld from inference. Six accepted REC8 slots remain accepted; K04 and K08 are unresolved. **New authenticated K04 selected bits: zero.**

## Source/premises

Original `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The 133 printer payloads are interpreted under Agent45/39's *hypothetical p951 chronology*, 4 little-endian CPython `getrandbits(32)` draws per entry at their specified `STARTS`. Row129, the selected 18:02 attempt2 ACK, is removed **before payload decoding**. All **132 other original packets** contribute intact source observations. The historical printer maker, output ordering and physical-copy stage are **not authenticated**; an independently modeled CLASS sampler already conflicts at row84.

Following Agent39's corrected first-cycle indexed register, set initialized `S[0..623]` as the 19,968 GF(2) initial variables. Standard MT recurrence and output untempering give 15,365 independent constraints from 132 intact original printer packets. Add CPython's `S[0]=0x80000000`: rank15,397 and 4,571 free nuisance bits. Source consistency is exactly zero contradictions. These rank values reproduce the existing p951 source geometry, rather than rebranding it as a new source observation.

## New 624-word exact nonlinear seed inversion

CPython's `init_by_array` uses 624 first-loop injections for a 624-word integer key and a 623-iteration second diffusion loop. Invert that latter loop backward to pre-second `X` using `M₂=1566083941` and `mix(x,m) = m*(x xor (x>>30)) mod 2^32`:

```text
X[1] = (S[1]+1) xor mix(S[623], M₂)
X[i] = (S[i]+i) xor mix(S[i-1], M₂)    for i=623 down to 2
```

For any desired initialized register `S` with `S[0]=0x80000000`, fix arbitrary intermediate `Y[1]=0`. Recover all 624 first-loop injected 32-bit key words, with `M₁=1664525` and `BASE=init_genrand(19650218)`:

```text
key[0] = Y[1] - (BASE[1] xor mix(BASE[0], M₁))
key[1] = X[2] - (BASE[2] xor mix(Y[1], M₁)) - 1
key[i-1] = X[i] - (BASE[i] xor mix(X[i-1], M₁)) - (i-1)   for i=3..623
key[623] = X[1] - (Y[1] xor mix(X[623], M₁)) - 623
```

All arithmetic is modulo `2^32`. Form a CPython integer seed from these 624 little-endian words. If the highest key word vanishes, change the freely selected `Y[1]`; positive controls and original source constructions obtained valid nonzero last words. This is an *exact inverse*, not a seed heuristic. **5 actual seeded 624-word positive controls and 5 arbitrary target-state positives, 10/10 in total**, verified the *entire 624-word initialized register* with fresh `random.Random(seed).getstate()`.

Using the original 132 intact packets' affine source solution and this inverse, two different genuine 624-word seeded instances reproduce **132/132 original 16-byte payloads exactly**, yet predict selected-coupon bytes `BAB2B9A2B291F52D9058C9907E35E2F0` versus `B8A3B1E6B291F52D9058C9907E35E2F0` (six differing bits). The complete selected 128-bit output basis remains independent, rank gain128. Three more original-constrained complete-seed positive tests impose **all-zero, all-ones or repeated-AA 16-byte selected coupons**, each achieve **132/132** original intact packets and **128/128** prescribed selected bytes. Because every 128-bit target choice corresponds to a consistent register, and the above inverse maps every such register to an actual 624-word CPython seed, **all 2^128 coupon values are feasible within this explicit unverified seeded producer model**. This is a *constructive target nonidentifiability certificate*, not a recovered physical coupon.

## New 623-word necessary-bit exclusion

A 623-word seed still causes exactly 624 first-loop iterations, but its last key injection repeats `key[0]` with **cyclic j=0**, unlike the fresh `key[623]` with j=623 in the 624-word model. Let `A = BASE[1] xor mix(BASE[0], M₁)`, `B = mix(X[623],M₁)`. Equality of the first and last injected key word forces

```text
Y[1] + (Y[1] xor B) = X[1] + A (mod 2^32).
```

Taking bit0 eliminates the unknown `Y[1]` completely: `bit0(B) = bit0(X[1]+A)`. The source GF(2) closure already fixes just the necessary original initialized-register projections:

```text
S[1] & 1 = 1
S[622] = BBD5A4AB (all 32 bits fixed)
S[623] & 7FFFFFFF = 04710790 (31 low bits fixed)
```

Under both possible high bits of `S[623]`, evaluating the exact inverse-second-loop equation gives **`bit0(B)=0`**, while `bit0(X[1]+A)=1`. The one-bit contradiction excludes **every** 623-word `random.Random(large_integer)` source consistent with all intact printer packets **under the stated p951 first-cycle, little-endian four-draw chronology**. We verified the reverse relation on **10/10 genuinely generated 623-word CPython seed positive controls**; the conditional original contradiction is a mathematical source certificate, not a failed blind seed search.

This removes length623 from Agent39's 16 *necessary-condition survivors*, leaving 15 lengths `606,607,608,609,610,611,613,614,615,616,618,619,620,621,622`. The earlier 16-length list was not claimed sufficient, and the new exclusion does not imply any shorter survivor is feasible.

## Distinctness, next action and safety

Agent39's nonlinear+linear p951 screen restricted lengths to 1..623; it neither tested 624 nor gave a complete state-to-actual-key inverse. This result goes beyond the linear 128-bit nullspace by constructing actual `random.Random(integer_seed)` instances with full original source matches, and uses a new 623-word repeated-first-key parity check independent of prior near-complete word-domain exclusions.

Next useful attack: generalize repeated-key-index bit identities for each remaining length 606..622 against source-fixed register bits, seeking a new contradiction or a reproducible genuine short-seed solution; keep historical architecture and copy stage explicitly unproven. Do not use a 624-word posterior seed's arbitrary selected bytes as the true K04 coupon.

The original ZIP, route, verifier, acceptance and six-slot candidate were untouched; no equipment or protected account was accessed.

## 3 November 00:47 UTC addendum: length622 is also constructively nonidentifying

[New standalone source-pinned 622-word inversion SFT](../agents/agent19/k04_p951_cpython622_constructive_sft.py) extends the 624-word construction into the highest surviving shorter seed length. CPython's 624 first-loop injections with **622** seed words repeat `key[0]` as word622 and `key[1]` as word623, with cyclic j values **0** and **1**. Backward inversion of the second diffusion loop gives pre-second register `X`. For a chosen source-consistent late initial-state word `S[621]` and the two source-compatible `S[623]` MSB values:

```text
key0 = X[623] - (BASE[623] xor mix(X[622], M₁))
Y1   = key0 + A
C    = S[2] + 2
T    = (BASE[2] xor mix(Y1,M₁)) - (Y1 xor mix(X[623],M₁))
Q    = X[1]
(C xor mix(Q,M₂)) - Q = T                  (mod 2^32)
S[1] = (Q xor mix(S[623],M₂)) - 1
```

The new exact **32-bit low-bit-lifting inverse** of `(C xor mix(Q,M₂)) - Q = T` enumerates both high bits of `Q`, then adds low bits sequentially, using final full-word validation. **12/12** genuinely seeded synthetic 622-word CPython controls recovered their true `Q` among solutions. For the original printer source, each candidate `S[621]` is imposed on the original linear basis; the inverse supplies `S[1]`, which is independently checked against all source constraints before constructing the complete register and actual 622-word seed. This found a source-compatible candidate at deterministic trial18 (seeded RNG 20261103), and exact `random.Random(seed).getstate()` plus **132/132 original packet equality** passed.

The repeated-key constraints depend on early/late initial words `S[1], S[2], S[621], S[622], S[623]`. Keep them fixed and add arbitrary selected native output equations: the selected quotient still has full independent rank**128**. With the same source-constrained 622-word initializer, selected all-00, all-FF and all-AA 16-byte coupons each produce **132/132 original intact source matches and exactly the prescribed 128 selected bits**. This constructively establishes that **every 128-bit coupon remains possible under the equally unverified 622-word p951 seeded producer model**. No original K04 bit is recovered and the historical 18:02 copied fragment remains untrusted.

Unlike length623 (source-excluded by exact bit0 contradiction), length622 has at least one fully legitimate source-matching seed and its entire selected coupon quotient is unconstrained. This supersedes any suggestion that simply solving the length622 repeated-key equalities would determine K04. The 14 other shorter survivors remain necessary-condition hypotheses, not complete solutions.

## 3 November ~00:51 UTC addendum: length621 also source-feasible, selected 128-bit quotient untouched

A further independent [source-pinned 621-word CPython SFT](../agents/agent19/k04_p951_cpython621_constructive_sft.py) extends the constructive proof by introducing an exact **two-equation 32-bit joint bit-lifting inverse**, not an unrestricted random-seed sweep. For seed length621 the 624 initialization injections repeat key indices **0,1,2** on steps621–623. With pre-second words `X`, fix a tentative source-compatible `S[621]` and `S[623]`; the repeated key1 fixes an equation for two unknown intermediate words `Y1` (first injection state) and `Q=X1`, while repeated key2 adds a second independent 32-bit equation:

```text
C = S[2]+2
X2 = C xor mix(Q,M₂)
key1 = X2 - (BASE[2] xor mix(Y1,M₁)) - 1
key2 = X3 - (BASE[3] xor mix(X2,M₁)) - 2
last2 = Q - (Y1 xor mix(X[623],M₁)) - 2
require key1 = X[623]-(BASE[623] xor mix(X[622],M₁))-1
require key2 = last2
```

Guess the top two bits of each of `Y1,Q,X2` (64 top-bit assignments); lift their 30 lower bits together, checking **both** equations at every bit. Full 32-bit checks eliminate spurious prefixes. The genuine original value `(Y1,Q)` was recovered in **10/10 randomly seeded CPython 621-word synthetic controls**, each independently prepared from `random.Random(integer)`.

For any resulting `Y1,Q` source-compatible solution, invert mixed multipliers to obtain `S[1]` and `S[620]` from the repeated key0 constraint, then impose those complete words and the chosen `S[621],S[623]` on the original 132-packet GF(2) source basis. At deterministic trial7 (random seed20261103), a full source-feasible original register exists. The derived **actual CPython integer seed with precisely 621 32-bit words** recreates the entire register and **all 132 intact original printer packets exactly**.

Keeping the source-compatible near-end register words fixed, the selected word quartet remains 128 independent GF(2) dimensions. The same exact 621-word initializer produced separate genuine seeds targeting **all-zero, all-FF, all-AA 16-byte selected coupons**, each reproducing the 132 intact packets and the exact forced coupon. The full original K04 target remains **128/128 indeterminate** for this *unverified historical producer architecture*. This positive result advances the short-seed feasibility boundary from 622 to 621; the excluded n623, and 13 other shorter necessary survivors, are unchanged.

The result is conditional on p951 chronology/MT/LittleEndian CPython and says nothing about the real damaged physical ACK coupon, its mask provenance, or final keeper K08. In particular, it does not constitute a seventh accepted REC8 slot.

## 3 November ~00:55 UTC addendum: length620 exact seeded source match and arbitrary selected coupon

The third new [standalone source-pinned original SFT](../agents/agent19/k04_p951_cpython620_constructive_sft.py) extends the constructive initialized-register attack to **620 integer-seed words**. Four key indices 0,1,2,3 repeat at first-loop iterations 620..623, and the source-fixed original initial register words `S2=E32E1557,S3=3152E7CB,S4=BBDD46A0,S622=BBD5A4AB` isolate a **single 32-bit equation in intermediate first-loop word Y1** after using the final repeated key3 to express `Q=X1` as a function of `Y1`.

For each source-compatible `S621` and one of the two source-compatible `S623` MSBs, the last repeated key2 is known. Guess top two bits of `Y1,Q,X2` (64 cases), lift lower 30 bits of `Y1` while checking the exact modulo-32 equality of key2 on each prefix, then validate the full equations. **10/10** genuinely CPython-seeded synthetic 620-word controls recovered their planted Y/Q. Given the solved Y/Q, invert the odd multipliers (1664525,1566083941) and xor-shift to recover exactly the required pre-second `X621,X620` and initialized `S620,S619`; check those, S1 and chosen S621/S623 against the **original 132-packet** GF2 source basis.

This found a genuine source-compatible 620-word CPython integer seed at deterministic trial5. Both full `random.Random(seed).getstate()` and **132/132 original intact printer payload bytes** match exactly. Fix the near early/late coordinates implementing repeated keys and append all 128 selected native bit equations: rank gain **128**. New real 620-word seeds with deliberately prescribed selected coupons `00*16`, `FF*16`, `AA*16` again achieve all 132 original records exactly and all 128 selected bits as requested. The 620-word producer hypothesis is therefore demonstrably **source-feasible yet wholly nonidentifying** for K04. Original 623 remains source-excluded, and 619 and lower were not constructively assessed in this branch.

**Direction:** These cases establish that successively stronger repeated-key constraints need not recover any selected original bits, even with real CPython seeds. Avoid repeatedly cataloguing adjacent seed lengths as if their mere existence constitutes a coupon recovery. High-value next work requires an *independent authentic producer/seed-length/origin constraint* or at least one actual original selected coupon bit, and the verbatim final K08 inscription. Exact archival acceptance remains six PASS / K04,K08 MISSING.
