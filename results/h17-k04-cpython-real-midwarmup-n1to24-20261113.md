# K04: genuine CPython startup-offset gap, n=1..24 source constraints and finite full-seed replay

**Agent 40 | 13 November 2026, 00:47 UTC | Eight GitHub Actions partitions complete.**

**Outcome:** The missing physical K04 coupon was **not** recovered. The scoped source model has many weakly constrained seed/phase pairs, but 476 fully specified short-seed producer replays all fail to reproduce the **132** undisputed complete original printer packets. Original K08 remains unquoted; REC8 still has six PASS, K04/K08 MISSING and combined INCOMPLETE.

## Distinct source-dependent model

The original ESC-N selected ACK2 at printer row129 is excluded before packet decoding; neither copied row129's 16 bytes, the original K04 SHA commitment, nor the route XOR mask is used for model fitting. The 132 intact historical spool packets are fit under **conditional** p951 native-MT19937 stage positions (source rank **15,365 / 19,968**). The model hypothesizes CPython `random.Random(integer_seed)` seeded with **1..24 actual 32-bit key words**, then emits a genuine prefix of `k` 32-bit outputs before the first ordinary spool record.

Previous checks covered genuine startup offsets `k=0..623`, three isolated mid-gap register boundaries (624, 1248, 1872), and a later segment at `k=2496..3119`. Here the full missing intermediate interval is tested **at every real output offset `k=624..2495`**, precisely 1,872 phases. Each offset reanchors the 624-word initial register and rebuilds the exact printer-source constraints, rather than cyclically rotating an established register or assuming no intervening twists.

At each phase:

1. Enforce the CPython initialized register's mandatory `S0=0x80000000` where source-constrained.
2. Derive every complete/one-bit-incomplete `init_by_array` inverse triplet `T_i` and enforce equal key-term residue classes modulo each seed length `n=1..24`.
3. For every surviving `n<=4` with all key words finitely determined, reconstruct every possible exact seed (subject to a 4,096-candidate limit) using genuine CPython and compare **all 132 original complete 16-byte source packets**. None reproduces the full stream. Longer or incompletely determined seeds remain only necessary-condition survivors.

The original 2026-10-03 spool source is SHA256-pinned to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Each of eight partitions verifies a synthetic 24-word genuinely seeded CPython **whole-stream** positive at its exact phase start, including reconstruction of source-derived initialized-register bits and its key-residue consistency.

## Original-source results

| Exact metric | Result |
| --- | ---: |
| Actual prior-output phases `624..2495` | **1,872 / 1,872 tested** |
| Seed lengths per phase `n=1..24` | **44,928 combinations** |
| Phase contradictions from mandatory initialized `S0` | **150** |
| Surviving phase × seed-length **necessary conditions** | **15,629** |
| Genuine CPython fully specified short-seed replays | **476** |
| Full 132-printer-packet original-source reproductions | **0** |
| Authentic selected coupon bytes independently recovered | **0 / 16** |
| Genuine 24-word seeded planted-control partitions | **8 / 8 PASS** |

Necessary-condition survivors by seed length n=1..24 respectively: 359, 529, 529, 529, 681, 613, 529, 613, 529, 693, 529, 613, 681, 600, 681, 905, 693, 760, 529, 747, 825, 529, 703, 1230.

**Important interpretation:** A surviving seed-length/phase pair is not a recovered seed and may leave many 32-bit key words unconstrained. For example, at genuine phase 768 and n18, only 14 of 18 key residues are constrained by eligible source-derived triplets; the other four remain completely free at this sieve level. Phase 1164 and n24 constrain just 9 of 24 seed residues. At phase 1959/n2 the two candidate seeds are finite and both fail the full preserved printer stream. At phase 2130/n1 the sole finite seed also fails. Phase 2350/n1 has no eligible source-derived key term, hence its necessary survival conveys **zero evidence** of a true producer.

There is **no original K04 commitment hit**, because no complete original-source-consistent seeded producer emerged. A finite full-source replay success would have supplied a candidate original 16-byte selected coupon under this model, but no such seed was recovered. Other seed sizes, origins and historical generators are not excluded. Neither the p951 stage mapping nor CPython is historically established.

## Reproduction

- [Phase/seed enumerator](../agents/agent40/k04_cpython_midwarmup_n1to24_sft.py)
- [Independent key-residue diagnostics](../agents/agent40/k04_midwarmup_residue_diagnostics_sft.py)
- [Eight-shard completed workflow](https://github.com/FlareZ123/workplace-v2/actions/runs/43338946531)
- [Completed diagnostics workflow](https://github.com/FlareZ123/workplace-v2/actions/runs/43339569384)
- [Manual workflow definition](../.github/workflows/agent40-k04-cpython-midwarmup.yml)

Both scripts import the prior genuine-CPython initialized-state and original-source symbolic-MT helpers and keep the selected ACK2 bytes omitted. Each partition writes a JSON file containing every surviving necessary phase/n pair and exact full-seed-replay outcomes, uploaded as an immutable workflow artifact. No source file, original commitment, canonical candidate or official verifier was modified.

**Research decision:** This exactly fills the prior genuine-startup phase coverage gap. The apparent high count of survivors is mainly due to insufficient term observations at later origin offsets. Further independent model improvements should constrain additional seed words through a genuinely new source relation or use a different complete-event issuer. Do not repeat this startup window or misinterpret necessary survivors as selected physical-coupon information.
