# Agent22 follow-up: selected rows redundantly encode A LOW BIT

One stronger internal check appeared after my previous note. For the seven valid one-row lowerings of Emily's fixed eight-note set, decode each candidate note's **body word count** with A=0, then form:

- candidate head position 1
- count letters positions 2–4
- candidate head positions 6–8

Only N10 -> N11 gives **ALOWBIT**. The same row choice is also the unique one giving **ATEALBIT** in all eight body heads.

For N10 -> N11:
- heads: `ATEALBIT`
- count letters: `NLOWIF?V`
- mixed instruction: `A` + `LOW` + `BIT` = **`ALOWBIT`**

So the chain now has an internal target-blind redundancy: **A TEAL BIT** and **A LOW BIT** arise from the same unique lowering. The SFT/report have been updated in commits `73c38aaf` / `f47a6ead`.

This strengthens LOW-as-bit-significance, while the final M -> Mug shelf step still needs adversarial review.
