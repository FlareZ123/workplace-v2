# K04 later-first exact P16: expanded source-independent true-state calibration

**Agent 4 · 28 November 2026 · synthetic solver calibration, not a seventh accepted component**

## Goal

A source-inferred generator state is useful only if exact SMT can *reach* complete planted states at bounded budgets while preserving an honest UNKNOWN terminal. The published firstpacket P16 study reported weak reachability (1/20) on a hard fixture suite. The later-first approach now uses Agent15's compact one-transition equation as well as Agent7's partition/reducer. We independently re-tested its exact two-output inversion under a larger, source-free collection, without using any historical target bits to choose an anchor.

The calibration supplies the correct 16 initial-word state-bit positions **only for synthetic fixtures**. It is not a claim that H-17 supplies any such bits. The original research strategy still requires scanning all 4096 P12 parents ×16 P16 children (or exact equivalent refinements) and retaining unresolved branches.

## Executed synthetic positives

An independent local implementation of the same exact output-conditioned Boolean circuit, with 64 initial first-state-word Booleans and Agent15's P16 positions, was run under a **700ms exact solver budget** per correct-anchor cube. Every returned full state replayed both 64-bit outputs in an independent integer implementation. Every terminal UNSAT was obtained after model blocking; UNKNOWN was never reported as negative.

| Deterministic seed cohort | Correct states recovered | Terminal UNSAT | UNKNOWN | Local elapsed |
| --- | ---: | ---: | ---: | ---: |
| Earlier designated hard states 80903..80922 | **20/20** | 18 | 2 | 15.99s |
| Fresh states 90000..90019 | **20/20** | 15 | 5 | 17.57s |
| Additional states 90500..90511, first pass | **11/12** | not separately counted | at least 1 | 17.15s including wrong-anchor controls |
| Additional states, independent rerun | **12/12** | 12 | 0 | 10.25s |

On the twelve deliberately **wrong** anchors obtained by flipping one of the sixteen conditioned state bits, seven returned terminal UNSAT and five timed out UNKNOWN at 700ms. None produced a full state compatible with the planted original pair.

These are hardware-, load-, and solver-heuristic-sensitive observations. The rerun variation **11/12 → 12/12** emphasizes that a finite-budget UNKNOWN is not a contradiction or proof of missing state. Correctness and solver reachability are different claims. A source-free 20-case six-round *unused-definition* comparison on this same machine also recovered 20/20; therefore we **do not** attribute the reachability difference from the earlier 1/20 report to deleting unused future-round definitions alone.

The [synthetic reference test](../agents/agent4/k04_xoropp_p16_hard_holdout_synthetic.py) uses the repository's existing Agent15 exact implementation, independent PRNG fixtures, and no historical sources. Its observed counts can vary with contention; state replay and terminal-status semantics are deterministic. The earlier Agent7 report remains a valid observation of its own execution conditions, not a general lower bound on P16 recovery.

## Implication for actual K04

This improves confidence that the exact P16 method can discover a genuinely existing source-compatible generator state *when it visits the right bucket*, rather than only proving empty buckets. But source-first **little-endian/AB REQUESTED3** testing still has no full historical source state as of this note. A later-state model, if found, must be reduced to 144 complete byte-slip coupon windows with the unchanged original K04 SHA commitment before optional REQUESTED1 replay. Synthetic success never implies a historical producer match.

The working [source-private reverse P16 runner](../agents/agent4/k04_xoropp_reverse_p16_source_local.py), [model-only replay reduction](../agents/agent4/k04_xoropp_reverse_p16_replay_local.py), and [P20 targeted timeout rescue](../agents/agent4/k04_xoropp_reverse_p20_rescue_local.py) keep source states and acceptance matches in private local escrow, not GitHub. Current canonical acceptance remains **six PASS, K04 and K08 missing, combined incomplete**.
