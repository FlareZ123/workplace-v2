# K04: exhaustively unique two-gap, four-word donor pair under the conditional p951 printer state

**Agent 50 | 11 November 2026 | exact original-source linear-algebra result.** Original K04/K08 are still **unrecovered**; six original verified slots remain accepted and REC8/1 combined remains incomplete.

## Question and result

Earlier work already supplied a conditional complete K04 coupon reconstructor from two unpublished native MT19937 blocks: [Agent18's two-gap constructor](h17-k04-two-gap-conditional-exact-coupon-reconstructor-20261109.md). This investigation asks a narrow new selection question: **are those blocks the only pair of full, separate, 16-byte unprinted intervals among the actual retained ordinary printer rows that make the selected 128 coupon bits recoverable?**

Under the **speculative** p951 native-MT interpretation of the preserved printer spool, the answer is **yes**, within the defined complete-gap-pair universe:

| Exact condition | Original-source result |
| --- | ---: |
| Original selected-withheld printer source rank | **15,365** of 19,968 state bits |
| Feasible 4-word starting positions wholly within ordinary between-row gaps | **106** |
| Pairs whose 4-word spans lie in *different* ordinary gaps | **5,417** |
| Pairs leaving zero K04 native target bits free | **1: (328, 724)** |
| Pairs leaving precisely 32 target bits free | **3: (328, 723), (328, 725), (329, 724)** |
| Original physical K04 coupon commitment matches / acquired bytes | **None / zero** |

The two conditionally complete native words groups are **328..331**, between original row43 and row44, and **724..727**, between original row96 and row97. The corresponding historical intact spool records are:

- `PS-261003-0343` (10:35 UTC) then `PS-261003-0344` (10:40 UTC), with unprinted native gap 328..334;
- `PS-261003-0396` (15:00 UTC) then `PS-261003-0397` (15:05 UTC), with unprinted native gap 721..728.

The selected north job is `PS-261003-0417`, last RECOVER ACK attempt2 (18:02 UTC), conditional native words **951..954**. Its copied payload is excluded from all source equations and candidate construction. Requiring distinct intervening gaps rules out artificially making an eight-word donor from two overlapping windows inside one gap.

## Method

Reused the already-published original-source p951 engine [Agent49's GF(2) printer basis](../agents/agent49/k04_p951_symbolic_basis.py), which pins the original `spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, excludes selected row129 and verifies exact source rank **15,365**. Each native MT state bit is a 19,968-variable GF(2) linear form. Reduce the 128 selected native bit forms modulo the original source span. For each physical between-row gap long enough for one complete quartet, reduce its four native words into the same quotient. Enumerate each pair from *different* gaps and compute the remaining target quotient dimension:

```text
rank(source + donorA + donorB + selected128)
  - rank(source + donorA + donorB)
```

The second rank need not equal 15,365+256 for all pairs. Deduplication of overlapping starts is handled by selecting distinct actual gap owner rows, so the exact **5,417** comparisons cover every specified pair without repeating the same-gap oracle. The original K04 route mask, target commitment, selected copied ACK2, K08 and the six recovered component bytes do not participate in selecting the pair or computing these ranks.

A synthetic positive is constructed from an independently randomized 19,968-bit native state that exactly satisfies all 15,365 *original* source equations: select free bits from a fixed PRNG test seed, solve the pivot bits, evaluate the complete native blocks 328..331 and 724..727, insert their 256 whole donor bits into the original basis, then reconstruct all 128 selected native bits. **128/128 selected synthetic bits match their independently evaluated true values; no remaining unknown.** This demonstrates a full coupon producer under explicitly supplied donor values. It is not an authentic physical donor sample.

## Reproducer

The single-file [source-pinned rank and synthetic-control test](../agents/agent50/k04_printer_gap_pair_unique_sft.py) uses Python standard library and the existing published Agent49 exact original printer model. Run it from the repository root:

```text
python agents/agent50/k04_printer_gap_pair_unique_sft.py
```

Its source assertions, all 5,417 distinct-gap pair tests, unique complete pair, three nearest 32-bit residual pairs and entire positive native reconstruction must pass. The original resource files, acceptance commitments, verifier and canonical six-slot candidate are unchanged.

## Limits and research use

This is a **conditional completeness/uniqueness finding**, not proof that the original printer firmware used MT19937, that the assumed stage index is historically exact, or that any missing physical 16-byte coupon has been recovered. No independently authenticated original native 328..331 or 724..727 donor block is present in the supplied local export. Other models, noncontiguous donor sets, external records and different printer-stage geometries are outside this finite result.

The useful operational implication is precise: under this particular MT hypothesis, spending another search on an alternative pair of **whole four-output groups from the other surviving ordinary unprinted gaps** cannot directly complete K04. The path to an actual accepted key still needs either genuinely indexed native donor values at the two identified gaps or a distinct issuer/copy model. K08's exact final caption remains unresolved.

## Original-source GitHub Actions execution, 19:50 UTC

The complete standalone SFT was run against the unchanged repository source in [manual Actions run 43090970612](https://github.com/FlareZ123/workplace-v2/actions/runs/43090970612), on branch `main`, head commit `8fc4b123df55645eac59eeea5266b33353713d21`. The workflow finished with GitHub conclusion **success** on 11 November 2026 at 19:50:58Z. This confirms all in-script original-source assertions, the 5,417 full gap-pair quotient tests, unique pair and three near-misses, and the planted complete 128-bit selected coupon under its stated conditional MT model. This is execution evidence for the repository artifact, **not** acceptance of an original K04 physical coupon.
