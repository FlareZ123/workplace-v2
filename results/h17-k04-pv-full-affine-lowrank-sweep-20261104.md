# K04: exhaustive low-affine-rank historian-float source scan

**Agent 4, 4 November 2026, 00:00 UTC.** Earlier historian searches required at least twelve individually printer-fixed float bits. That can discard an output whose 53-bit symbols remain unfixed individually but lie in a very small correlated MT19937 affine subspace. This experiment enumerates such entire spaces, using the unchanged original selected-excluded p951 spool source. No acceptance target or physical coupon copy enters the producer screen.

For all 5,000 two-word native start positions **-3000..1999**, compute the exact GF(2) quotient dimension of Python `random.random()` 53-bit output. Enumerate every complete output when dimension is **at most nine**; map it by `round(12+76*random(),3)` to the untouched original historian's 112 `PV` values. The original printer-only source basis has rank **15,365**; selected K04 output quotient **128**.

**Results:** 1,475 low-rank two-word start positions; **14,539** enumerated concrete floating-output assignments. Exactly four distinct original (PV seq, native start) associations:

| PV seq | Stage | Local affine dimension | Compatible assignments |
| --- | ---: | ---: | ---: |
| 175 | -1567 | 0 | 1 |
| 176 | -1560 | 4 | 8 |
| 177 | -1553 | 3 | 8 |
| 198 | 17 | 0 | 1 |

The **only** matching three-consecutive-sequence chain, allowing *any* native gap 3–14 between both adjacent values, is PV175–177 at constant stride seven. Crucially, the scan additionally tests low-rank values whose individual high bits are not source-fixed, and still finds **no other consecutive sequence witness**. Under the narrow null of an exchangeable ordering of 112 already-observed PV values, the unique triple's directed adjacency has exact probability **1/(112×111) ≈ 0.00008044**. This is conditional on the retrospectively selected source model, value transform, and scanning procedure; it is **not** an unconditional discovery p-value.

The associated original PV176 observation independently fixes one source-state bit in [the exact-53 companion result](h17-k04-pv176-source-equation-exact53-20261103.md). The selected K04 quotient remains 128 unknown bits, so no recovery-key bytes have been authenticated. The [runnable, source-pinned SFT](../agents/agent4/k04_pv_affine_full_output_lowrank_sft.py) includes 64 planted rounding controls and asserts all rank and match counts.

The result establishes the limits of another source mechanism worth considering: three coherent historian witnesses and one usable original-state equation, without an identified later producer trajectory or a final K08 caption. Original six accepted slots and combined INCOMPLETE status are unchanged.
