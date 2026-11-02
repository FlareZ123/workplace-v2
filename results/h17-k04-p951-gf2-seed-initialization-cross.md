# K04 p951: source GF(2) register constraints intersect CPython initialization, 71 -> 16

**Agent39, 2 November 2026 ~21:38 UTC. Exact source-only conditional falsifier.** Corrected recurrence and source-pinned SFT: [`agents/agent39/k04_p951_gf2_seed_cross_sft.py`](../agents/agent39/k04_p951_gf2_seed_cross_sft.py). **The original K04 selected 128-bit component is still wholly unresolved; original K08 final words remain unknown.**

## Core advance

Agent45's independent CPython first/third initialized-state inversions excluded lengths 1..363 and reduced 144 source residue survivors to 71 possible integer-seed-array lengths among 1..623. Agent39's [new central-word inverse](h17-k04-p951-cpython-middle-state-inverse-exclusions.md) then eliminated five further lengths with only the locally propagated full/31-bit original register masks, leaving 66.

A stronger joint constraint now recovers **2,730 additional *source-fixed bit observations*** of the initial 624-word CPython register relative to the earlier conservative propagation:
- Construct a full **19,968-variable** GF(2) symbolic transition from the initialized register `S[0..623]` to every observed printer word.
- Load only the **132 original intact printer packets**, withholding selected row129 before decoding its payload. The row-index vector is the unchanged *hypothetical* p951 sequence from Agent2/45.
- Eliminate all intact original native MT output equations: rank **15,365**, zero source contradictions. The register's source-independent bit mask fixes **9,736 individual bits** (Agent45's masked recurrence fixed 7,040). The CPython `init_by_array` invariant `S[0]=0x80000000` adds 32 independent equations and propagates two further individual fixed bits, giving **9,770 fixed register bits**, compared with the baseline 7,040.
- Those 9,770 bits expose **94 complete/one-bit source key terms** for `init_by_array` instead of the previously accessible 64.
- Intersect key terms `T[j]` by seed length residues, apply Agent45's exact first/third inverse and new GF(2) consistency, then Agent39's [exact middle-word bit-lift inverse](h17-k04-p951-cpython-middle-state-inverse-exclusions.md) with a second GF(2) pass and fixed-point iterations.

| Original-source necessary-condition screen | Conditional surviving integer key lengths 1..623 |
| --- | ---: |
| Agent45 previous complete/one-bit terms | 144 |
| Agent45 prior outer inverse + conservative MT propagation | 71 |
| **New full symbolic source bit extraction, 94 term domains** | **42** |
| **New outer inverse + full global GF(2) contradictions** | **17** |
| **New central initialized-register inverse** | **16** |

The final 16 lengths are **606,607,608,609,610,611,613,614,615,616,618,619,620,621,622,623**. The new central inverse specifically excludes the otherwise source-consistent `n=588` at `i=14`. The remaining lengths are *not* proven to produce any full-seed stream matching the original packets. The exact selected quotient remains **128 unknown native/printed bits under every one**; even whole-model nonlinear register bit deductions currently fix zero individual selected bit positions.

## Crucial model-origin correction and genuine positive tests

An early pilot used a symbolic MT state at index **-1100** and identified the arbitrary backward-derived 624-word block `[-624,-1]` with CPython's `init_by_array` initial register. This silently imposed an extra **pre-initialization history** on a seed-initialized state, which is generally invalid. A true CPython synthetic spool immediately falsified the mapping: it spuriously inferred nonzero `S[0]` low bits, inconsistent with CPython's required `0x80000000`. **That entire backwards-origin pilot was discarded, with no result promoted.**

The corrected model starts its 624-word algebraic state at the *actual initialized register*, native index `0..623`; the first CPython `getrandbits(32)` output corresponds to native index624, and spool position `p` to symbolic index `624+p`. This orientation reproduces real CPython twist semantics and honors the specially seeded register's lack of an arbitrary prehistory.

**18/18** independent genuine `random.Random(large_integer)` source-spool positive controls pass, comprising two seeds for each key-array length **1,32,249,364,588,606,611,618,623**. For each the actual source is generated, selected spool packet is withheld, and the GF(2) source basis and nonlinear inversions are recomputed without inspecting that selected packet. All inferred initial-state bits agree with the genuine seed-initialized Python register, every surviving source hypothesis remains feasible for its own synthetic data, and every inferred selected native output bit agrees with the hidden true output. At seed lengths 1 and 32 the procedure in fact identifies all 128 selected native bits in synthetic data (target quotient0), establishing a positive **target-reaching** capability for short seeds. For the authentic source, **all 16 survivors retain target quotient128**, so no historical selected candidate has been constructed.

## Source provenance, limits, and next attack

The SFT pins original `resources/evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; uses the first-cycle p951 assumed emission chronology, exact MT recurrence and untempering; never reads the selected row's value, K04 XOR mask/commitment, K08 nonce/commitment, candidate or verifier. It extends Agent45's SFT with an **independently originated 624-state GF(2) symbolic solver**, rather than borrowing the risky negative-index prehistory.

These exclusions are **conditional**: the original company never attests that the printer used CPython MT or that row start positions coincide with the p951 sequence. A previously assumed independent ordinary CLASS sampler conflicts at row84; source bookkeeping and actual physical copy/ACK provenance remain unvalidated. A complete recovery requires an evidenced historical producer or another source-to-selected-event mechanism. The current 16 long-seed survivors maintain all 128 target degrees under the source-derived linear and key-inverse constraints. Future work should investigate a justified stronger nonlinear high-bit/full-key-term cross-relation or a different producer, rather than blindly enumerate 16 seeds of ~20,000 bits.

**Verified authoritative archive remains:** K01/K02/K03/K05/K06/K07 individual PASS; K04/K08 MISSING; combined INCOMPLETE. The mathematical improvement does not establish an authenticated original K04 bit.
