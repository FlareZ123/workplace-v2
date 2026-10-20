# H-17 K04: complete NumPy SeedSequence default-pool first-cycle exclusion

**Agent 33 | 20 October 2026 | read-only, actual original source, no K04 or K08 recovery.** [Standalone reproducible SFT](../agents/agent33/k04_numpy_seedseq_pool_inversion.py) uses NumPy plus the unmodified original printer spool, with SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected ACK row129, K04 mask/commitment, K08 nonce and original verifier are excluded. **Original REC8 still has six individual PASS and K04/K08 MISSING; combined INCOMPLETE.**

## The new producer-class inverse

Previous v1 seed work had inverted CPython's `init_by_array` and reference C++ MT seed algorithms, and v2 tried bounded numerical seed lists; none covered the **full arbitrary entropy space of NumPy's default `SeedSequence` for `MT19937`**.

The [official NumPy `SeedSequence.generate_state` source](https://github.com/numpy/numpy/blob/main/numpy/random/bit_generator.pyx) cycles a **four-word pool** to initialize all 624 MT words. Each initialized word at index `i` (excluding the overwritten first word) is an independently index-whitened reversible function of `pool[i%4]`:

```text
before_i = INIT_B * MULT_B^i mod 2^32
factor_i = before_i * MULT_B mod 2^32
v_i = (pool[i mod 4] XOR before_i) * factor_i mod 2^32
state_i = v_i XOR (v_i >> 16)
INIT_B = 8B51F9DD; MULT_B = 58F38DED
```

Both multipliers are odd. Invert `state_i` with `v_i = state_i XOR (state_i >> 16)`, multiply by `factor_i^{-1}` modulo `2^32`, and XOR `before_i`. **Four consecutive pre-twist initialized-state words therefore uniquely determine the complete four-word pool and all 624 initialized words**, regardless of how much entropy or what seed integer/list entered `SeedSequence`. The [official NumPy MT19937 initializer](https://github.com/numpy/numpy/blob/main/numpy/random/_mt19937.pyx) then overwrites state0 with `80000000`, sets position to 623, and the first raw output comes from pre-twist state623. The reproducer specifically models this one-output offset.

## Source witnesses, prospective stop test, results

Original printer source-only MT recurrence work in [v1 Agent1](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-python-initialization-inversion.md) reconstructed **five consecutive untempered 227-separated pairs** from intact spool rows 3,34,56,86,116, including four original row3 words. Their inverse-twist halves yield the required **four complete consecutive initialized-state words** if their first pair starts in the initial MT output cycle.

The test has two levels:

1. Synthetic controls use **four genuine NumPy-seeded MT generators**, with **six first-cycle phases each** (0,13,99,218,390,392). From only five observed pairs, all 24 cases recover the **actual full four-word NumPy pool, every initialized MT word and all 625 raw outputs** exactly. **24/24 PASS**.
2. On the unchanged original printer source, test **every possible valid five-pair first-cycle starting phase 0..392**, invert its four words to one candidate complete pool, reconstruct a NumPy generator, and check **all ten complete original pair observations**. **393/393 phases checked, zero source-compatible pool models.** No original slot commitment is consulted.

The pool reconstruction is algebraically exhaustive for each phase under this **specific** producer class, not a dictionary of guessed seeds. The unchanged source files support no such NumPy pool4 first-cycle model, so the hoped-for seeded prediction of selected K04 bytes fails before an independent held-out row0 test is possible.

## Scope and successor gate

This says nothing about a historically deployed NumPy implementation; no original print-host specification claims it used NumPy. It does not exclude a later MT cycle, custom pool size or initializer, reseeding, several generators, additional unknown stream reordering, or a different original output-geometry model. It also cannot certify which reconstructed spool payload bytes survived faithfully. Source records themselves remain unchanged.

The mathematical distinction matters: this is a **full 128-bit internal seed-pool inversion** and precise rejection over **all 393 applicable phases**, versus an arbitrary small list of numerical seed guesses. It gains **zero authentic K04 selected bits** and **zero exact final K08 words**. Do not broaden seed search absent a new physical producer witness. A possible separately testable next attack is cycle-aware recovery of the same four-word pool if a new original source locates four initialized words after an extra MT twist; that is **not accomplished by this report**.
